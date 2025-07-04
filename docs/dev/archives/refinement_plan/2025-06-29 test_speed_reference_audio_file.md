# TTS Reference Audio File Performance Test Results

**Test Date:** 2025-06-29 10:15:03
**API Endpoint:** http://127.0.0.1:7860

## Test Configuration

- **Speed Factors:** 0.85x, 0.95x, 1.05x
- **Reference Audio Files:** 4 different files

### Test Text Used:

"The quick brown fox jumps over the lazy dog, demonstrating agility and grace in nature's eternal dance."

### Reference Audio Files:

- **alt_voice:** speaker_en/Jamie01.mp3 - Length: 16s
- **native_voice:** speaker_en/jamie_vc_to_david-2.wav - Length: 20s
- **non_native_voice:** speaker_en/DAVID-2.mp3 - Length: 1m 23s
- **linda_johnson:** test_voices/linda_johnson_01.mp3 - Length: 49s

## Results Summary

### Speed Factor: 0.85x

| Reference File | Duration | Status |
|----------------|----------|--------|
| alt_voice | 56.56s | ✅ Success |
| native_voice | 59.12s | ✅ Success |
| non_native_voice | 71.31s | ✅ Success |
| linda_johnson | 132.58s | ✅ Success |

### Speed Factor: 0.95x

| Reference File | Duration | Status |
|----------------|----------|--------|
| alt_voice | 63.62s | ✅ Success |
| native_voice | 65.64s | ✅ Success |
| non_native_voice | 93.82s | ✅ Success |
| linda_johnson | 130.45s | ✅ Success |

### Speed Factor: 1.05x

| Reference File | Duration | Status |
|----------------|----------|--------|
| alt_voice | 69.42s | ✅ Success |
| native_voice | 64.01s | ✅ Success |
| non_native_voice | 88.48s | ✅ Success |
| linda_johnson | 148.20s | ✅ Success |

## Performance Comparison Across All Speed Factors

| Reference File | 0.85x | 0.95x | 1.05x | Average |
|----------------|-------|-------|-------|---------|
| alt_voice | 56.56s | 63.62s | 69.42s | **63.20s** |
| native_voice | 59.12s | 65.64s | 64.01s | **62.92s** |
| non_native_voice | 71.31s | 93.82s | 88.48s | **84.54s** |
| linda_johnson | 132.58s | 130.45s | 148.20s | **137.08s** |

## Detailed Results

### Speed Factor 0.85x - Detailed Results

- **alt_voice:** ✅ 56.56s - Success (JSON)
- **native_voice:** ✅ 59.12s - Success (JSON)
- **non_native_voice:** ✅ 71.31s - Success (JSON)
- **linda_johnson:** ✅ 132.58s - Success (JSON)

### Speed Factor 0.95x - Detailed Results

- **alt_voice:** ✅ 63.62s - Success (JSON)
- **native_voice:** ✅ 65.64s - Success (JSON)
- **non_native_voice:** ✅ 93.82s - Success (JSON)
- **linda_johnson:** ✅ 130.45s - Success (JSON)

### Speed Factor 1.05x - Detailed Results

- **alt_voice:** ✅ 69.42s - Success (JSON)
- **native_voice:** ✅ 64.01s - Success (JSON)
- **non_native_voice:** ✅ 88.48s - Success (JSON)
- **linda_johnson:** ✅ 148.20s - Success (JSON)
