from fastapi import FastAPI,status
from fastapi.responses import JSONResponse
import logging
import os

from api.v1.user import router as UserRouter
from settings import ENVIRONMENT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title='ThePLaylist API',
    description='API for ThePlaylist social network',
    version=ENVIRONMENT.API_VERSION
)

app.include_router(UserRouter,prefix=ENVIRONMENT.GLOBAL_API_PREFIX)

@app.exception_handler(404)
async def not_found(request,exc):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={'msg':'Resource not found'}
    )

@app.exception_handler(500)
async def internal_server_error(request,exc):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={'message':'An unexpected error has ocurred'}
    )