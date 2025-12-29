from enum import IntEnum
import time
from fastapi import HTTPException,status

class CircuitState(IntEnum):
    '''
    Docstring for CircuitState

    States of a circuit
    '''
    CLOSED = 0
    OPEN = 1
    HALF_OPEN = 2

class AsyncCircuitBreaker:
    
    def __init__(self,reset_time:int,failure_threshold:int) -> None:
        self._circuit_state = CircuitState.CLOSED
        self._reset_time = reset_time
        self._failure_threshold = failure_threshold
        self._failed_at:float | None = None
    
    async def execute(self,func):
        '''
        Docstring for _execute
        
        try to execute func in circuit breaker architecture

        :type func: async function
        '''
        try:
            if self._circuit_state == CircuitState.CLOSED:
                return await func()
            elif self._circuit_state == CircuitState.OPEN and time.time() - self._failed_at > self._reset_time: # type: ignore
                self._circuit_state = CircuitState.CLOSED
                return await func()
            else:
                raise HTTPException(
                    status_code=status.HTTP_424_FAILED_DEPENDENCY,
                    detail='Dependency fallen'
                )
        except Exception as e:
            self._circuit_state = CircuitState.OPEN
            self._failed_at = time.time()
            raise e