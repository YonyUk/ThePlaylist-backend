import asyncio
import logging
from typing import Callable,Any
from fastapi import HTTPException,status
from functools import wraps

logger = logging.getLogger(__name__)

def timeout(seconds:int):
    '''
    Docstring for timeout

    :type seconds: int
    '''

    def decorator(func:Callable[...,Any]) -> Callable[...,Any]:

        @wraps(func)
        async def wrapper(*args,**kwargs) -> Any:
            try:
                return await asyncio.wait_for(
                    func(*args,**kwargs),
                    timeout=seconds
                )
            except asyncio.TimeoutError:
                logger.warning(f'Timout in {func.__name__} after {seconds}s')
                raise HTTPException(
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                    detail=f'Time limit exceded'
                )
        
        wrapper.timeout_seconds = seconds # type: ignore
        return wrapper
    
    return decorator