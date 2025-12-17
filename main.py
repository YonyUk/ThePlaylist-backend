from fastapi import FastAPI,status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
import logging

from api.v1.user import router as UserRouter
from settings import ENVIRONMENT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title='ThePLaylist API',
    description='API for ThePlaylist social network',
    version=ENVIRONMENT.API_VERSION,
    docs_url=None,
    redoc_url=None
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ENVIRONMENT.ALLOWED_ORIGINS,
    allow_credentials=ENVIRONMENT.ALLOWED_CREDENTIALS,
    allow_methods=ENVIRONMENT.ALLOWED_METHODS,
    allow_headers=ENVIRONMENT.ALLOWED_HEADERS
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

@app.get('/docs',include_in_schema=False)
async def swagger_ui_html_with_cookie_support():
    return get_swagger_ui_html(
        openapi_url=str(app.openapi_url),
        title=app.title + ' - Swagger - UI',
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        swagger_ui_parameters={
            "tryItOutEnabled": True,
            "displayRequestDuration": True,
            "persistAuthorization": True,
            "withCredentials": True,
        }
    )

def openapi_with_cookie_support():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title='ThePlaylist',
        version=ENVIRONMENT.API_VERSION,
        description='API for ThePlaylist social network',
        routes=app.routes
    )

    openapi_schema["components"]["securitySchemes"] = {
        "cookieAuth": {
            "type": "apiKey",
            "in": "cookie",
            "name": "access_token",
            "description": "Cookie de autenticación httpOnly"
        }
    }

    openapi_schema["security"] = [{"cookieAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = openapi_with_cookie_support