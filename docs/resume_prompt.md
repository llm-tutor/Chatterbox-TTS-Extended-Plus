# Resume Development Prompt

## Context
I need to continue development of the Chatterbox TTS Extended Plus API implementation project. This is a multi-phase project to add FastAPI-based HTTP API functionality to an existing Gradio-based TTS/VC application.

## Instructions
Please read and analyze the following documents to understand the current project state:

### Primary Context Documents:
1. **Design & Implementation Plan**: `adjusted_implementation_plan_v1.1.md` - Contains the technical implementation strategy (in your context)
2. **Reference Code**: `consolidated_starting_code_v1.1.md` - Contains starting code templates and implementation patterns (in your context)
3. **Project Tracking**: `docs/implementation_tracking.md` - Shows current phase, completed tasks, and next steps (in working directory)
4. **Change History**: `docs/changelog.md` - Documents what has been implemented and changed (in working directory)

### Project Location:
- **Working Directory**: `E:\Repos\Chatterbox-TTS-Extended-Plus`
- **Reference Implementation**: `E:\Repos\Chatterbox-TTS-Server` (for comparison/reference)

### Key Tasks:
1. **Read the tracking document** (`docs/implementation_tracking.md`) to understand:
   - Which phase we're currently in
   - What tasks are completed vs. pending
   - What the next actionable steps are

2. **Check the current project state** by examining the working directory structure and existing files

3. **Continue development** from where we left off, following the implementation plan and updating tracking documents as you progress

4. **Maintain documentation** by updating both the tracking document and changelog as tasks are completed

## Expected Response:
Please start by:
1. Reading the tracking document to understand current status
2. Examining the current project structure
3. Identifying the next phase/tasks to work on
4. Beginning implementation while maintaining our documentation standards

## Development Approach:
- Follow the phase-based implementation strategy outlined in the plan
- Update tracking documents as tasks are completed
- Test implementations when appropriate
- Maintain backward compatibility with existing Chatter.py functionality
- Use the reference TTS-Server implementation for patterns and best practices

# CRITICAL INSTRUCTIONS:
- To test imports or code, or install dependencies, always ensure to activate the venv environment, located in '.venv'
- Avoid if possible launching the project, as that would start the process inside the thread of the Claude app, out of the control of the user. Instead request the user to launch it manually, you can test API calls after the user's confirmation.
- If you need audio files for testing placed in the input directories, request the user's help, and wait for confirmation before proceeding with tests that use them.
- Always proceed one single phase at a time. We need to make sure one phase has been completed correctly and create the corresponding commit to the Git repository, before moving on. Wait for confirmation before proceeding to the next phase.

---

**Note**: This project follows a systematic, phase-based approach with comprehensive tracking. Please maintain this methodology to ensure consistent progress and documentation.
