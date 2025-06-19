# Monitoring Troubleshooting Reference Card

**Quick Reference for Chatterbox TTS Extended Plus v1.7.0**

## Emergency Commands

### Service Status
```bash
# Is the service running?
curl -f http://localhost:7860/api/v1/health || echo "SERVICE DOWN"

# Quick system check
curl -s http://localhost:7860/api/v1/health | jq '{status, memory: .system_info.memory.percent, errors: .metrics.error_rate}'
```

### Critical Issues

#### Service Not Responding
```bash
# Check if process is running
ps aux | grep main_api.py

# Check port binding
netstat -tlnp | grep 7860

# Check recent logs
tail -50 logs/chatterbox_extended.log | grep ERROR
```

#### High Memory Usage (>80%)
```bash
# Current memory usage
curl -s http://localhost:7860/api/v1/health | jq '.system_info.memory'

# Force cleanup (if available)
curl -X POST http://localhost:7860/api/v1/admin/cleanup

# Restart service
sudo systemctl restart chatterbox-tts
```

#### High Error Rate (>5%)
```bash
# Recent error summary
grep '"level":"ERROR"' logs/chatterbox_extended.log | tail -10 | jq -r '.message' | sort | uniq -c

# Find problematic requests
grep '"level":"ERROR"' logs/chatterbox_extended.log | jq 'select(.timestamp > "2025-06-19T14:00:00")'
```

## Log File Locations

- **Main Log:** `logs/chatterbox_extended.log`
- **Rotated Logs:** `logs/chatterbox_extended.log.1`, `.2`, etc.
- **System Logs:** `/var/log/syslog` (if using systemd)

## Monitoring Endpoints

- **Health Check:** `GET http://localhost:7860/api/v1/health`
- **Detailed Metrics:** `GET http://localhost:7860/api/v1/metrics`
- **Voice List:** `GET http://localhost:7860/api/v1/voices`

## Log Analysis Patterns

### Find Request by ID
```bash
grep '"request_id":"REQUEST_ID_HERE"' logs/chatterbox_extended.log | jq .
```

### Performance Issues
```bash
# Slow operations (>10 seconds)
grep '"duration_ms"' logs/chatterbox_extended.log | jq 'select((.data.duration_ms // .duration_ms) > 10000)'

# Average processing time today
grep '"duration_ms"' logs/chatterbox_extended.log | grep $(date +%Y-%m-%d) | jq -r '.data.duration_ms // .duration_ms' | awk '{sum+=$1} END {print "Average:", sum/NR, "ms"}'
```

### Error Patterns
```bash
# Most common errors
grep '"level":"ERROR"' logs/chatterbox_extended.log | jq -r '.message' | sort | uniq -c | sort -nr | head -5

# Errors by hour
grep '"level":"ERROR"' logs/chatterbox_extended.log | jq -r '.timestamp' | cut -c1-13 | uniq -c
```

## Alert Thresholds

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| Memory Usage | >70% | >85% | Restart service |
| Error Rate | >2% | >5% | Check logs |
| Response Time | >5s | >10s | Check performance |
| Disk Space | <5GB | <1GB | Archive logs |

## Contact Information

- **Documentation:** `docs/Logging_and_Monitoring_Guide.md`
- **User Guide:** `docs/Monitoring_User_Guide.md`
- **API Docs:** `docs/API_Documentation.md`

---
*Keep this reference card accessible for quick troubleshooting*
