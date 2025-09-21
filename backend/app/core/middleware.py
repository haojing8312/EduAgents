"""
Custom Middleware for PBL Assistant API
Provides request tracking, metrics, rate limiting, and logging
"""

import time
import uuid
import logging
from typing import Callable
from collections import defaultdict, deque
from datetime import datetime, timedelta

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


logger = logging.getLogger(__name__)


class RequestTrackingMiddleware(BaseHTTPMiddleware):
    """Middleware to track request processing time and add request IDs"""

    async def dispatch(self, request: Request, call_next: Callable):
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Track start time
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Calculate processing time
        process_time = time.time() - start_time

        # Add headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)

        # Log request
        logger.info(
            f"Request {request_id}: {request.method} {request.url.path} "
            f"- {response.status_code} - {process_time:.3f}s"
        )

        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Enhanced logging middleware"""

    async def dispatch(self, request: Request, call_next: Callable):
        request_id = getattr(request.state, "request_id", "unknown")

        # Log request details
        logger.info(
            f"Request {request_id} started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
                "client_ip": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent", "unknown"),
            }
        )

        try:
            response = await call_next(request)

            # Log response
            logger.info(
                f"Request {request_id} completed",
                extra={
                    "request_id": request_id,
                    "status_code": response.status_code,
                }
            )

            return response

        except Exception as e:
            # Log error
            logger.error(
                f"Request {request_id} failed",
                extra={
                    "request_id": request_id,
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
                exc_info=True
            )
            raise


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect application metrics"""

    def __init__(self, app):
        super().__init__(app)
        self.request_count = defaultdict(int)
        self.response_times = defaultdict(list)
        self.error_count = defaultdict(int)

    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()
        endpoint = f"{request.method} {request.url.path}"

        try:
            response = await call_next(request)

            # Track metrics
            self.request_count[endpoint] += 1
            process_time = time.time() - start_time
            self.response_times[endpoint].append(process_time)

            # Keep only last 1000 response times per endpoint
            if len(self.response_times[endpoint]) > 1000:
                self.response_times[endpoint] = self.response_times[endpoint][-1000:]

            return response

        except Exception as e:
            # Track errors
            self.error_count[endpoint] += 1
            raise


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware"""

    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients = defaultdict(lambda: deque())

    def _clean_old_requests(self, client_requests: deque):
        """Remove requests older than the period"""
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=self.period)

        while client_requests and client_requests[0] < cutoff:
            client_requests.popleft()

    async def dispatch(self, request: Request, call_next: Callable):
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/api/health"]:
            return await call_next(request)

        # Get client identifier
        client_ip = request.client.host if request.client else "unknown"

        # Clean old requests
        client_requests = self.clients[client_ip]
        self._clean_old_requests(client_requests)

        # Check rate limit
        if len(client_requests) >= self.calls:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Too many requests.",
                headers={"Retry-After": str(self.period)}
            )

        # Record this request
        client_requests.append(datetime.utcnow())

        return await call_next(request)


class CORSMiddleware(BaseHTTPMiddleware):
    """Custom CORS middleware with specific PBL Assistant requirements"""

    def __init__(self, app, allowed_origins: list = None):
        super().__init__(app)
        self.allowed_origins = allowed_origins or ["*"]

    async def dispatch(self, request: Request, call_next: Callable):
        # Handle preflight requests
        if request.method == "OPTIONS":
            response = Response()
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
            response.headers["Access-Control-Max-Age"] = "86400"
            return response

        response = await call_next(request)

        # Add CORS headers
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"

        return response