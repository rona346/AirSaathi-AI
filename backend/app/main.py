from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.v1.api import api_router
from backend.app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize cloud persistence and telemetry providers safely on service boot."""
    from backend.app.core.firebase import initialize_firebase
    initialize_firebase()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    version=settings.VERSION,
    description="AirSaathi AI: GenAI-powered Urban Air Quality Assistant API",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "active",
        "docs_url": "/docs",
        "api_v1": settings.API_V1_STR,
    }
