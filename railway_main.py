#!/usr/bin/env python3
"""
Railway-optimized main application for Collique Delivery API.
This version starts faster and doesn't require database connection on startup.
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Use demo endpoints for Railway deployment
from demo_main import (
    root, health_check, register_client, login_client,
    register_store, login_store, login_admin, get_stores, get_demo_data
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lightweight lifespan for Railway deployment."""
    print("Starting Collique Delivery API on Railway...")
    yield
    print("Shutting down...")

# Create FastAPI app optimized for Railway
app = FastAPI(
    title="Collique Delivery API",
    version="1.0.0",
    description="Delivery platform API optimized for Railway deployment",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS for Railway
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all endpoints from demo
app.get("/")(root)
app.get("/health")(health_check)
app.post("/api/v1/auth/client/register")(register_client)
app.post("/api/v1/auth/client/login")(login_client)
app.post("/api/v1/auth/store/register")(register_store)
app.post("/api/v1/auth/store/login")(login_store)
app.post("/api/v1/auth/admin/login")(login_admin)
app.get("/api/v1/stores/")(get_stores)
app.get("/demo/data")(get_demo_data)

@app.get("/railway/status")
async def railway_status():
    """Railway-specific status endpoint."""
    return {
        "success": True,
        "status": "Railway deployment active",
        "service": "Collique Delivery API",
        "version": "1.0.0",
        "environment": "railway",
        "port": os.getenv("PORT", "8000")
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)