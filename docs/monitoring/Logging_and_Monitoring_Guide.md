# Enhanced Logging and Monitoring Guide

**Version:** 1.7.0  
**Last Updated:** 2025-06-19  
**Phase:** 7.1 - Enhanced Operations & Monitoring

## Overview

The Chatterbox TTS Extended Plus API now includes comprehensive logging and monitoring capabilities designed for production deployment and operational visibility. This guide covers all logging and monitoring features, how to use them, and how to analyze the collected data.

## Table of Contents

1. [Enhanced Logging System](#enhanced-logging-system)
2. [Performance Metrics Collection](#performance-metrics-collection)
3. [Request/Response Monitoring](#requestresponse-monitoring)
4. [Health Check and Metrics Endpoints](#health-check-and-metrics-endpoints)
5. [Configuration](#configuration)
6. [Log Analysis and Troubleshooting](#log-analysis-and-troubleshooting)
7. [Production Best Practices](#production-best-practices)

## Enhanced Logging System

### Features

The enhanced logging system provides:
- **Structured JSON logging** for easy parsing and analysis
- **Request tracing** with unique request IDs
- **Operation timing** for performance analysis
- **Context tracking** throughout request lifecycle
- **Multiple output targets** (console and file)
- **Thread-safe operation** for concurrent requests

### Log Format

All logs are output in structured JSON format:

```json
{
  "timestamp": "2025-06-19T15:33:07.088582+00:00",
  "level": "INFO",
  "logger": "core_engine",
  "message": "Starting TTS generation for text: Hello world...",
  "module": "core_engine",
  "function": "generate_tts",
  "line": 262,
  "request_id": "abc123-def456-ghi789",
  "operation": "tts_generation",
  "data": {
    "text_length": 50,
    "parameters": {
      "temperature": 0.75,
      "seed": 42
    }
  }
}
```

### Log Levels

- **DEBUG**: Detailed debugging information
- **INFO**: General application flow and operations
- **WARNING**: Potential issues that don't prevent operation
- **ERROR**: Error conditions that may affect functionality
- **CRITICAL**: Serious errors that may cause application failure

### Log Locations

#### Console Output
All logs are displayed on the console when running the application with structured JSON formatting.

#### File Output
Log files are written to the configured location (default: `logs/chatterbox_extended.log`):

```
project_root/
├── logs/
│   └── chatterbox_extended.log    # Main application log file
```

### Request Tracing

Every API request gets a unique request ID that follows the request through its entire lifecycle:

```json
{"timestamp": "...", "request_id": "req_123", "message": "Request started: POST /api/v1/tts"}
{"timestamp": "...", "request_id": "req_123", "message": "Starting TTS generation..."}
{"timestamp": "...", "request_id": "req_123", "message": "TTS generation completed"}
{"timestamp": "...", "request_id": "req_123", "message": "Request completed: POST /api/v1/tts"}
```

### Operation Timing

Critical operations are automatically timed:

```json
{
  "message": "Completed operation: tts_generation",
  "operation": "tts_generation",
  "duration_ms": 2847.5,
  "request_id": "req_123"
}
```

## Performance Metrics Collection

### System Metrics

The system continuously collects metrics about:

#### CPU Usage
- Current CPU usage percentage
- Process-specific CPU consumption

#### Memory Usage
- RSS (Resident Set Size) in MB
- VMS (Virtual Memory Size) in MB
- Memory usage percentage

#### Disk Usage
- Free disk space in GB
- Disk usage percentage for output directories

#### File Counts
- Number of files in output directories
- Number of temporary files

### Performance Metrics

#### Processing Times
- TTS generation duration
- VC processing duration
- API response times
- Operation-specific timing

#### Request Statistics
- Total requests processed
- Success/error rates
- Requests by endpoint
- Error types and frequencies

### Accessing Metrics

#### Via API Endpoints

**Basic Health Check:**
```bash
GET /api/v1/health
```

Response includes basic metrics:
```json
{
  "status": "healthy",
  "models_loaded": {"tts": true, "vc": true},
  "version": "1.7.0",
  "uptime_seconds": 3600.5,
  "metrics": {
    "requests_total": 150,
    "requests_success": 147,
    "requests_error": 3,
    "success_rate": 0.98,
    "average_processing_time": 1250.5
  },
  "system_info": {
    "cpu_percent": 15.2,
    "memory": {"rss_mb": 502.4, "percent": 12.5},
    "disk": {"free_gb": 45.8, "usage_percent": 65.2}
  }
}
```

**Detailed Metrics:**
```bash
GET /api/v1/metrics
```

Response includes comprehensive metrics:
```json
{
  "timestamp": "2025-06-19T15:33:07Z",
  "system": {
    "cpu_percent": 15.2,
    "memory": {
      "rss_mb": 502.4,
      "vms_mb": 1024.8,
      "percent": 12.5
    },
    "disk": {
      "free_gb": 45.8,
      "usage_percent": 65.2
    },
    "file_counts": {
      "outputs": 25,
      "temp": 3
    }
  },
  "performance": {
    "time_window_minutes": 60,
    "processing_times": {
      "min_ms": 450.2,
      "max_ms": 5670.8,
      "avg_ms": 1250.5,
      "count": 15
    },
    "response_times": {
      "min_ms": 500.1,
      "max_ms": 6000.2,
      "avg_ms": 1350.7,
      "count": 18
    }
  }
}
```

## Request/Response Monitoring

### Automatic Request Logging

Every HTTP request is automatically logged with:

#### Request Start
```json
{
  "message": "Request started: POST /api/v1/tts",
  "method": "POST",
  "url": "http://localhost:7860/api/v1/tts",
  "client_ip": "127.0.0.1",
  "user_agent": "python-requests/2.31.0",
  "request_id": "req_123"
}
```

#### Request Body (for API endpoints)
```json
{
  "message": "Request body received",
  "body": {
    "text": "Hello world! This is a test of the TTS system...",
    "temperature": 0.75,
    "seed": 42
  },
  "body_size_bytes": 156,
  "request_id": "req_123"
}
```

#### Request Completion
```json
{
  "message": "Request completed: POST /api/v1/tts",
  "status_code": 200,
  "duration_ms": 2847.5,
  "response_size_bytes": 1024,
  "request_id": "req_123"
}
```

### Error Tracking

Failed requests are automatically tracked:

```json
{
  "message": "Request failed: POST /api/v1/tts",
  "error": "Text cannot be empty",
  "status_code": 400,
  "request_id": "req_123"
}
```

## Health Check and Metrics Endpoints

### Health Check Endpoint

**Endpoint:** `GET /api/v1/health`  
**Purpose:** Quick health status and basic metrics  
**Use Case:** Load balancer health checks, basic monitoring

**Response Fields:**
- `status`: Application health status
- `models_loaded`: Status of AI models
- `version`: Application version
- `uptime_seconds`: Time since application start
- `metrics`: Basic request and performance metrics
- `system_info`: Current system resource usage

### Detailed Metrics Endpoint

**Endpoint:** `GET /api/v1/metrics`  
**Purpose:** Comprehensive system and performance metrics  
**Use Case:** Detailed monitoring, performance analysis, alerting

**Response Fields:**
- `timestamp`: Metrics collection timestamp
- `system`: Detailed system resource metrics
- `performance`: Processing and response time statistics

### Usage Examples

#### Basic Health Check
```bash
curl http://localhost:7860/api/v1/health
```

#### Detailed Metrics
```bash
curl http://localhost:7860/api/v1/metrics | jq .
```

#### Continuous Monitoring Script
```bash
#!/bin/bash
while true; do
  echo "=== $(date) ==="
  curl -s http://localhost:7860/api/v1/health | jq '.system_info'
  sleep 30
done
```

## Configuration

### Logging Configuration

Configure logging in `config.yaml`:

```yaml
server:
  log_level: "INFO"                           # DEBUG, INFO, WARNING, ERROR, CRITICAL
  log_file_path: "logs/chatterbox_extended.log"  # Log file location
  log_file_max_size_mb: 10                    # Max log file size before rotation
  log_file_backup_count: 5                    # Number of backup files to keep

paths:
  logs_dir: "logs"                            # Directory for log files
```

### Performance Monitoring Configuration

```yaml
api:
  max_text_length: 10000                      # Maximum text length for TTS
  cleanup_temp_files: true                    # Enable automatic cleanup
  enable_url_downloads: true                  # Allow URL downloads for audio
  download_timeout_seconds: 30                # Timeout for URL downloads
```

### Environment Variables

Override configuration with environment variables:

```bash
export CHATTERBOX_LOG_LEVEL=DEBUG
export CHATTERBOX_LOG_FILE=/var/log/chatterbox/app.log
```

## Log Analysis and Troubleshooting

### Finding Logs

#### Console Logs
All logs appear on stdout/stderr when running the application.

#### File Logs
Default location: `logs/chatterbox_extended.log`

#### Log Structure
```
project_root/
├── logs/
│   ├── chatterbox_extended.log      # Current log file
│   ├── chatterbox_extended.log.1    # Rotated log file 1
│   ├── chatterbox_extended.log.2    # Rotated log file 2
│   └── ...
```

### Analyzing Logs

#### Using jq for JSON Log Analysis

**Find all errors:**
```bash
grep '"level":"ERROR"' logs/chatterbox_extended.log | jq .
```

**Find requests by ID:**
```bash
grep '"request_id":"req_123"' logs/chatterbox_extended.log | jq .
```

**Performance analysis:**
```bash
grep '"operation":"tts_generation"' logs/chatterbox_extended.log | jq '.data.duration_ms'
```

**Error summary:**
```bash
grep '"level":"ERROR"' logs/chatterbox_extended.log | jq -r '.message' | sort | uniq -c
```

#### Using Log Analysis Tools

**ELK Stack (Elasticsearch, Logstash, Kibana):**
- Configure Logstash to parse JSON logs
- Set up index patterns in Kibana
- Create dashboards for metrics visualization

**Grafana + Loki:**
- Use Promtail to ship logs to Loki
- Create Grafana dashboards for log analysis
- Set up alerts based on log patterns

### Common Troubleshooting Scenarios

#### High Memory Usage
```bash
# Check memory metrics
curl -s http://localhost:7860/api/v1/metrics | jq '.system.memory'

# Find memory-related logs
grep -i "memory\|mem" logs/chatterbox_extended.log | jq .
```

#### Slow Response Times
```bash
# Check processing times
curl -s http://localhost:7860/api/v1/metrics | jq '.performance.processing_times'

# Find slow operations
grep '"duration_ms"' logs/chatterbox_extended.log | jq 'select(.data.duration_ms > 5000)'
```

#### Error Investigation
```bash
# Find recent errors
tail -n 1000 logs/chatterbox_extended.log | grep '"level":"ERROR"' | jq .

# Trace request that failed
REQUEST_ID="req_123"
grep "\"request_id\":\"$REQUEST_ID\"" logs/chatterbox_extended.log | jq .
```

## Production Best Practices

### Log Management

#### Log Rotation
- Configure log rotation to prevent disk space issues
- Default: 10MB max size, 5 backup files
- Consider daily rotation for high-volume deployments

#### Log Retention
- Keep logs for compliance and debugging needs
- Typical retention: 30-90 days
- Archive old logs to cheaper storage

#### Log Aggregation
- Use centralized logging in production
- Forward logs to ELK, Splunk, or cloud logging services
- Parse JSON logs for better searchability

### Monitoring Setup

#### Health Check Monitoring
```bash
# Nagios/Icinga check
curl -f http://localhost:7860/api/v1/health || exit 1

# Prometheus monitoring
curl -s http://localhost:7860/api/v1/metrics | \
  jq -r '.system.memory.percent' | \
  awk '{if($1>80) exit 1}'
```

#### Alerting Rules

**High Error Rate:**
- Trigger: Error rate > 5% over 5 minutes
- Action: Page on-call engineer

**High Memory Usage:**
- Trigger: Memory usage > 80%
- Action: Send warning notification

**Slow Response Times:**
- Trigger: Average response time > 10 seconds
- Action: Investigation required

### Performance Optimization

#### Log Level Configuration
- Use INFO level in production
- Use DEBUG only for troubleshooting
- Reduce log verbosity for high-volume endpoints

#### Metrics Collection
- Monitor metrics collection overhead
- Adjust collection intervals if needed
- Archive old metrics data regularly

### Security Considerations

#### Log Sanitization
- Sensitive data is automatically filtered from logs
- Request bodies are truncated for large content
- Personal information is not logged

#### Access Control
- Restrict access to log files
- Secure metrics endpoints in production
- Use authentication for sensitive monitoring data

## Appendix

### Log Message Reference

#### Application Lifecycle
- `"Starting Chatterbox TTS Extended Plus API"` - Application startup
- `"Models preloaded successfully"` - Model initialization complete
- `"Shutting down application"` - Application shutdown

#### TTS Operations
- `"Starting TTS generation for text: ..."` - TTS request started
- `"Using reference audio: ..."` - Reference audio file loaded
- `"TTS generation completed successfully"` - TTS request completed

#### VC Operations
- `"Starting VC generation: ... -> ..."` - VC request started
- `"Voice conversion: ... -> ..."` - VC processing started
- `"Voice conversion completed successfully"` - VC request completed

#### Error Messages
- `"Text cannot be empty"` - Validation error for empty text
- `"Audio file not found: ..."` - Resource error for missing audio
- `"TTS generation failed: ..."` - Generation error during TTS
- `"VC generation failed: ..."` - Generation error during VC

### Metrics Reference

#### Request Metrics
- `requests_total`: Total number of requests processed
- `requests_success`: Number of successful requests
- `requests_error`: Number of failed requests
- `success_rate`: Ratio of successful to total requests
- `error_rate`: Ratio of failed to total requests

#### Performance Metrics
- `average_processing_time`: Average processing time in milliseconds
- `processing_times`: Detailed processing time statistics
- `response_times`: Detailed API response time statistics

#### System Metrics
- `cpu_percent`: Current CPU usage percentage
- `memory.rss_mb`: Resident set size in megabytes
- `memory.percent`: Memory usage percentage
- `disk.free_gb`: Free disk space in gigabytes
- `disk.usage_percent`: Disk usage percentage

---

This documentation provides comprehensive coverage of the enhanced logging and monitoring capabilities. For additional support or questions, please refer to the main API documentation or deployment guide.
