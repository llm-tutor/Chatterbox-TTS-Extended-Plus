# monitoring/middleware.py - Request/response logging middleware

import time
import uuid
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import json

from monitoring.logger import get_logger, metrics_collector
from monitoring.metrics import record_api_time

logger = get_logger(__name__)

class RequestLoggingMiddleware:
    """Middleware for logging requests and responses"""
    
    def __init__(self, app):
        self.app = app
        
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
            
        request = Request(scope, receive)
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Extract request info
        method = request.method
        url = str(request.url)
        headers = dict(request.headers)
        client_ip = request.client.host if request.client else "unknown"
        
        # Start request context
        with logger.request_context(request_id=request_id, operation=f"{method} {url}"):
            # Log request start
            logger.info(f"Request started: {method} {url}", extra_data={
                'method': method,
                'url': url,
                'client_ip': client_ip,
                'user_agent': headers.get('user-agent', 'unknown')
            })
            
            # Track metrics
            metrics_collector.increment_counter('requests_total')
            metrics_collector.record_endpoint_request(f"{method} {url}")
            
            response_body = b""
            status_code = 200
            
            async def send_wrapper(message):
                nonlocal response_body, status_code
                
                if message["type"] == "http.response.start":
                    status_code = message["status"]
                elif message["type"] == "http.response.body":
                    response_body += message.get("body", b"")
                    
                await send(message)
                
            try:
                await self.app(scope, receive, send_wrapper)
                
                # Record success
                metrics_collector.increment_counter('requests_success')
                
            except Exception as e:
                # Record error
                metrics_collector.increment_counter('requests_error')
                metrics_collector.record_error(type(e).__name__)
                
                logger.error(f"Request failed: {method} {url}", 
                           extra_data={'error': str(e)}, exc_info=True)
                raise
                
            finally:
                # Calculate duration
                duration_ms = (time.time() - start_time) * 1000
                
                # Record API timing
                record_api_time(duration_ms, f"{method} {request.url.path}")
                
                # Log response
                response_size = len(response_body)
                logger.info(f"Request completed: {method} {url}", extra_data={
                    'status_code': status_code,
                    'duration_ms': round(duration_ms, 2),
                    'response_size_bytes': response_size
                })

async def log_request_body_middleware(request: Request, call_next: Callable):
    """Middleware to log request bodies for API endpoints"""
    request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
    
    # Only log bodies for API endpoints
    if request.url.path.startswith('/api/'):
        try:
            body = await request.body()
            if body:
                # Try to parse as JSON for structured logging
                try:
                    body_json = json.loads(body.decode('utf-8'))
                    # Remove sensitive data if any
                    if 'text' in body_json and len(str(body_json['text'])) > 100:
                        body_json['text'] = str(body_json['text'])[:100] + "..."
                        
                    logger.info("Request body received", extra_data={
                        'body': body_json,
                        'body_size_bytes': len(body)
                    })
                except (json.JSONDecodeError, UnicodeDecodeError):
                    logger.info("Request body received (non-JSON)", extra_data={
                        'body_size_bytes': len(body),
                        'content_type': request.headers.get('content-type', 'unknown')
                    })
        except Exception as e:
            logger.warning(f"Could not log request body: {e}")
    
    response = await call_next(request)
    return response

# Export middleware
__all__ = [
    'RequestLoggingMiddleware',
    'log_request_body_middleware'
]
