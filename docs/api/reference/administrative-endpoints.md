# Administrative API Endpoints

> **Chatterbox TTS Extended Plus** - Administrative and monitoring endpoints

## Overview

This document covers administrative, monitoring, and debugging endpoints that are primarily intended for system administrators, DevOps teams, and advanced users. These endpoints are separated from the main API documentation to keep the core user documentation focused and accessible.

## Endpoint Classification

### Core vs Administrative Separation
- **Core Endpoints** (in main `openapi.yaml`): User-facing functionality for TTS, voice conversion, and voice management
- **Administrative Endpoints** (this document): System monitoring, resource management, cleanup operations, and debugging tools

## Administrative Endpoints

### System Monitoring

#### GET `/api/v1/metrics`
**Purpose**: Get detailed system metrics and performance statistics

**Response**: JSON with system metrics including:
- CPU and memory usage
- Request counts and response times
- Model loading status and performance
- Error rates and patterns
- Queue status and processing metrics

**Use Cases**:
- System monitoring dashboards
- Performance optimization
- Capacity planning
- Health monitoring automation

**Example Response**:
```json
{
  "system": {
    "cpu_percent": 45.2,
    "memory_percent": 67.8,
    "disk_usage_percent": 23.1
  },
  "api": {
    "total_requests": 1547,
    "requests_per_minute": 12.3,
    "average_response_time_ms": 245,
    "error_rate_percent": 0.8
  },
  "models": {
    "tts_loaded": true,
    "vc_loaded": true,
    "tts_memory_mb": 1024,
    "vc_memory_mb": 512
  }
}
```

---

#### GET `/api/v1/resources`
**Purpose**: Get current resource usage and system capabilities

**Response**: Detailed resource information including:
- Available disk space
- Memory allocation
- GPU status (if applicable)
- Model memory usage
- Temporary file counts

**Use Cases**:
- Resource planning
- Cleanup scheduling
- System health checks
- Performance troubleshooting

**Example Response**:
```json
{
  "disk": {
    "total_gb": 500,
    "used_gb": 125,
    "available_gb": 375,
    "outputs_size_mb": 2048,
    "temp_files_count": 12
  },
  "memory": {
    "total_mb": 16384,
    "used_mb": 8192,
    "models_mb": 1536
  },
  "limits": {
    "max_file_size_mb": 100,
    "max_concurrent_requests": 5
  }
}
```

---

### Cleanup Management

#### POST `/api/v1/cleanup`
**Purpose**: Manually trigger cleanup operations

**Request Body**:
```json
{
  "target": "all|outputs|temp|old_files",
  "max_age_hours": 24,
  "dry_run": false
}
```

**Response**: Cleanup operation results
```json
{
  "status": "completed",
  "files_removed": 45,
  "bytes_freed": 1073741824,
  "duration_seconds": 2.1,
  "errors": []
}
```

**Use Cases**:
- Manual cleanup before maintenance
- Emergency disk space recovery
- Testing cleanup configurations
- Scheduled cleanup via external automation

---

#### GET `/api/v1/cleanup/status`
**Purpose**: Get status of automatic cleanup scheduler and recent cleanup history

**Response**: Cleanup scheduler status and history
```json
{
  "scheduler": {
    "running": true,
    "cleanup_on_startup": true,
    "cleanup_interval_hours": 5,
    "last_cleanup_time": "2025-06-23T18:00:00.123456+00:00",
    "next_cleanup_time": "2025-06-23T23:00:00.123456+00:00"
  },
  "recent_cleanups": [
    {
      "timestamp": "2025-06-23T18:00:00.123456+00:00",
      "files_removed": 12,
      "bytes_freed": 52428800,
      "duration_seconds": 0.8
    }
  ]
}
```

**Use Cases**:
- Monitoring cleanup effectiveness
- Verifying cleanup scheduling
- Troubleshooting storage issues
- Audit trails for maintenance

---

### Error Tracking & Debugging

#### GET `/api/v1/errors/summary`
**Purpose**: Get aggregated error statistics and patterns

**Query Parameters**:
- `hours`: Time window for statistics (default: 24)
- `group_by`: Group errors by type, endpoint, or time

**Response**: Error summary statistics
```json
{
  "period_hours": 24,
  "total_errors": 23,
  "error_rate_percent": 1.2,
  "by_type": {
    "validation_error": 15,
    "file_not_found": 5,
    "model_error": 3
  },
  "by_endpoint": {
    "/api/v1/tts": 18,
    "/api/v1/vc": 5
  },
  "trends": {
    "increasing": false,
    "peak_hour": 14
  }
}
```

