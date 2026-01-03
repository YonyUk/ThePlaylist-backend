from contextlib import asynccontextmanager
from enum import IntEnum
from functools import wraps
import time
from typing import Any, Callable, List
from dataclasses import dataclass
import asyncio
from fastapi import HTTPException,status
import logging

logger = logging.getLogger(__name__)

class CircuitState(IntEnum):
    '''
    Docstring for CircuitState

    States of a circuit
    '''
    CLOSED = 0
    OPEN = 1
    HALF_OPEN = 2

class CircuitMetrics:

    _failures = 0
    _success = 0
    _slow_calls = 0
    _total_requests = 0
    _circuit_opens = 0
    _last_failures_times: List[float] = []
    _latency_history:List[float] = []

    def __init__(self,min_failure_pool_size:int,window_seconds:int=60):
        '''
        Docstring for __init__
        
        :type min_failure_pool_size: int
        :type default_wait_time: float
        :param window_seconds: window time for recent metrics
        :type window_seconds: int
        '''
        self._min_failure_pool_size = min_failure_pool_size
        self._window_seconds = window_seconds

    @property
    def failure_rate(self) -> float:
        if self._total_requests == 0:
            return 0.0
        return self._failures / self._total_requests
    
    @property
    def success_rate(self) -> float:
        if self._total_requests == 0:
            return 0.0
        return self._success / self._total_requests
    
    @property
    def recent_failures_count(self) -> int:
        now = time.time()
        return len([
            t for t in self._last_failures_times if now - t  < self._window_seconds
        ])

    @property
    def failures(self) -> int:
        return self._failures
    
    @property
    def success(self) -> int:
        return self._success
    
    @property
    def slow_calls(self) -> int:
        return self._slow_calls
    
    def record_success_request(self,latency:float) -> None:
        self._total_requests += 1
        self._success += 1
        self._latency_history.append(latency)
    
    def record_failure(self,latency:float) -> None:
        self._total_requests += 1
        self._failures += 1
        self._latency_history.append(latency)

    def record_slow_call(self) -> None:
        self._slow_calls += 1
    

    
    def add_fail(self,value:float) -> None:
        self._last_failures_times.append(value)
    
    def clear(self) -> None:
        self._success = 0
        self._failures = 0
        self._slow_calls = 0
        self._total_requests = 0
        self._last_failures_times = self._last_failures_times[len(self._last_failures_times) - self._min_failure_pool_size:]
        self._latency_history.clear()
    
@dataclass
class CircuitBreakerConfig:
    '''
    Docstring for CircuitBreakerConfig
    
    onfig class for circuit breaker architecture
    '''

    failure_threshold:int = 5
    failure_window_seconds:int = 60

    reset_timeout_seconds:int = 60
    max_reset_timeout_seconds:int = 300
    slow_call_threshold_seconds:float = 5.0
    call_timeout_seconds:float | None = None

    half_open_max_attemps:int = 2
    half_open_success_threshold:int = 2

    metrics_history_size:int = 1000

    ignored_exceptions: tuple = ()

class CircuitBreakerException(Exception):
    '''
    Docstring for CircuitBreakerException

    inner exception of a circuit breaker
    '''
    pass

class OpenCircuitBreakerException(CircuitBreakerException):

    def __init__(self,circuit_name:str,retry_after:float | None = None):
        self._circuit_name = circuit_name
        self._retry_after = retry_after
        message = f'Circuit "{circuit_name}" is OPEN'
        if retry_after:
            message += f', retry after {retry_after:.1f}s'
        super().__init__(message)

