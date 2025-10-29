# Health Endpoint

Check the API server status and get comprehensive system information.

## Endpoint

**GET** `/api/v1/health`

Enhanced health check endpoint to verify the API server is running and get detailed system metrics.

## Parameters

No parameters required.

## Response

### Success Response

```json
{
  "status": "healthy",
  "models_loaded": {
    "tts": true,
    "vc": true
  },
  "version": "1.8.2",
  "uptime_seconds": 950.68,
  "metrics": {
    "requests_total": 2,
    "requests_success": 1,
    "requests_error": 0,
    "tts_generations": 0,
    "vc_generations": 0,
    "total_processing_time": 0.0,
    "average_processing_time": 0.0,
    "model_loads": 0,
    "errors_by_type": {},
    "requests_by_endpoint": {
      "GET http://localhost:7860/api/v1/health": 2
    },
    "processing_times": [],
    "success_rate": 0.5,
    "error_rate": 0.0
  },
  "system_info": {
    "cpu_percent": 0.7,
    "memory": {
      "rss_mb": 2260.71,
      "vms_mb": 11125.27,
      "percent": 6.92
    },
    "disk": {
      "free_gb": 27.97,
      "usage_percent": 87.49
    },
    "file_counts": {
      "outputs": 2281,
      "temp": 3
    }
  },
  "resource_status": {
    "timestamp": "2025-07-30T19:01:16.988650",
    "directories": {
      "outputs": {
        "size_bytes": 1275589964,
        "size_mb": 1216.50,
        "max_size_mb": 5120.0,
        "usage_percent": 23.76,
        "file_count": 2268
      },
      "temp": {
        "size_bytes": 1086960,
        "size_mb": 1.04,
        "file_count": 3,
        "max_files": 200,
        "usage_percent": 1.5
      },
      "vc_inputs": {
        "size_bytes": 4440606,
        "size_mb": 4.23,
        "max_size_mb": 2048.0,
        "usage_percent": 0.21,
        "file_count": 18
      }
    },
    "warnings": []
  },
  "warnings": null,
  "error_summary": null
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Server health status (always "healthy" for successful responses) |
| `models_loaded` | object | Status of AI models with boolean flags for TTS and VC models |
| `version` | string | Current API version |
| `uptime_seconds` | number | Server uptime in seconds since last restart |
| `metrics` | object | Detailed API usage and performance metrics |
| `system_info` | object | System resource information (CPU, memory, disk) |
| `resource_status` | object | Detailed directory usage and resource allocation |
| `warnings` | array/null | System warnings if any issues detected |
| `error_summary` | object/null | Error summary from last 24 hours (null if no errors) |

#### Metrics Object Fields

| Field | Type | Description |
|-------|------|-------------|
| `requests_total` | number | Total number of API requests processed |
| `requests_success` | number | Number of successful requests |
| `requests_error` | number | Number of failed requests |
| `tts_generations` | number | Total TTS generations completed |
| `vc_generations` | number | Total voice conversions completed |
| `total_processing_time` | number | Cumulative processing time in seconds |
| `average_processing_time` | number | Average processing time per request |
| `model_loads` | number | Number of times models were loaded |
| `errors_by_type` | object | Breakdown of errors by type |
| `requests_by_endpoint` | object | Request count per endpoint |
| `processing_times` | array | Recent processing times for performance analysis |
| `success_rate` | number | Success rate as decimal (0.0 to 1.0) |
| `error_rate` | number | Error rate as decimal (0.0 to 1.0) |

#### System Info Object Fields

| Field | Type | Description |
|-------|------|-------------|
| `cpu_percent` | number | Current CPU usage percentage |
| `memory.rss_mb` | number | Resident set size in megabytes |
| `memory.vms_mb` | number | Virtual memory size in megabytes |
| `memory.percent` | number | Memory usage percentage |
| `disk.free_gb` | number | Available disk space in gigabytes |
| `disk.usage_percent` | number | Disk usage percentage |
| `file_counts.outputs` | number | Number of files in outputs directory |
| `file_counts.temp` | number | Number of files in temp directory |

#### Resource Status Object Fields

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | string | ISO 8601 timestamp of resource status check |
| `directories` | object | Detailed information for each managed directory |
| `warnings` | array | List of resource-related warnings |

Each directory object contains:
- `size_bytes`: Total size in bytes
- `size_mb`: Total size in megabytes  
- `file_count`: Number of files
- `max_size_mb`: Maximum allowed size in megabytes
- `usage_percent`: Usage percentage of allowed maximum
- `max_files`: Maximum allowed files (for temp directory)

## Usage Examples

### cURL

```bash
curl http://localhost:7860/api/v1/health
```

### Python

```python
import requests

