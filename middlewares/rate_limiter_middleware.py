# security/in_memory_rate_limiter.py
import time
from typing import Dict, Tuple, Optional
from dataclasses import dataclass, field
import threading
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from settings import CONFIG,Rule
import logging

logger = logging.getLogger(__name__)

@dataclass
class TokenBucket:
    """Token Bucket algorithm implementation in memory."""
    capacity: float
    refill_rate: float
    tokens: float = field(default=1.0)
    last_refill: float = field(default_factory=time.time)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def consume(self, tokens: float = 1.0) -> bool:
        '''
        Docstring for consume
        
        :type tokens: float
        :return: return True if the token was consumed
        :rtype: bool
        '''
        with self._lock:
            current_time = time.time()
            time_passed = current_time - self.last_refill
            logger.info(self.refill_rate)
            self.tokens = min(
                self.capacity,
                self.tokens + (time_passed * self.refill_rate)
            )
            self.last_refill = current_time
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    def get_retry_after(self) -> float:
        '''
        Docstring for get_retry_after
        
        :return: the time after the request can be done
        :rtype: float
        '''
        with self._lock:
            if self.refill_rate <= 0:
                return 3600
            
            tokens_needed = 1 - self.tokens
            if tokens_needed <= 0:
                return 0
            
            return tokens_needed / self.refill_rate


class InMemoryRateLimiter:
    
    def __init__(self):
        self.buckets: Dict[str, TokenBucket] = {}
        self.rules: Dict[str, Rule] = {}
        self._lock = threading.RLock()
        self._cleanup_interval = CONFIG.cleanup_interval
        self._last_cleanup = time.time()
        
        # Definir reglas por endpoint
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        self.rules = CONFIG.rules
    
    def _get_bucket_key(self, request: Request) -> str:
        '''
        Docstring for _get_bucket_key
        
        :type request: Request
        :rtype: str
        '''
        client_ip = request.client.host if request.client else "unknown"
        endpoint = request.url.path
        
        rule_found = False
        rule_type = "global"
        for key,paths in CONFIG.endpoints.items():
            for path in paths:
                if path in endpoint:
                    rule_type = key
                    rule_found = True
                    break
            if rule_found:
                break
        
        return f"{rule_type}:{client_ip}:{endpoint}"
    
    def _get_rule(self, bucket_key: str) -> Rule:
        """Obtiene la regla aplicable para una clave de bucket."""
        rule_type = bucket_key.split(":")[0]
        return self.rules.get(rule_type, self.rules["global"])
    
    def _cleanup_old_buckets(self):
        """Limpia buckets antiguos para evitar memory leaks."""
        with self._lock:
            current_time = time.time()
            if current_time - self._last_cleanup < self._cleanup_interval:
                return
            
            keys_to_delete = []
            for key, bucket in self.buckets.items():
                # Si el bucket ha estado inactivo por 1 hora, eliminarlo
                if current_time - bucket.last_refill > 3600:
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                del self.buckets[key]
            
            self._last_cleanup = current_time
            logger.debug(f"Cleaned up {len(keys_to_delete)} old buckets")
    
    def is_allowed(self, request: Request, cost: float = 1.0) -> Tuple[bool, float]:
        """
        Verifica si una request está permitida.
        Retorna: (allowed, retry_after_seconds)
        """
        # Ejecutar limpieza periódica
        self._cleanup_old_buckets()
        
        bucket_key = self._get_bucket_key(request)
        rule = self._get_rule(bucket_key)
        
        with self._lock:
            # Obtener o crear el bucket
            if bucket_key not in self.buckets:
                self.buckets[bucket_key] = TokenBucket(
                    capacity=rule.capacity,
                    refill_rate=rule.rate
                )
            
            bucket = self.buckets[bucket_key]
            
            # Verificar rate limit
            if bucket.consume(cost):
                return True, 0
            else:
                return False, bucket.get_retry_after()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware de FastAPI para rate limiting en memoria."""
    
    def __init__(self, app, rate_limiter: Optional[InMemoryRateLimiter] = None):
        super().__init__(app)
        self.limiter = rate_limiter or InMemoryRateLimiter()
        
        # Costos por operación (ajustables según complejidad)
        self.operation_costs = CONFIG.operations_costs
    
    async def dispatch(self, request: Request, call_next):
        cost = self.operation_costs.get(request.method, 1.0)
        
        for key,factor in CONFIG.operations_costs_factors.items():
            if key in request.url.path:
                cost *= factor
        
        allowed, retry_after = self.limiter.is_allowed(request, cost)
        
        if not allowed:
            logger.warning(
                f"Rate limit exceeded for {request.client.host} " # type: ignore
                f"on {request.url.path}"
            )
            
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "retry_after": retry_after,
                    "message": f"Please try again in {retry_after:.1f} seconds"
                },
                headers={
                    "Retry-After": str(int(retry_after)),
                    "X-RateLimit-Reset": str(int(time.time() + retry_after))
                }
            )
        
        response = await call_next(request)
        response.headers["X-RateLimit-Policy"] = f"{cost} token(s)"
        
        return response