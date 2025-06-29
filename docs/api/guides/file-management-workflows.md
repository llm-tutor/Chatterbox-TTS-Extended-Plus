# File Management Workflows

This guide demonstrates complete file management workflows using the Chatterbox TTS Extended Plus API. These workflows show how to organize, process, and manage audio files effectively using the API's comprehensive file management features.

## Overview

The API provides three main file management systems:

1. **TTS Outputs** - Generated audio files with project organization
2. **VC Inputs** - Source files for voice conversion with project organization  
3. **Voices** - Reference audio files with metadata and categorization

Each system supports:
- Organized folder structures
- Metadata management
- Search and filtering
- Bulk operations
- Complete cleanup

## TTS Output Management Workflow

### 1. Generate Audio in Projects

Organize generated content by creating audio files in project folders:

```bash
# Generate audio in organized project structure
curl -X POST "http://localhost:7860/api/v1/tts" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Chapter 1: The beginning of our story",
    "project": "audiobook/chapter1",
    "export_formats": ["wav", "mp3"],
    "temperature": 0.75
  }'
```

### 2. List and Browse Files

Browse generated files by project or search across all outputs:

```bash
# List all outputs
curl "http://localhost:7860/api/v1/outputs"

# List files in specific project
curl "http://localhost:7860/api/v1/outputs?project=audiobook"

# Search for specific content
curl "http://localhost:7860/api/v1/outputs?search=chapter"

# Get folder structure
curl "http://localhost:7860/api/v1/outputs/folders"
```

### 3. File Management and Cleanup

Manage individual files or entire project folders:

```bash
# Delete individual file
curl -X DELETE "http://localhost:7860/api/v1/output/filename.wav?confirm=true"

# Delete entire project folder and contents
curl -X DELETE "http://localhost:7860/api/v1/outputs?project=audiobook&confirm=true"
```

## VC Input Management Workflow

### 1. Upload and Organize

Upload source audio files with proper organization:

```bash
# Upload to project folder
curl -X POST "http://localhost:7860/api/v1/vc_input" \
  -F "vc_input_file=@interview.wav" \
  -F "project=podcast_project/raw_interviews" \
  -F "text=Raw interview recording for voice conversion"
```

### 2. Browse and Search

Find uploaded files across your organized structure:

```bash
# List all VC inputs
curl "http://localhost:7860/api/v1/vc_inputs"

# List by project
curl "http://localhost:7860/api/v1/vc_inputs?project=podcast_project"

# Search for specific files
curl "http://localhost:7860/api/v1/vc_inputs?search=interview"

# Get folder structure
curl "http://localhost:7860/api/v1/vc_inputs/folders"
```

### 3. Cleanup and Management

Remove files and folders when projects are complete:

```bash
# Delete single file
curl -X DELETE "http://localhost:7860/api/v1/vc_input/interview.wav?confirm=true"

# Delete project folder
curl -X DELETE "http://localhost:7860/api/v1/vc_inputs?project=podcast_project&confirm=true"
```

## Voice Management Workflow

### 1. Upload and Categorize

Upload voice files with rich metadata:

```bash
# Upload voice with full metadata
curl -X POST "http://localhost:7860/api/v1/voice" \
  -F "audio_file=@narrator_voice.wav" \
  -F "name=Professional Narrator" \
  -F "description=Authoritative voice for documentary narration" \
  -F "folder_path=documentary/narrators" \
  -F "tags=professional,narrator,documentary"
```

### 2. Browse and Search

Find voices by category, tags, or characteristics:

```bash
# List all voices
curl "http://localhost:7860/api/v1/voices"

# List by category
curl "http://localhost:7860/api/v1/voices?folder=documentary"

# Search by name or tags
curl "http://localhost:7860/api/v1/voices?search=narrator"
curl "http://localhost:7860/api/v1/voices?search=professional"

# Get voice categories
curl "http://localhost:7860/api/v1/voices/folders"
```

### 3. Voice Maintenance

Remove individual voices or entire categories:

```bash
# Delete single voice
curl -X DELETE "http://localhost:7860/api/v1/voice/narrator_voice.wav?confirm=true"

# Delete voice category
curl -X DELETE "http://localhost:7860/api/v1/voices?folder=documentary&confirm=true"
```

## Complete Project Workflow Example

Here's how to manage a complete audio project from start to finish:

