"""
Main FastAPI application for HistAgent backend.

This module sets up the FastAPI application with all necessary
middleware, routes, and configuration.
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, Response, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from core.protocols.websocket_protocol import websocket_protocol
from .websocket import websocket_router
from .routes import api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    logger.info("Starting HistAgent backend...")
    
    # Startup tasks
    try:
        # Initialize any required services here
        logger.info("Backend startup complete")
        
        yield
        
    finally:
        # Cleanup tasks
        logger.info("Shutting down HistAgent backend...")
        
        # Clean up WebSocket connections
        active_sessions = websocket_protocol.get_active_sessions()
        for session_id in active_sessions:
            await websocket_protocol.disconnect(session_id)
        
        logger.info("Backend shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="HistAgent API",
    description="A specialized AI agent for historical research with real-time frontend interface",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    GZipMiddleware,
    minimum_size=1000,
)


# Custom middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests."""
    start_time = time.time()
    
    # Log request
    logger.info(f"{request.method} {request.url.path} - {request.client.host}")
    
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(f"Response {response.status_code} - {process_time:.3f}s")
    
    return response


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Global exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "path": request.url.path,
        }
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "HistAgent Backend",
        "version": "0.1.0",
        "active_sessions": len(websocket_protocol.get_active_sessions()),
    }


# Include routers
app.include_router(websocket_router, prefix="/ws")
app.include_router(api_router, prefix="/api/v1")

# Create a separate router for simple API endpoints (without version prefix)
from fastapi import APIRouter
simple_api_router = APIRouter()

@simple_api_router.post("/upload")
async def upload_file_simple(file: UploadFile = File(...)):
    """Simple upload endpoint for frontend compatibility."""
    from .routes import upload_file
    return await upload_file(file)

app.include_router(simple_api_router, prefix="/api")

# Serve static files (for frontend)
try:
    app.mount("/static", StaticFiles(directory="frontend/dist"), name="static")
except Exception:
    logger.warning("Frontend static files not found, skipping mount")

# Serve frontend at root (for SPA)
@app.get("/", include_in_schema=False)
async def serve_frontend():
    """Serve frontend application."""
    try:
        from fastapi.responses import FileResponse
        return FileResponse("frontend/dist/index.html")
    except Exception:
        return JSONResponse(
            status_code=200,
            content={
                "message": "HistAgent Backend API",
                "docs": "/docs",
                "health": "/health",
                "websocket": "/ws",
            }
        )


if __name__ == "__main__":
    import time
    
    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True,
    ) 