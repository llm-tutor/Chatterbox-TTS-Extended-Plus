# Development Documentation

This directory contains development and implementation documentation for the Chatterbox TTS Extended Plus project.

## 📁 Directory Structure

### **Active Development**
Documents for ongoing projects and foundational standards:

| Document | Purpose | Status |
|----------|---------|---------|
| **[implementation-protocols.md](implementation-protocols.md)** | Common protocols, guidelines, and testing procedures for all development projects | **Foundation** |

### **Pending Projects**
Future development plans in standby:

```
pending_api_plans/
├── openai_plan.md              # Phase 12: OpenAI Compatibility Layer
└── api_polish_and_documentation.md    # Phase 13: Polish & Production Features
```

### **Project Archives**
Completed projects organized by category:

```
archives/
├── api-implementation/          # Original API development (Phases 1-7)
├── api-docs-reorganization/     # API documentation restructuring  
├── fastapi-migration/          # FastAPI migration project (Phases 1-5)
├── refinement_plan/            # API refinement project (Phases 8-11)
├── two-tier-testing/           # Testing strategy implementation
└── utils-refactoring/          # Utils.py modular refactoring project
```

## 🔄 **Archival Workflow & Conventions**

### **When to Archive**
Projects are archived when:
- ✅ All implementation phases are completed
- ✅ Final testing and validation passed
- ✅ Documentation is complete and up-to-date
- ✅ Project commit is merged and tagged

### **Archive Organization**
1. **Directory Naming**: Use kebab-case matching the project focus
   - Example: `two-tier-testing`, `api-docs-reorganization`
2. **File Preservation**: All project files moved as-is to maintain history
3. **Documentation Links**: Update any active references to archived files

### **Active vs Archived vs Pending**
- **Active**: Root-level files for ongoing development
- **Foundation**: Core documents that support multiple projects (e.g., `implementation-protocols.md`)
- **Pending**: Future projects in `pending_api_plans/` - not active but reserved for future implementation
- **Archived**: Completed projects in organized subdirectories

### **Archive Contents**
Each project archive typically contains:
- **Strategy/Plan Documents**: Original design and planning files
- **Implementation Plans**: Detailed task tracking and progress
- **Resume Prompts**: Project-specific development guidelines
- **Research Files**: Analysis, performance data, and investigation results

## 📖 **For Developers**

### **Getting Started with Development**
1. **Read Foundation Documents**: Start with `implementation-protocols.md` for comprehensive development standards
2. **Active Projects**: Check root-level files for ongoing work
3. **Pending Projects**: Review `pending_api_plans/` for future work
4. **Historical Context**: Review archived projects for patterns and lessons learned
5. **Resume Development**: Use project-specific `*_resume_prompt.md` files when continuing work

### **Testing & Validation Standards**
- **Core Validation**: `python scripts/test_core_examples.py` (2-3 minutes, implementation protocol)
- **Comprehensive Testing**: `python scripts/test_curl_examples.py --timeout 90` (8-15 minutes, release quality)
- **Complete Documentation**: [`../../scripts/README.md`](../../scripts/README.md)

### **Project Lifecycle Pattern**
1. **Planning**: Create strategy and implementation plan documents
2. **Development**: Track progress with detailed task checklists
3. **Documentation**: Maintain resume prompts and guidelines
4. **Completion**: Full testing, documentation updates, commit
5. **Archival**: Move project files to `archives/[project-name]/`

## 🗂️ **Archived Projects Reference**

### **API Implementation** (`archives/api-implementation/`)
- **Scope**: Original API development (Phases 1-7)
- **Key Achievements**: FastAPI server, endpoints, error handling, resource management
- **Reference**: Complete implementation history and architecture decisions

### **API Documentation Reorganization** (`archives/api-docs-reorganization/`)
- **Scope**: Modular documentation structure implementation
- **Key Achievements**: Organized endpoint docs, improved navigation, validation scripts
- **Reference**: Documentation patterns and maintenance procedures

