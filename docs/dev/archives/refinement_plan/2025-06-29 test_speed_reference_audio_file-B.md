# TTS Reference Audio File Performance Test Results

**Test Date:** 2025-06-29 13:05:05
**API Endpoint:** http://127.0.0.1:7860

## Test Configuration

- **Speed Factors:** 0.85x, 0.95x, 1.05x
- **Reference Audio Files:** 4 different files

### Test Text Used:

"Second test: The quick brown fox jumps over the lazy dog, displaying the grace of nature's eternal dance."

### Reference Audio Files:

- **alt_voice:** speaker_en/Jamie01.mp3
- **native_voice:** speaker_en/jamie_vc_to_david-2.wav
- **non_native_voice:** speaker_en/DAVID-2.mp3
- **linda_johnson:** test_voices/linda_johnson_01.wav

## Results Summary

### Speed Factor: 0.85x

| Reference File | Duration | Status |
|----------------|----------|--------|
| alt_voice | 27.49s | ✅ Success |
| native_voice | 20.33s | ✅ Success |
| non_native_voice | 21.85s | ✅ Success |
| linda_johnson | 28.90s | ✅ Success |

### Speed Factor: 0.95x

| Reference File | Duration | Status |
|----------------|----------|--------|
| alt_voice | 20.40s | ✅ Success |
| native_voice | 19.81s | ✅ Success |
| non_native_voice | 22.92s | ✅ Success |
| linda_johnson | 32.94s | ✅ Success |

### Speed Factor: 1.05x

| Reference File | Duration | Status |
|----------------|----------|--------|
| alt_voice | 24.20s | ✅ Success |
| native_voice | 20.26s | ✅ Success |
| non_native_voice | 26.07s | ✅ Success |
| linda_johnson | 33.30s | ✅ Success |

## Performance Comparison Across All Speed Factors

| Reference File | 0.85x | 0.95x | 1.05x | Average |
|----------------|-------|-------|-------|---------|
| alt_voice | 27.49s | 20.40s | 24.20s | **24.03s** |
| native_voice | 20.33s | 19.81s | 20.26s | **20.14s** |
| non_native_voice | 21.85s | 22.92s | 26.07s | **23.61s** |
| linda_johnson | 28.90s | 32.94s | 33.30s | **31.71s** |

## Detailed Results

### Speed Factor 0.85x - Detailed Results

- **alt_voice:** ✅ 27.49s - Success (JSON)
- **native_voice:** ✅ 20.33s - Success (JSON)
- **non_native_voice:** ✅ 21.85s - Success (JSON)
- **linda_johnson:** ✅ 28.90s - Success (JSON)

### Speed Factor 0.95x - Detailed Results

- **alt_voice:** ✅ 20.40s - Success (JSON)
- **native_voice:** ✅ 19.81s - Success (JSON)
- **non_native_voice:** ✅ 22.92s - Success (JSON)
- **linda_johnson:** ✅ 32.94s - Success (JSON)

### Speed Factor 1.05x - Detailed Results

- **alt_voice:** ✅ 24.20s - Success (JSON)
- **native_voice:** ✅ 20.26s - Success (JSON)
- **non_native_voice:** ✅ 26.07s - Success (JSON)
- **linda_johnson:** ✅ 33.30s - Success (JSON)
