from .upload_download import BackBlazeB2Service
from .circuit_breaker import AsyncCircuitBreaker,CircuitBreakerConfig,CircuitState,circuit_breaker,circuit_breaker_context

def get_backblazeb2_service():
    service = BackBlazeB2Service()
    try:
        yield service
    finally:
        service = None