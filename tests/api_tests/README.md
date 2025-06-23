# API Documentation Examples Tests

This directory contains automated tests that validate all code examples in the reorganized API documentation work correctly with the current API implementation.

## Purpose

During the API documentation reorganization (Phase 1), we extracted all code examples from the monolithic documentation into organized files:
- `docs/api/schemas/examples/curl-examples.md`
- `docs/api/schemas/examples/python-examples.md`

These tests ensure that the examples in those files actually work against the running API server.

## Test Files

### Core Test Framework
- **`test_runner.py`** - Main test framework with server warm-up handling and reporting
- **`run_all_tests.py`** - Complete test suite runner

### Example Validation Tests  
- **`test_curl_examples.py`** - Tests cURL commands from documentation
- **`test_python_examples.py`** - Tests Python code examples from documentation

### Temporary Files
- **`temp_files/`** - Directory for test-generated audio files (auto-created, auto-cleaned)

## Running Tests

### Prerequisites
1. **API Server Running**: Ensure the API server is running on `http://localhost:7860`
   ```bash
   cd E:\Repos\Chatterbox-TTS-Extended-Plus
   .venv\Scripts\activate
   python main_api.py
   ```

2. **Virtual Environment**: Activate the project's virtual environment
   ```bash
   .venv\Scripts\activate
   ```

### Run All Tests
```bash
cd tests/api_tests
python run_all_tests.py
```

### Run Individual Test Suites
```bash
# Test only cURL examples
python test_curl_examples.py

# Test only Python examples
python test_python_examples.py
```

## Test Behavior

### Server Warm-up
- **First Request Delay**: Tests account for server reload by using extended timeout (30s) for the first request
- **Subsequent Requests**: Use normal timeout (15s) after server is warmed up

### File Handling
- **Temporary Files**: Generated in `temp_files/` directory
- **Auto Cleanup**: Test files are automatically removed after validation
- **Size Validation**: Ensures generated audio files are reasonable size (>1KB)

### Error Handling
- **Connection Issues**: Clear error messages if server is not running
- **Timeout Handling**: Appropriate timeouts for different operation types
- **Detailed Logging**: Timestamped logs with success/failure indicators

## Test Coverage

### cURL Examples Tests
- ✅ Health check endpoint
- ✅ Basic TTS generation (direct download)
- ✅ TTS with JSON response (legacy mode)
- ✅ Voice listing and search
- ✅ Generated files listing

### Python Examples Tests
- ✅ Basic health check function
- ✅ ChatterboxClient class functionality  
- ✅ Basic TTS generation
- ✅ TTS with voice cloning (if voices available)
- ✅ Voice listing with search
- ✅ Generated files listing

## Notes

These tests are part of the API documentation reorganization project and help ensure that our reorganized documentation maintains accuracy and usability.
