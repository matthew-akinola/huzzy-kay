from api.router import api_router
from fastapi import FastAPI
from fastapi.responses import UJSONResponse
from fastapi.middleware.cors import CORSMiddleware
from core.settings import settings
from elasticapm.contrib.starlette import make_apm_client, ElasticAPM

apm_config = {
    "SERVICE_NAME": "Starfinder",
    "SERVER_URL": "localhost:8200",
    "ENVIRONMENT": "production",
    "GLOBAL_LABELS": "platform=Remote-server, application=backend-api",
}

apm = None

if settings.ENV == "production":
    apm = make_apm_client(apm_config)

origins = ["*"]


def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    app = FastAPI(
        title="VIP Service API",
        description="Backend to VIP Service Project by Team Axe",
        version="1.0",
        docs_url="/api/docs/",
        redoc_url="/api/redoc/",
        openapi_url="/api/openapi.json",
        default_response_class=UJSONResponse,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router=api_router, prefix="/api")

    if settings.ENV == "production":
        app.add_middleware(ElasticAPM, client=apm)

    return app