**Use Cases**:
- Error rate monitoring
- Identifying problem patterns
- System health assessment
- Performance optimization targets

---

#### GET `/api/v1/errors/recent`
**Purpose**: Get recent error details for debugging

**Query Parameters**:
- `limit`: Number of recent errors (default: 50, max: 500)
- `level`: Error level filter (error, warning, critical)
- `endpoint`: Filter by specific endpoint

**Response**: Recent error entries
```json
{
  "errors": [
    {
      "timestamp": "2025-06-23T12:15:30.123456+00:00",
      "level": "error",
      "endpoint": "/api/v1/tts",
      "error_code": "VALIDATION_ERROR",
      "message": "Invalid temperature value: 2.5",
      "request_id": "req_abc123",
      "user_ip": "192.168.1.100"
    }
  ],
  "pagination": {
    "total": 150,
    "page": 1,
    "page_size": 50
  }
}
```

**Use Cases**:
- Real-time error debugging
- User support and troubleshooting
- API integration debugging
- System behavior analysis

---

## Security Considerations

### Access Control
Administrative endpoints should be protected with appropriate authentication and authorization:

- **Recommended**: Separate API keys or tokens for administrative access
- **Network Security**: Consider restricting access to admin endpoints by IP/network
- **Monitoring**: Log all administrative endpoint access for security auditing

### Rate Limiting
Administrative endpoints may have different rate limiting rules:
- Metrics endpoints: Higher frequency allowed for monitoring
- Cleanup endpoints: Lower frequency to prevent system overload
- Error endpoints: Moderate frequency for debugging needs

---

## Integration Examples

### Monitoring Dashboard
```python
import requests
import time

def get_system_health():
    """Get comprehensive system health for dashboard"""
    base_url = "http://localhost:7860/api/v1"
    
    # Get multiple admin endpoints
    metrics = requests.get(f"{base_url}/metrics").json()
    resources = requests.get(f"{base_url}/resources").json()
    cleanup_status = requests.get(f"{base_url}/cleanup/status").json()
    error_summary = requests.get(f"{base_url}/errors/summary?hours=1").json()
    
    return {
        "cpu_usage": metrics["system"]["cpu_percent"],
        "memory_usage": metrics["system"]["memory_percent"],
        "disk_available": resources["disk"]["available_gb"],
        "error_rate": error_summary["error_rate_percent"],
        "last_cleanup": cleanup_status["scheduler"]["last_cleanup_time"]
    }
```

### Automated Cleanup
```python
def scheduled_cleanup():
    """Automated cleanup with monitoring"""
    cleanup_url = "http://localhost:7860/api/v1/cleanup"
    
    # Trigger cleanup
    response = requests.post(cleanup_url, json={
        "target": "outputs",
        "max_age_hours": 48,
        "dry_run": False
    })
    
    result = response.json()
    print(f"Cleaned {result['files_removed']} files, freed {result['bytes_freed']} bytes")
```

---

## Future Automation Plans

### Documentation Maintenance Automation
This separation between core and administrative endpoints is designed to support future automation:

1. **Automatic Endpoint Detection**: Future tooling will scan `main_api.py` to identify new endpoints
2. **Classification Rules**: Endpoints will be automatically classified as 'core' or 'administrative' based on:
   - Endpoint patterns (e.g., `/metrics`, `/cleanup`, `/errors` → administrative)
   - Response model types (monitoring vs user-facing)
   - HTTP methods and purposes
3. **Documentation Generation**: Core endpoints update `openapi.yaml`, administrative endpoints update this document
4. **Validation Automation**: Automated checks ensure both documents stay synchronized with implementation

### Implementation Notes for Future Automation
- **Core Endpoint Patterns**: `/tts`, `/vc`, `/voice`, `/voices`, `/outputs`, `/health`, `/config`
- **Administrative Patterns**: `/metrics`, `/resources`, `/cleanup`, `/errors`
- **Classification Markers**: Response models ending in `Response` (core) vs monitoring data structures (administrative)

---

## Changelog

### Version History
- **v1.0**: Initial separation of administrative endpoints from core API documentation
- **Future**: Automated maintenance and synchronization with implementation

---

*This document is maintained alongside the main API documentation and should be updated when administrative endpoints are added, modified, or removed.*