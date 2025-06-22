# Health Endpoint

Check the API server status and get system information.

## Endpoint

**GET** `/api/v1/health`

Simple health check endpoint to verify the API server is running and responsive.

## Parameters

No parameters required.

## Response

### Success Response

```json
{
  "success": true,
  "message": "API is healthy",
  "timestamp": "2025-06-22T14:30:00Z"
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Always `true` for successful responses |
| `message` | string | Status message |
| `timestamp` | string | ISO 8601 timestamp of the response |

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
    print(f"API Status: {data['message']}")
else:
    print(f"Health check failed: {response.status_code}")
```

### JavaScript

```javascript
async function checkHealth() {
    try {
        const response = await fetch('http://localhost:7860/api/v1/health');
        const data = await response.json();
        console.log('API Status:', data.message);
        return data.success;
    } catch (error) {
        console.error('Health check failed:', error);
        return false;
    }
}
```

## Error Responses

If the server is not running or experiencing issues, you'll receive:

- **Connection Error**: No response (server down)
- **HTTP 500**: Server internal error

## Use Cases

- **Service Monitoring**: Verify API availability in monitoring systems
- **Connection Testing**: Test API connectivity before making other requests
- **Load Balancer Health Checks**: Used by load balancers to check service health
- **Development Testing**: Quick verification during development

## Related Endpoints

- [Configuration](../reference/configuration.md) - For detailed system configuration
- [Outputs](file-operations.md) - For checking generated files

---

*Need help? Check the [Quick Start Guide](../quick-start.md) or [Error Handling Guide](../guides/error-handling.md)*