class AsyncCircuitBreaker:

    def __init__(
        self,
        name:str,
        config:CircuitBreakerConfig | None = None
    ):
        '''
        :type name: str
        :type config: CircuitBreakerConfig
        '''
        self._name = name
        self._config = config or CircuitBreakerConfig()
        self._state = CircuitState.CLOSED
        self._last_state_change = time.time()
        self._half_open_attemps = 0
        self._half_open_successes = 0
        self._metrics = CircuitMetrics(30,self._config.failure_window_seconds)
        self._lock = asyncio.Lock()

    @property
    def state(self) -> CircuitState:
        return self._state
    
    @property
    def metrics(self) -> CircuitMetrics:
        return self._metrics
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def is_closed(self) -> bool:
        return self._state == CircuitState.CLOSED
    
    @property
    def is_open(self) -> bool:
        return self._state == CircuitState.OPEN
    
    @property
    def is_half_open(self) -> bool:
        return self._state == CircuitState.HALF_OPEN
    
    async def execute(
        self,
        func:Callable[...,Any],
        *args,
        **kwargs
    ) -> Any:
        
        async with self._lock:
            if self._state == CircuitState.OPEN:
                retry_after = self._get_retry_after()
                if retry_after > 0:
                    raise OpenCircuitBreakerException(self._name,retry_after)
                self._transition_to(CircuitState.OPEN)
            elif self._state == CircuitState.HALF_OPEN:
                if self._half_open_attemps >= self._config.half_open_max_attemps:
                    self._transition_to(CircuitState.OPEN)
                    retry_after = self._get_retry_after()
                    raise OpenCircuitBreakerException(self._name,retry_after)
            
            start_time = time.time()
            try:
                if self._config.call_timeout_seconds:
                    result = await asyncio.wait_for(
                        func(*args,**kwargs),
                        timeout=self._config.call_timeout_seconds
                    )
                else:
                    result = await func(*args,**kwargs)

                await self._on_success(start_time)
                return result
            except asyncio.TimeoutError:
                await self._on_fail(start_time,'timout')
                raise
            except self._config.ignored_exceptions:
                duration_time = time.time() - start_time
                if duration_time >= self._config.slow_call_threshold_seconds:
                    self._metrics.record_slow_call()
                raise
            except Exception as e:
                await self._on_fail(start_time,str(e))
                raise
    
    async def _on_success(self,start_time:float) -> None:
        duration = time.time() - start_time
        self._metrics.record_success_request(duration)
        if duration >= self._config.slow_call_threshold_seconds:
            self._metrics.record_slow_call()
        if self._state == CircuitState.HALF_OPEN:
            self._half_open_attemps += 1
            self._half_open_successes += 1
            if self._half_open_attemps >= self._config.half_open_success_threshold:
                self._transition_to(CircuitState.CLOSED)
                logger.info(f'Circuit "{self._name}" CLOSED after successfully recovered')
        elif self._state == CircuitState.CLOSED:
            recent_failures = self._metrics.recent_failures_count
            if recent_failures == 0:
                cutoff = time.time() - (self._config.failure_window_seconds * 2)
                self._metrics._last_failures_times = [
                    t for t in self._metrics._last_failures_times 
                    if t > cutoff
                ]
    
    async def _on_fail(self,start_time:float,error_type:str) -> None:
        duration = time.time() - start_time
        self._metrics.record_failure(duration)
        recent_failures = self._metrics.recent_failures_count
        if self._state == CircuitState.HALF_OPEN:
            self._transition_to(CircuitState.OPEN)
            self._half_open_attemps += 1
            logger.warning(f'Circuit "{self._name}" re-OPENED after failure  in HALF_OPEN state')
        elif self._state == CircuitState.CLOSED:
            if recent_failures >= self._config.failure_threshold:
                self._transition_to(CircuitState.OPEN)
                logger.error(f'Circuit {self._name} OPENED after {recent_failures} failures in {self._config.failure_window_seconds}s')
    
    def _transition_to(self,new_state:CircuitState) -> None:
        old_state = self._state
        if old_state == new_state:
            return
        self._state = new_state
        self._last_state_change = time.time()

        if new_state != CircuitState.HALF_OPEN:
            self._half_open_attemps = 0
            self._half_open_successes = 0
        
        if new_state == CircuitState.OPEN:
            logger.debug(f'CIrcuit {self._name} transition: {old_state.name} -> {new_state.name}')
    
    def _get_retry_after(self) -> float:
        if self._state != CircuitState.OPEN:
            return 0.0
        time_in_open = time.time() - self._last_state_change

        recent_failures = self._metrics.recent_failures_count
        base_timeout = self._config.reset_timeout_seconds
        calculated_timeout = base_timeout * 2 ** min(recent_failures,5)
        final_timout = min(calculated_timeout,self._config.max_reset_timeout_seconds)
        final_remaining = max(0.0,final_timout - time_in_open)
        return final_remaining

def circuit_breaker(
    name:str,
    config:CircuitBreakerConfig | None = None
):
    def decorator(func):
        cb = AsyncCircuitBreaker(name,config)

        @wraps(func)
        async def wrapper(*args,**kwargs):
            return await cb.execute(func,*args,**kwargs)
        
        wrapper.circuit_breaker = cb # type: ignore
        return wrapper
    
    return decorator

@asynccontextmanager
async def circuit_breaker_context(name:str,config:CircuitBreakerConfig | None = None):
    cb = AsyncCircuitBreaker(name,config)
    try:
        yield cb
    finally:
        pass