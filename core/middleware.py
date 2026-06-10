"""Security and rate limiting middleware."""

import time
import json
from typing import Dict, Any, Optional
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
import ipaddress
from datetime import datetime, timedelta

from app.core.cache import cache, CacheKeys
from app.config.settings import settings
from app.core.logging_config import logger, log_audit



class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # HSTS for HTTPS
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware."""
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        # Get client IP
        client_ip = self.get_client_ip(request)
        
        # Different limits for different endpoints
        endpoint_limits = self.get_endpoint_limits(request.url.path)
        
        # Check rate limit
        if not await self.check_rate_limit(client_ip, request.url.path, endpoint_limits):
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded",
                    "retry_after": self.period
                },
                headers={"Retry-After": str(self.period)}
            )
        
        return await call_next(request)
    
    def get_client_ip(self, request: Request) -> str:
        """Extract client IP from request."""
        # Check X-Forwarded-For header
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # Check X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct client IP
        return request.client.host if request.client else "unknown"
    
    def get_endpoint_limits(self, path: str) -> Dict[str, int]:
        """Get rate limits for specific endpoints."""
        # Authentication endpoints - stricter limits
        if "/auth/" in path:
            return {"calls": 10, "period": 60}  # 10 calls per minute
        
        # WebSocket endpoints - more lenient
        if "/ws/" in path:
            return {"calls": 1000, "period": 60}  # 1000 calls per minute
        
        # API endpoints - moderate limits
        if "/v1/" in path:
            return {"calls": 100, "period": 60}  # 100 calls per minute
        
        # Default limits
        return {"calls": self.calls, "period": self.period}
    
    async def check_rate_limit(self, client_ip: str, endpoint: str, limits: Dict[str, int]) -> bool:
        """Check if request is within rate limit."""
        try:
            key = CacheKeys.RATE_LIMIT_IP.format(ip_address=client_ip, endpoint=endpoint.replace("/", "_"))
            
            # Get current count
            current_count = await cache.get(key) or 0
            
            if current_count >= limits["calls"]:
                return False
            
            # Increment counter
            await cache.increment(key)
            
            # Set expiry if this is the first request
            if current_count == 0:
                await cache.expire(key, limits["period"])
            
            return True
            
        except Exception as e:
            print(f"Rate limiting error: {e}")
            return True  # Allow request if rate limiting fails


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests for monitoring."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request details
        logger.info(
            f"Incoming request: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params)
            }
        )
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Add processing time header
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log response details
        logger.info(
            f"Request completed: {request.method} {request.url.path} -> {response.status_code}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time_seconds": process_time
            }
        )
        
        return response



class IPWhitelistMiddleware(BaseHTTPMiddleware):
    """IP whitelist middleware for admin endpoints."""
    
    def __init__(self, app, admin_paths: list = None, allowed_ips: list = None):
        super().__init__(app)
        self.admin_paths = admin_paths or ["/admin", "/internal"]
        self.allowed_ips = allowed_ips or ["127.0.0.1", "::1"]
    
    async def dispatch(self, request: Request, call_next):
        # Check if this is an admin path
        if not any(request.url.path.startswith(path) for path in self.admin_paths):
            return await call_next(request)
        
        # Get client IP
        client_ip = self.get_client_ip(request)
        
        # Check if IP is allowed
        if not self.is_ip_allowed(client_ip):
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "Access denied from this IP address"}
            )
        
        return await call_next(request)
    
    def get_client_ip(self, request: Request) -> str:
        """Extract client IP from request."""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def is_ip_allowed(self, client_ip: str) -> bool:
        """Check if IP address is in whitelist."""
        try:
            client_addr = ipaddress.ip_address(client_ip)
            
            for allowed_ip in self.allowed_ips:
                try:
                    # Support both individual IPs and CIDR ranges
                    if "/" in allowed_ip:
                        allowed_network = ipaddress.ip_network(allowed_ip, strict=False)
                        if client_addr in allowed_network:
                            return True
                    else:
                        allowed_addr = ipaddress.ip_address(allowed_ip)
                        if client_addr == allowed_addr:
                            return True
                except ValueError:
                    continue
            
            return False
            
        except ValueError:
            # Invalid IP address
            return False


class AuthenticationLoggerMiddleware(BaseHTTPMiddleware):
    """Log authentication attempts for security monitoring."""
    
    async def dispatch(self, request: Request, call_next):
        # Only log auth endpoints
        if "/auth/" not in request.url.path:
            return await call_next(request)
        
        # Get request details
        client_ip = self.get_client_ip(request)
        user_agent = request.headers.get("User-Agent", "Unknown")
        
        # Process request
        response = await call_next(request)
        
        # Log authentication attempt
        if request.url.path.endswith("/login") and request.method == "POST":
            success = response.status_code == 200
            
            # Structured audit logging
            log_audit(
                action="LOGIN",
                resource_type="user",
                status="success" if success else "failure",
                details={
                    "ip_address": client_ip,
                    "user_agent": user_agent,
                    "status_code": response.status_code
                }
            )
        
        return response

    
    def get_client_ip(self, request: Request) -> str:
        """Extract client IP from request."""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"


class InputSanitizationMiddleware(BaseHTTPMiddleware):
    """Sanitize input data to prevent injection attacks."""
    
    DANGEROUS_PATTERNS = [
        # SQL injection patterns
        "(?i)(union|select|insert|update|delete|drop|create|alter|exec|execute)",
        # XSS patterns  
        "(?i)(<script|javascript:|vbscript:|onload|onerror)",
        # Path traversal
        r"(\.\.\/|\.\.\\)",
        # Command injection
        r"(;|\||&|`|\$\()"
    ]
    
    async def dispatch(self, request: Request, call_next):
        # Only check certain content types
        content_type = request.headers.get("Content-Type", "")
        if not content_type.startswith(("application/json", "application/x-www-form-urlencoded")):
            return await call_next(request)
        
        # Read and validate request body
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    body_str = body.decode("utf-8")
                    
                    # Check for dangerous patterns
                    import re
                    for pattern in self.DANGEROUS_PATTERNS:
                        if re.search(pattern, body_str):
                            return JSONResponse(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                content={"detail": "Invalid input detected"}
                            )
                
            except Exception:
                pass  # Continue if we can't decode body
        
        return await call_next(request)


class CORSConfigMiddleware(CORSMiddleware):
    """Enhanced CORS middleware with environment-specific settings."""
    
    def __init__(self, app):
        if settings.ENV == "production":
            # Strict CORS for production
            allowed_origins = [
                "https://fleetmaster.app",
                "https://app.fleetmaster.com"
            ]
        else:
            # Lenient CORS for development
            allowed_origins = settings.CORS_ORIGINS
        
        super().__init__(
            app,
            allow_origins=allowed_origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
            allow_headers=["*"],
            expose_headers=["X-Process-Time"]
        )