### **Two-Tier Testing Strategy** (`archives/two-tier-testing/`)
- **Scope**: Balanced testing approach implementation
- **Key Achievements**: Core validation (2-3 min), comprehensive testing (8-15 min), implementation protocols
- **Reference**: Testing patterns and validation procedures

### **FastAPI Migration** (`archives/fastapi-migration/`)
- **Scope**: Complete migration of Chatter.py functionality to FastAPI with full feature parity (Phases 1-5)
- **Key Achievements**: Parallel processing, Whisper validation system, dual backend support, post-processing pipeline, enhanced features, Unicode compatibility
- **Reference**: Complete implementation plan, analysis, and methodology documentation

### **Utils Refactoring** (`archives/utils-refactoring/`)
- **Scope**: Modular transformation of monolithic utils.py (2,391 lines → organized modules)
- **Key Achievements**: 29 functions migrated across 6 modules, 100% backward compatibility, zero breaking changes
- **Reference**: Modular architecture patterns and incremental migration strategies

### **API Refinement** (`archives/refinement_plan/`)
- **Scope**: Enhanced API features and user experience improvements (Phases 8-11)
- **Key Achievements**: Speed factor control, enhanced file naming, voice management, audio concatenation, streaming responses, file upload integration
- **Reference**: Advanced API feature patterns, performance optimization, and user experience design

## 🔮 **Pending Projects Reference**

### **OpenAI Compatibility** (`pending_api_plans/openai_plan.md`)
- **Scope**: Phase 12 - Broader ecosystem integration
- **Planned Features**: `/v1/audio/speech` endpoint, OpenAI parameter mapping, voice resolution system, client library compatibility
- **Focus**: Drop-in replacement capability for OpenAI TTS API

### **Polish & Production Features** (`pending_api_plans/api_polish_and_documentation.md`)
- **Scope**: Phase 13 - Production readiness and advanced features
- **Planned Features**: Advanced voice management, enhanced error handling, performance optimization, security validation
- **Focus**: Production deployment readiness and enterprise features

## 🔍 **Finding Information**

### **Current Development**
- **Active Projects**: Check root-level `*_implementation_plan.md` files (currently none - all complete)
- **Guidelines**: Use `*_resume_prompt.md` for project-specific protocols (archived)
- **Standards**: Reference `implementation-protocols.md` for common procedures

### **Historical Information**
- **Implementation History**: `archives/api-implementation/api-implementation_tracking.md`
- **Architecture Decisions**: Review implementation plan documents in archives
- **Performance Data**: Check `phase*.*` files for research and benchmarks
- **Lessons Learned**: Review completed project documentation patterns

### **Development Patterns**
- **Project Structure**: Examine archived projects for organizational patterns
- **Documentation Standards**: See how previous projects handled documentation
- **Testing Approaches**: Review testing evolution across projects
- **Workflow Evolution**: Track how development processes improved over time

## 📝 **Contributing to Documentation**

### **Adding New Projects**
1. Create project-specific implementation plan and resume prompt
2. Follow established naming conventions (kebab-case for archives)
3. Reference `implementation-protocols.md` for common standards
4. Document progress with detailed task tracking

### **Maintaining Archives**
1. **Preserve History**: Never delete or significantly modify archived files
2. **Update Links**: Ensure active documents properly reference archived content
3. **Cross-Reference**: Link related projects and shared patterns
4. **Documentation Quality**: Maintain clear README files in each archive

### **Future Archive Guidelines**
When archiving new completed projects:
1. Create `archives/[project-name]/` directory
2. Move all project-specific files maintaining their structure
3. Update this README with project reference
4. Verify and update any broken links in active documents
5. Add archive entry to project lifecycle tracking

### **Activating Pending Projects**
When starting work on pending projects:
1. Move relevant files from `pending_api_plans/` to root level
2. Create implementation plan and resume prompt documents
3. Update this README to reflect active status
4. Follow established development protocols

---

**Note**: This documentation structure supports the complete development lifecycle from pending through active development to historical preservation, enabling effective knowledge management and development continuity.
