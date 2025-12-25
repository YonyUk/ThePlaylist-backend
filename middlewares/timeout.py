import asyncio
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_504_GATEWAY_TIMEOUT

class TimeoutMiddleware(BaseHTTPMiddleware):
    
    def __init__(self, app, timeout_seconds: int = 30):
        super().__init__(app)
        self.timeout = timeout_seconds

    async def dispatch(self, request: Request, call_next):
        try:
            return await asyncio.wait_for(call_next(request), timeout=self.timeout)
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=HTTP_504_GATEWAY_TIMEOUT,
                detail=f"Request timed out after {self.timeout} seconds"
            )