#!/bin/bash
# test_monitoring_setup.sh - Validate monitoring configuration

echo "========================================="
echo "Chatterbox TTS Monitoring Setup Test"
echo "Version: 1.7.0"
echo "========================================="
echo ""

PASSED=0
TOTAL=0
BASE_URL="http://localhost:7860"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

test_result() {
    local test_name="$1"
    local result="$2"
    local message="$3"
    
    ((TOTAL++))
    
    if [ "$result" -eq 0 ]; then
        echo -e "[${GREEN}PASS${NC}] $test_name"
        ((PASSED++))
    else
        echo -e "[${RED}FAIL${NC}] $test_name - $message"
    fi
}

# Test 1: Check if service is running
echo "Testing service availability..."
curl -s -f "$BASE_URL/api/v1/health" > /dev/null 2>&1
test_result "Service Health Check" $? "Service not responding at $BASE_URL"

# Test 2: Check log directory exists
echo "Testing log configuration..."
[ -d "logs" ]
test_result "Log Directory Exists" $? "logs/ directory not found"

# Test 3: Check log file exists
[ -f "logs/chatterbox_extended.log" ]
test_result "Log File Exists" $? "logs/chatterbox_extended.log not found"

# Test 4: Check log file has recent entries
if [ -f "logs/chatterbox_extended.log" ]; then
    # Check if log has entries from today
    grep "$(date +%Y-%m-%d)" logs/chatterbox_extended.log > /dev/null 2>&1
    test_result "Recent Log Entries" $? "No recent log entries found"
fi

# Test 5: Check JSON log format
if [ -f "logs/chatterbox_extended.log" ]; then
    # Check if logs are in JSON format
    tail -1 logs/chatterbox_extended.log | jq . > /dev/null 2>&1
    test_result "JSON Log Format" $? "Logs are not in valid JSON format"
fi

# Test 6: Test health endpoint response
echo "Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s "$BASE_URL/api/v1/health" 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "$HEALTH_RESPONSE" | jq . > /dev/null 2>&1
    test_result "Health Endpoint JSON" $? "Health endpoint not returning valid JSON"
    
    # Check required fields
    echo "$HEALTH_RESPONSE" | jq -e '.status' > /dev/null 2>&1
    test_result "Health Status Field" $? "Health response missing 'status' field"
    
    echo "$HEALTH_RESPONSE" | jq -e '.metrics' > /dev/null 2>&1
    test_result "Health Metrics Field" $? "Health response missing 'metrics' field"
    
    echo "$HEALTH_RESPONSE" | jq -e '.system_info' > /dev/null 2>&1
    test_result "Health System Info Field" $? "Health response missing 'system_info' field"
fi

# Test 7: Test metrics endpoint
echo "Testing metrics endpoint..."
curl -s -f "$BASE_URL/api/v1/metrics" > /dev/null 2>&1
test_result "Metrics Endpoint" $? "Metrics endpoint not responding"

# Test 8: Test request tracing
echo "Testing request tracing..."
# Make a test request and check if it appears in logs
TEST_START_TIME=$(date -u +"%Y-%m-%dT%H:%M:%S")
curl -s "$BASE_URL/api/v1/health" > /dev/null 2>&1

# Wait a moment for logs to be written
sleep 2

# Check if request appears in logs
if [ -f "logs/chatterbox_extended.log" ]; then
    grep "Request started.*GET.*health" logs/chatterbox_extended.log | tail -1 > /dev/null 2>&1
    test_result "Request Tracing" $? "Request tracing not working - no request logs found"
fi

# Test 9: Generate test TTS request with monitoring
echo "Testing TTS request monitoring..."
TTS_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/tts" \
    -H "Content-Type: application/json" \
    -d '{"text": "Monitoring test"}' 2>/dev/null)

if [ $? -eq 0 ]; then
    echo "$TTS_RESPONSE" | jq . > /dev/null 2>&1
    test_result "TTS Request Processing" $? "TTS request failed or returned invalid JSON"
    
    # Check if TTS operation appears in logs
    sleep 2
    if [ -f "logs/chatterbox_extended.log" ]; then
        grep "tts_generation" logs/chatterbox_extended.log | tail -1 > /dev/null 2>&1
        test_result "TTS Operation Logging" $? "TTS operations not being logged"
    fi
else
    test_result "TTS Request Processing" 1 "TTS endpoint not responding"
fi

# Summary
echo ""
echo "========================================="
echo "Test Summary: $PASSED/$TOTAL tests passed"

if [ $PASSED -eq $TOTAL ]; then
    echo -e "${GREEN}✓ All monitoring tests passed!${NC}"
    echo "Your monitoring setup is working correctly."
    exit 0
else
    echo -e "${RED}✗ Some tests failed.${NC}"
    echo ""
    echo "Common solutions:"
    echo "1. Make sure the application is running: python main_api.py"
    echo "2. Check the logs directory exists and is writable"
    echo "3. Verify config.yaml has correct logging settings"
    echo "4. Check for any error messages in the logs"
    echo ""
    echo "For detailed troubleshooting, see:"
    echo "- docs/Monitoring_User_Guide.md"
    echo "- docs/Monitoring_Reference_Card.md"
    exit 1
fi
