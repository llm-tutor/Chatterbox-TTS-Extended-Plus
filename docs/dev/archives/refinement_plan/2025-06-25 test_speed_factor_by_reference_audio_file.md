# TTS Reference Audio File Performance Test Results

**Test Date:** 2025-06-28 17:49:01
**API Endpoint:** http://127.0.0.1:7860

## Test Configuration

- **Speed Factors:** 0.85x, 0.95x, 1.05x
- **Reference Audio Files:** 3 different files

### Test Text Used:

"The quick brown fox jumps over the lazy dog, demonstrating agility and grace in nature's eternal dance."

### Reference Audio Files:

- **male_voice:** speaker_en/Jamie01.mp3
- **female_voice:** speaker_en/DAVID-2.mp3
- **linda_johnson:** test_voices/linda_johnson_01.mp3

## Results Summary

### Speed Factor: 0.85x

| Reference File | Duration | Status |
|----------------|----------|--------|
| male_voice | 84.31s | ✅ Success |
| female_voice | 99.03s | ✅ Success |
| linda_johnson | 216.43s | ✅ Success |

### Speed Factor: 0.95x

| Reference File | Duration | Status |
|----------------|----------|--------|
| male_voice | 68.07s | ✅ Success |
| female_voice | 97.33s | ✅ Success |
| linda_johnson | 145.36s | ✅ Success |

### Speed Factor: 1.05x

| Reference File | Duration | Status |
|----------------|----------|--------|
| male_voice | 97.07s | ✅ Success |
| female_voice | 100.61s | ✅ Success |
| linda_johnson | 182.94s | ✅ Success |

## Performance Comparison Across All Speed Factors

| Reference File | 0.85x | 0.95x | 1.05x | Average |
|----------------|-------|-------|-------|---------|
| male_voice | 84.31s | 68.07s | 97.07s | **83.15s** |
| female_voice | 99.03s | 97.33s | 100.61s | **98.99s** |
| linda_johnson | 216.43s | 145.36s | 182.94s | **181.58s** |

## Detailed Results

### Speed Factor 0.85x - Detailed Results

- **male_voice:** ✅ 84.31s - Success (JSON)
- **female_voice:** ✅ 99.03s - Success (JSON)
- **linda_johnson:** ✅ 216.43s - Success (JSON)

### Speed Factor 0.95x - Detailed Results

- **male_voice:** ✅ 68.07s - Success (JSON)
- **female_voice:** ✅ 97.33s - Success (JSON)
- **linda_johnson:** ✅ 145.36s - Success (JSON)

### Speed Factor 1.05x - Detailed Results

- **male_voice:** ✅ 97.07s - Success (JSON)
- **female_voice:** ✅ 100.61s - Success (JSON)
- **linda_johnson:** ✅ 182.94s - Success (JSON)
