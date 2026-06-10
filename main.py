"""FastAPI application entry point."""

from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config.settings import settings
from app.core.exceptions import BaseException
from app.core.middleware import (
    SecurityHeadersMiddleware, 
    RateLimitMiddleware, 
    RequestLoggingMiddleware,
    CORSConfigMiddleware,
    InputSanitizationMiddleware
)
from app.api import auth, companies, fleets, vehicles, drivers, trips

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Transport Business Operating System API - Production Ready",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Add security middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(InputSanitizationMiddleware)
app.add_middleware(RateLimitMiddleware, calls=100, period=60)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)
app.add_middleware(CORSConfigMiddleware)


# Exception handlers
@app.exception_handler(BaseException)
async def base_exception_handler(request, exc: BaseException):
    """Handle base exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "detail": exc.detail, 
            "code": exc.code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    """Handle request validation errors."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=422,
        content={
            "error": True,
            "detail": "Validation failed",
            "errors": errors,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc: StarletteHTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "detail": exc.detail,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle unexpected exceptions."""
    import traceback
    
    # Log the full error in production
    print(f"Unexpected error: {exc}")
    print(traceback.format_exc())
    
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "detail": "Internal server error" if settings.ENV == "production" else str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy", 
        "service": "FleetMaster API",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    from app.core.cache import cache
    from app.core.rbac import seed_rbac
    from app.config.database import SessionLocal

    await cache.connect()

    db = SessionLocal()
    try:
        seed_rbac(db)
    finally:
        db.close()
    
    print(f"🚀 {settings.APP_NAME} API started successfully!")
    print(f"📊 Environment: {settings.ENV}")
    if settings.DEBUG:
        print(f"📖 API Documentation: http://localhost:8000/docs")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    from app.core.cache import cache
    await cache.disconnect()
    
    print(f"🛑 {settings.APP_NAME} API shutting down...")


# Include API routers
app.include_router(auth.router, prefix="/v1/auth", tags=["auth"])
app.include_router(companies.router, prefix="/v1/companies", tags=["companies"])
app.include_router(fleets.router, prefix="/v1/fleets", tags=["fleets"])
app.include_router(vehicles.router, prefix="/v1/vehicles", tags=["vehicles"])
app.include_router(drivers.router, prefix="/v1/drivers", tags=["drivers"])
app.include_router(trips.router, prefix="/v1/trips", tags=["trips"])

# Import and include additional endpoints
from app.api import dashboard, websocket, fuel, maintenance, audit, health, whatsapp, documents
app.include_router(dashboard.router, prefix="/v1/dashboard", tags=["dashboard"])
app.include_router(websocket.router, prefix="/v1", tags=["websocket"])
app.include_router(fuel.router, prefix="/v1/fuel", tags=["fuel"])
app.include_router(maintenance.router, prefix="/v1/maintenance", tags=["maintenance"])
app.include_router(audit.router, prefix="/v1/audit", tags=["audit"])
app.include_router(health.router, prefix="/v1/health", tags=["health"])
app.include_router(whatsapp.router, prefix="/v1/whatsapp", tags=["whatsapp"])
app.include_router(documents.router, prefix="/v1/documents", tags=["documents"])



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