### Step 1: Set Up Voice Assets

```bash
# Upload narrator voice
curl -X POST "http://localhost:7860/api/v1/voice" \
  -F "audio_file=@narrator.wav" \
  -F "name=Main Narrator" \
  -F "folder_path=project_alpha/voices" \
  -F "tags=narrator,main"

# Upload character voice
curl -X POST "http://localhost:7860/api/v1/voice" \
  -F "audio_file=@character.wav" \
  -F "name=Character Voice" \
  -F "folder_path=project_alpha/voices" \
  -F "tags=character,dialogue"
```

### Step 2: Generate Content

```bash
# Generate introduction
curl -X POST "http://localhost:7860/api/v1/tts" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Welcome to Project Alpha",
    "reference_audio_filename": "narrator.wav",
    "project": "project_alpha/episodes/intro",
    "export_formats": ["wav", "mp3"]
  }'

# Generate dialogue
curl -X POST "http://localhost:7860/api/v1/tts" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, this is the main character speaking",
    "reference_audio_filename": "character.wav", 
    "project": "project_alpha/episodes/dialogue",
    "export_formats": ["wav"]
  }'
```

### Step 3: Process External Audio

```bash
# Upload external interview
curl -X POST "http://localhost:7860/api/v1/vc_input" \
  -F "vc_input_file=@interview.wav" \
  -F "project=project_alpha/raw_audio" \
  -F "text=External interview for voice conversion"

# Convert to project voice
curl -X POST "http://localhost:7860/api/v1/vc" \
  -H "Content-Type: application/json" \
  -d '{
    "input_audio_source": "interview.wav",
    "target_voice_source": "narrator.wav",
    "export_formats": ["wav"]
  }'
```

### Step 4: Combine and Finalize

```bash
# List all project outputs
curl "http://localhost:7860/api/v1/outputs?project=project_alpha"

# Concatenate final episode
curl -X POST "http://localhost:7860/api/v1/concat" \
  -H "Content-Type: application/json" \
  -d '{
    "segments": ["intro_file.wav", "dialogue_file.wav", "converted_interview.wav"],
    "crossfade_ms": 100,
    "normalize_levels": true,
    "export_formats": ["wav", "mp3"]
  }'
```

### Step 5: Project Cleanup

```bash
# Review project structure
curl "http://localhost:7860/api/v1/outputs/folders"

# Clean up temporary files
curl -X DELETE "http://localhost:7860/api/v1/vc_inputs?project=project_alpha&confirm=true"

# Archive or clean project outputs
curl -X DELETE "http://localhost:7860/api/v1/outputs?project=project_alpha/raw&confirm=true"

# Preserve voices for future use (optional cleanup)
curl -X DELETE "http://localhost:7860/api/v1/voices?folder=project_alpha&confirm=true"
```

## Best Practices

### Organization Strategy

1. **Use Hierarchical Projects**: Organize with clear hierarchy
   - `project_name/content_type/specific_section`
   - `audiobook/chapters/chapter_01`
   - `podcast/season1/episode_03`

2. **Consistent Naming**: Use consistent file naming conventions
   - Include key parameters in filenames
   - Use descriptive folder names

3. **Metadata Management**: Use rich metadata for voices
   - Descriptive names and descriptions
   - Relevant tags for searchability
   - Organized folder structure

### Performance Tips

1. **Batch Operations**: Use bulk deletion for project cleanup
2. **Search Efficiency**: Use specific search terms
3. **Folder Structure**: Keep reasonable folder depth (2-4 levels)

### Workflow Automation

The integrated test scripts demonstrate these workflows:

- `scripts/test_integrated_tts_file_management.py`
- `scripts/test_integrated_vc_input_management.py`  
- `scripts/test_integrated_voice_management.py`

These scripts provide complete examples of automated file management workflows that can be adapted for production use.

## Troubleshooting

### Common Issues

1. **File Not Found**: Check exact filename and folder path
2. **Permission Errors**: Ensure `confirm=true` for deletions
3. **Search No Results**: Try broader search terms

### Recovery

1. **Accidental Deletion**: Check if files exist in other projects
2. **Folder Structure**: Use `/folders` endpoints to understand organization
3. **Cleanup Verification**: List files after bulk operations

For additional support, see the [Error Handling Guide](error-handling.md).
