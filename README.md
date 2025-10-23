# citizenApp

Multi-language citizen application project managed with Claude Code.

## Quick Start

1. **Read CLAUDE.md first** - Contains essential rules for Claude Code
2. Follow the pre-task compliance checklist before starting any work
3. Use proper module structure under `src/main/[language]/`
4. Commit after every completed task
5. Push to GitHub after every commit for backup

## Project Structure

**Multi-Language Standard Project** - Supports Python, JavaScript, Java, and more

```
citizenApp/
├── src/main/           # Source code by language
│   ├── python/         # Python components
│   ├── js/             # JavaScript components
│   ├── java/           # Java components
│   ├── shared/         # Shared resources
│   └── resources/      # Configuration and assets
├── src/test/           # Test code
├── docs/               # Documentation
├── tools/              # Development tools
├── examples/           # Usage examples
└── output/             # Generated files
```

## Development Guidelines

- **Always search first** before creating new files
- **Extend existing** functionality rather than duplicating
- **Use Task agents** for operations >30 seconds
- **Single source of truth** for all functionality
- **Language-agnostic structure** - works with Python, JS, Java, etc.
- **Commit frequently** - after each completed task
- **GitHub backup** - push after every commit

## Multi-Language Support

This project supports multiple programming languages:

- **Python**: `src/main/python/` - Python implementations
- **JavaScript**: `src/main/js/` - JavaScript/Node.js code
- **Java**: `src/main/java/` - Java implementations
- **Shared**: `src/main/shared/` - Cross-language resources

Each language directory follows consistent structure:
- `core/` - Core business logic
- `utils/` - Utility functions/classes
- `models/` - Data models
- `services/` - Service layer
- `api/` - API endpoints

## Getting Started

1. Choose your language directory under `src/main/`
2. Follow language-specific conventions
3. Use shared resources for cross-language functionality
4. Maintain consistent patterns across implementations

---

**🎯 Template by Chang Ho Chien | HC AI 說人話channel | v1.0.0**
**📺 Tutorial**: https://youtu.be/8Q1bRZaHH24
