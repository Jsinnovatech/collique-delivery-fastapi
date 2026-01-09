from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import init_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print("Starting up Collique Delivery API...")
    # Skip database table creation as tables already exist
    print("Using existing database tables...")

    yield

    # Shutdown
    print("Shutting down...")
    await close_db()
    print("Database connections closed")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "success": True,
        "message": "Collique Delivery API",
        "version": settings.VERSION,
        "endpoints": {
            "auth": f"{settings.API_V1_STR}/auth",
            "stores": f"{settings.API_V1_STR}/stores",
            "products": f"{settings.API_V1_STR}/products",
            "orders": f"{settings.API_V1_STR}/orders",
            "users": f"{settings.API_V1_STR}/users",
        },
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "success": True,
        "status": "OK",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }


# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)