response = requests.get("http://localhost:7860/api/v1/health")
if response.status_code == 200:
    data = response.json()
    print(f"API Status: {data['status']}")
    print(f"Version: {data['version']}")
    print(f"Uptime: {data['uptime_seconds']:.1f} seconds")
    print(f"Models loaded - TTS: {data['models_loaded']['tts']}, VC: {data['models_loaded']['vc']}")
    print(f"CPU Usage: {data['system_info']['cpu_percent']}%")
    print(f"Memory Usage: {data['system_info']['memory']['percent']:.1f}%")
    print(f"Disk Free: {data['system_info']['disk']['free_gb']:.1f} GB")
else:
    print(f"Health check failed: {response.status_code}")
```

### JavaScript

```javascript
async function checkHealth() {
    try {
        const response = await fetch('http://localhost:7860/api/v1/health');
        const data = await response.json();
        
        console.log('API Status:', data.status);
        console.log('Version:', data.version);
        console.log('Uptime:', `${(data.uptime_seconds / 60).toFixed(1)} minutes`);
        console.log('Models:', data.models_loaded);
        console.log('System:', {
            cpu: `${data.system_info.cpu_percent}%`,
            memory: `${data.system_info.memory.percent.toFixed(1)}%`,
            disk_free: `${data.system_info.disk.free_gb.toFixed(1)} GB`
        });
        
        return data.status === 'healthy';
    } catch (error) {
        console.error('Health check failed:', error);
        return false;
    }
}
```

### PowerShell

```powershell
# Simple health check
$response = Invoke-RestMethod -Uri "http://localhost:7860/api/v1/health"
Write-Host "Status: $($response.status)"
Write-Host "Version: $($response.version)"
Write-Host "Uptime: $([math]::Round($response.uptime_seconds / 60, 1)) minutes"

# Detailed system monitoring
$health = Invoke-RestMethod -Uri "http://localhost:7860/api/v1/health"
$system = $health.system_info
Write-Host "System Resources:"
Write-Host "  CPU: $($system.cpu_percent)%"
Write-Host "  Memory: $([math]::Round($system.memory.percent, 1))%"
Write-Host "  Disk Free: $([math]::Round($system.disk.free_gb, 1)) GB"
Write-Host "  Output Files: $($system.file_counts.outputs)"
```

## Error Responses

If the server is not running or experiencing issues, you'll receive:

- **Connection Error**: No response (server down)
- **HTTP 500**: Server internal error with JSON response containing error details

## Use Cases

### System Monitoring
- **Health Dashboards**: Integrate health data into monitoring dashboards
- **Automated Monitoring**: Use metrics for alerting and trend analysis
- **Performance Tracking**: Monitor request rates, processing times, and error rates
- **Resource Management**: Track disk usage, file counts, and memory consumption

### Development & Operations
- **Service Discovery**: Verify API availability and version compatibility
- **Load Testing**: Monitor system performance under load
- **Debugging**: Analyze error patterns and system resource usage
- **Capacity Planning**: Use historical metrics for scaling decisions

### Integration Examples
- **Load Balancer Health Checks**: Simple status verification
- **Monitoring Tools**: Integration with Prometheus, Grafana, or similar tools
- **CI/CD Pipelines**: Automated health verification during deployments
- **Client Applications**: Version compatibility checks and error handling

## Advanced Usage

### Monitoring Script Example

```python
import requests
import time
from datetime import datetime

def monitor_api_health(interval_seconds=60):
    """Continuous monitoring with alerts"""
    while True:
        try:
            response = requests.get("http://localhost:7860/api/v1/health", timeout=10)
            data = response.json()
            
            # Check critical metrics
            cpu = data['system_info']['cpu_percent']
            memory = data['system_info']['memory']['percent']
            disk_free = data['system_info']['disk']['free_gb']
            error_rate = data['metrics']['error_rate']
            
            timestamp = datetime.now().isoformat()
            print(f"[{timestamp}] Health: {data['status']}")
            
            # Alert conditions
            if cpu > 90:
                print(f"⚠️  HIGH CPU: {cpu}%")
            if memory > 85:
                print(f"⚠️  HIGH MEMORY: {memory:.1f}%")
            if disk_free < 5:
                print(f"⚠️  LOW DISK: {disk_free:.1f} GB")
            if error_rate > 0.1:
                print(f"⚠️  HIGH ERROR RATE: {error_rate:.1%}")
                
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            
        time.sleep(interval_seconds)
```

## Related Endpoints

- [Metrics](../reference/administrative-endpoints.md#get-apiv1metrics) - Detailed system metrics
- [Configuration](../reference/configuration.md) - For system configuration details
- [Outputs](file-operations.md) - For checking generated files

---

*Need help? Check the [Quick Start Guide](../quick-start.md) or [Error Handling Guide](../guides/error-handling.md)*