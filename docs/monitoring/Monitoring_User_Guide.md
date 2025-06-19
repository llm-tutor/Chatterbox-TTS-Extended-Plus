# Monitoring and Logging - Quick Start User Guide

**Version:** 1.7.0  
**Target Audience:** System Administrators, DevOps Engineers, Developers  
**Prerequisites:** Chatterbox TTS Extended Plus API v1.7.0 or later

## Quick Start Checklist

✅ **Basic Setup** (5 minutes)
- [ ] Verify logging configuration
- [ ] Start application with monitoring enabled
- [ ] Test health check endpoint
- [ ] Verify log file creation

✅ **Monitoring Setup** (10 minutes)  
- [ ] Set up basic monitoring script
- [ ] Configure log analysis tools
- [ ] Test metrics collection
- [ ] Verify request tracing

✅ **Production Ready** (15 minutes)
- [ ] Configure log rotation
- [ ] Set up alerting rules
- [ ] Create monitoring dashboard
- [ ] Test error scenarios

## Step 1: Basic Setup (5 minutes)

### 1.1 Verify Configuration

Check your `config.yaml` file:

```yaml
server:
  log_level: "INFO"
  log_file_path: "logs/chatterbox_extended.log"

paths:
  logs_dir: "logs"
```

### 1.2 Start Application

```bash
# Start with monitoring enabled (default)
cd /path/to/Chatterbox-TTS-Extended-Plus
python main_api.py

# You should see JSON logs like:
# {"timestamp": "2025-06-19T15:33:07.088582+00:00", "level": "INFO", ...}
```

### 1.3 Test Health Check

```bash
# Basic health check
curl http://localhost:7860/api/v1/health

# Expected response:
{
  "status": "healthy",
  "models_loaded": {"tts": true, "vc": true},
  "version": "1.7.0",
  "uptime_seconds": 125.4,
  "metrics": { ... },
  "system_info": { ... }
}
```

### 1.4 Verify Log Files

```bash
# Check log directory exists
ls -la logs/

# Check log file content
tail -f logs/chatterbox_extended.log
```

## Step 2: Monitoring Setup (10 minutes)

### 2.1 Basic Monitoring Script

Create `monitor.sh`:

```bash
#!/bin/bash
# Basic monitoring script

LOG_FILE="monitoring_$(date +%Y%m%d_%H%M%S).log"

while true; do
    echo "=== $(date) ===" | tee -a $LOG_FILE
    
    # Health check
    HEALTH=$(curl -s http://localhost:7860/api/v1/health)
    echo "Health: $(echo $HEALTH | jq -r '.status')" | tee -a $LOG_FILE
    
    # System metrics
    echo "CPU: $(echo $HEALTH | jq -r '.system_info.cpu_percent')%" | tee -a $LOG_FILE
    echo "Memory: $(echo $HEALTH | jq -r '.system_info.memory.rss_mb')MB" | tee -a $LOG_FILE
    echo "Success Rate: $(echo $HEALTH | jq -r '.metrics.success_rate // 0')" | tee -a $LOG_FILE
    
    echo "" | tee -a $LOG_FILE
    sleep 30
done
```

Make it executable and run:
```bash
chmod +x monitor.sh
./monitor.sh
```

### 2.2 Log Analysis Setup

Create `analyze_logs.sh`:

```bash
#!/bin/bash
# Log analysis helper script

LOG_FILE="logs/chatterbox_extended.log"

echo "=== Log Analysis ==="
echo "Total log entries: $(wc -l < $LOG_FILE)"
echo "Error count: $(grep -c '"level":"ERROR"' $LOG_FILE)"
echo "Warning count: $(grep -c '"level":"WARNING"' $LOG_FILE)"
echo ""

echo "=== Recent Errors ==="
grep '"level":"ERROR"' $LOG_FILE | tail -5 | jq -r '.message'
echo ""

echo "=== Processing Times (last 10) ==="
grep '"duration_ms"' $LOG_FILE | tail -10 | jq -r '.data.duration_ms // .duration_ms'
echo ""

echo "=== Top Error Messages ==="
grep '"level":"ERROR"' $LOG_FILE | jq -r '.message' | sort | uniq -c | sort -nr | head -5
```

### 2.3 Test Metrics Collection

Make some API requests to generate metrics:

```bash
# Test TTS request
curl -X POST http://localhost:7860/api/v1/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "This is a test of the monitoring system"}'

# Check detailed metrics
curl http://localhost:7860/api/v1/metrics | jq '.performance'
```

### 2.4 Test Request Tracing

Make a request and trace it through the logs:

```bash
# Make a request and watch logs in real-time
tail -f logs/chatterbox_extended.log | jq 'select(.request_id != null)'
```

## Step 3: Production Ready Setup (15 minutes)

### 3.1 Configure Log Rotation

Create `/etc/logrotate.d/chatterbox-tts`:

```
/path/to/Chatterbox-TTS-Extended-Plus/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
}
```

