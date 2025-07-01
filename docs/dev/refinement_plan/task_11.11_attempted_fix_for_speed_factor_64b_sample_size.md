**Situation:** When we use speed_factor in tts generation, we obtain 64 bit sample size wav files. The system pipeline requires 32 bit sample size for many operations. It would be ideal that from generation, even when we use speed_factor alteration, we end up with usable 32 bit sample size files.

We tried a first fix, but it failed.

**Reverted:** Attempted fix for speed factor (generated 32 bits sample size files)

We tried to alter the speed_factor generation with the following, as to obtain a resulting wav file with 32 bits sample size directly after the stretch processing.

Technically, this solution was perfect. We were obtaining files at the desired sample size. But in real terms, the solution turned out to be useless: A massive amount of artifacts/bad audio quality makes the resulting wav files unusable.


This was the implementation that was tested, and then reverted to the previous one.
utils/audio/processing.py - line 121

```python
        try:
            # Write input audio to temp file with explicit 32-bit float format
            # This ensures audiostretchy processes 32-bit audio and maintains consistency
            if audio_np.ndim == 2:
                sf.write(temp_input_path, audio_np.T, sample_rate, subtype='FLOAT')  # Transpose for soundfile, 32-bit float
            else:
                sf.write(temp_input_path, audio_np, sample_rate, subtype='FLOAT')  # 32-bit float
            
            # Process with audiostretchy (TDHS)
            stretch_audio(temp_input_path, temp_output_path, ratio=ratio)
            
            # Read processed result with explicit dtype handling
            processed_audio, _ = sf.read(temp_output_path, dtype='float32')
            
            # Handle channel dimensions correctly
            if audio_np.ndim == 2 and processed_audio.ndim == 2:
                processed_audio = processed_audio.T  # Transpose back
            elif audio_np.ndim == 2 and processed_audio.ndim == 1:
                processed_audio = processed_audio[np.newaxis, :]  # Add channel dimension
            elif audio_np.ndim == 1 and processed_audio.ndim == 2:
                processed_audio = processed_audio[:, 0]  # Take first channel
            
            # Ensure the output is float32 (additional safety check)
            processed_audio = processed_audio.astype(np.float32)
            logger.debug(f"audiostretchy processing complete: {processed_audio.dtype}, shape: {processed_audio.shape}")
            
        finally:
```

**Alternative solution**: Maybe we could try different ways of implementing the above. Maybe the problem is not from forcing audiostretchy to work with 32 bits, but from force-saving the resulting output in that configuration.

If that is so, maybe we should let the system to save the file, but with a suffix like `_64bit_ss`. Then, before returning we could do the following:

- Open the new file `*_64bit_ss.wav`.
- Convert it to 32bits sample size, and save it as `*.wav`
- Let the rest of the process continue: Generate the alternative formats from the 32bits wav, return the requested format as stream or the json, depending of the `response_mode` value.

The place to do this (saving as 64 bit and converting to a new file in 32 bits) would probably be:

`def apply_speed_factor_post_processing` at 'core_engine.py', line 855 to 909

Now, we have already a normalizing function, that transform an input in 64 bits sample size, to an audio segment with 32 bit sample size. This forms part of the v1/concat processing pipeline:

In the file `utils/audio/analysis.py`, the function `normalize_audio_format`, lines 11 to 59, does that effectively. Check it out to see if we can use it.

NOTE: Maybe this is a solution that could be even used in `utils/audio/processing.py` instead of the other solution, instead of saving 64bits, opening it, and generating other file in 32bits. In a way does that, by creating a temporal file with the fix, and loading the audio to be returned from that temp file.

Explore options and suggest what approach seems the best to try first.