Test log rotation:
```bash
sudo logrotate -d /etc/logrotate.d/chatterbox-tts
```

### 3.2 Set Up Alerting Rules

Create `alert_rules.sh`:

```bash
#!/bin/bash
# Simple alerting script

HEALTH_URL="http://localhost:7860/api/v1/health"
ALERT_EMAIL="admin@yourcompany.com"

# Check if service is responding
if ! curl -s -f $HEALTH_URL > /dev/null; then
    echo "ALERT: Chatterbox TTS API is not responding" | mail -s "Chatterbox TTS Alert" $ALERT_EMAIL
    exit 1
fi

# Get metrics
METRICS=$(curl -s $HEALTH_URL)
MEMORY_PCT=$(echo $METRICS | jq -r '.system_info.memory.percent // 0')
ERROR_RATE=$(echo $METRICS | jq -r '.metrics.error_rate // 0')

# Memory check (using awk instead of bc for compatibility)
if awk "BEGIN {exit !($MEMORY_PCT > 80)}"; then
    echo "ALERT: High memory usage: ${MEMORY_PCT}%" | mail -s "Chatterbox TTS Memory Alert" $ALERT_EMAIL
fi

# Error rate check  
if awk "BEGIN {exit !($ERROR_RATE > 0.05)}"; then
    echo "ALERT: High error rate: ${ERROR_RATE}" | mail -s "Chatterbox TTS Error Rate Alert" $ALERT_EMAIL
fi
```

Add to crontab:
```bash
# Check every 5 minutes
*/5 * * * * /path/to/alert_rules.sh
```

### 3.3 Test Error Scenarios

Test the monitoring system with intentional errors:

```bash
# Test with invalid request (should generate error)
curl -X POST http://localhost:7860/api/v1/tts \
  -H "Content-Type: application/json" \
  -d '{"text": ""}'  # Empty text should fail

# Test with missing file (should generate error)
curl -X POST http://localhost:7860/api/v1/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "test", "reference_audio_filename": "nonexistent.wav"}'

# Check error logs
grep '"level":"ERROR"' logs/chatterbox_extended.log | tail -2 | jq .
```

## Daily Operations

### Morning Checks (2 minutes)

```bash
# Quick health check
curl -s http://localhost:7860/api/v1/health | jq '{status, uptime_seconds, success_rate: .metrics.success_rate, memory_percent: .system_info.memory.percent}'

# Check for overnight errors
grep '"level":"ERROR"' logs/chatterbox_extended.log | grep $(date +%Y-%m-%d) | wc -l
```

### Weekly Maintenance (10 minutes)

```bash
# Analyze performance trends
./analyze_logs.sh

# Check disk usage
df -h logs/
du -sh logs/*

# Archive old logs if needed
find logs/ -name "*.log.*" -mtime +30 -exec gzip {} \;
```

### Troubleshooting Common Issues

#### High Memory Usage
```bash
# Check current memory
curl -s http://localhost:7860/api/v1/metrics | jq '.system.memory'

# Find memory-related logs
grep -i "memory\|cleanup" logs/chatterbox_extended.log | tail -10 | jq .
```

#### Slow Performance
```bash
# Check processing times
curl -s http://localhost:7860/api/v1/metrics | jq '.performance.processing_times'

# Find slow operations (> 5 seconds)
grep '"duration_ms"' logs/chatterbox_extended.log | jq 'select((.data.duration_ms // .duration_ms) > 5000)'
```

#### High Error Rate
```bash
# Check error distribution
grep '"level":"ERROR"' logs/chatterbox_extended.log | jq -r '.message' | sort | uniq -c | sort -nr

# Recent error details
grep '"level":"ERROR"' logs/chatterbox_extended.log | tail -5 | jq '{timestamp, message, data}'
```

## Essential Commands Reference

### Health Monitoring
```bash
# Quick status
curl -s http://localhost:7860/api/v1/health | jq '.status'

# System resources
curl -s http://localhost:7860/api/v1/health | jq '.system_info'

# Performance metrics
curl -s http://localhost:7860/api/v1/metrics | jq '.performance'
```

### Log Analysis
```bash
# Recent errors
grep '"level":"ERROR"' logs/chatterbox_extended.log | tail -10

# Request tracing
grep '"request_id":"YOUR_REQUEST_ID"' logs/chatterbox_extended.log

# Performance analysis
grep '"duration_ms"' logs/chatterbox_extended.log | jq '.data.duration_ms // .duration_ms'
```

### Metrics Queries
```bash
# Memory usage trend
curl -s http://localhost:7860/api/v1/health | jq '.system_info.memory.percent'

# Success rate
curl -s http://localhost:7860/api/v1/health | jq '.metrics.success_rate'

# Average processing time
curl -s http://localhost:7860/api/v1/health | jq '.metrics.average_processing_time'
```

---

**Next Steps:**
- For detailed technical information, see: `Logging_and_Monitoring_Guide.md`
- For production deployment, see: `Deployment_Guide.md`
- For API documentation, see: `API_Documentation.md`
