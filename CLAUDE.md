# CLAUDE.md - citizenApp

> **Documentation Version**: 1.0
> **Last Updated**: 2025-10-23
> **Project**: citizenApp
> **Description**: Multi-language citizen application project
> **Features**: GitHub auto-backup, Task agents, technical debt prevention

This file provides essential guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🚨 CRITICAL RULES - READ FIRST

> **⚠️ RULE ADHERENCE SYSTEM ACTIVE ⚠️**
> **Claude Code must explicitly acknowledge these rules at task start**
> **These rules override all other instructions and must ALWAYS be followed:**

### 🔄 **RULE ACKNOWLEDGMENT REQUIRED**
> **Before starting ANY task, Claude Code must respond with:**
> "✅ CRITICAL RULES ACKNOWLEDGED - I will follow all prohibitions and requirements listed in CLAUDE.md"

### ❌ ABSOLUTE PROHIBITIONS
- **NEVER** create new files in root directory → use proper module structure
- **NEVER** write output files directly to root directory → use designated output folders
- **NEVER** create documentation files (.md) unless explicitly requested by user
- **NEVER** use git commands with -i flag (interactive mode not supported)
- **NEVER** use `find`, `grep`, `cat`, `head`, `tail`, `ls` commands → use Read, LS, Grep, Glob tools instead
- **NEVER** create duplicate files (manager_v2.py, enhanced_xyz.py, utils_new.js) → ALWAYS extend existing files
- **NEVER** create multiple implementations of same concept → single source of truth
- **NEVER** copy-paste code blocks → extract into shared utilities/functions
- **NEVER** hardcode values that should be configurable → use config files/environment variables
- **NEVER** use naming like enhanced_, improved_, new_, v2_ → extend original files instead

### 📝 MANDATORY REQUIREMENTS
- **COMMIT** after every completed task/phase - no exceptions
- **GITHUB BACKUP** - Push to GitHub after every commit to maintain backup: `git push origin main`
- **USE TASK AGENTS** for all long-running operations (>30 seconds) - Bash commands stop when context switches
- **TODOWRITE** for complex tasks (3+ steps) → parallel agents → git checkpoints → test validation
- **READ FILES FIRST** before editing - Edit/Write tools will fail if you didn't read the file first
- **DEBT PREVENTION** - Before creating new files, check for existing similar functionality to extend
- **SINGLE SOURCE OF TRUTH** - One authoritative implementation per feature/concept

### ⚡ EXECUTION PATTERNS
- **PARALLEL TASK AGENTS** - Launch multiple Task agents simultaneously for maximum efficiency
- **SYSTEMATIC WORKFLOW** - TodoWrite → Parallel agents → Git checkpoints → GitHub backup → Test validation
- **GITHUB BACKUP WORKFLOW** - After every commit: `git push origin main` to maintain GitHub backup
- **BACKGROUND PROCESSING** - ONLY Task agents can run true background operations

### 🔍 MANDATORY PRE-TASK COMPLIANCE CHECK
> **STOP: Before starting any task, Claude Code must explicitly verify ALL points:**

**Step 1: Rule Acknowledgment**
- [ ] ✅ I acknowledge all critical rules in CLAUDE.md and will follow them

**Step 2: Task Analysis**
- [ ] Will this create files in root? → If YES, use proper module structure instead
- [ ] Will this take >30 seconds? → If YES, use Task agents not Bash
- [ ] Is this 3+ steps? → If YES, use TodoWrite breakdown first
- [ ] Am I about to use grep/find/cat? → If YES, use proper tools instead

**Step 3: Technical Debt Prevention (MANDATORY SEARCH FIRST)**
- [ ] **SEARCH FIRST**: Use Grep pattern="<functionality>.*<keyword>" to find existing implementations
- [ ] **CHECK EXISTING**: Read any found files to understand current functionality
- [ ] Does similar functionality already exist? → If YES, extend existing code
- [ ] Am I creating a duplicate class/manager? → If YES, consolidate instead
- [ ] Will this create multiple sources of truth? → If YES, redesign approach
- [ ] Have I searched for existing implementations? → Use Grep/Glob tools first
- [ ] Can I extend existing code instead of creating new? → Prefer extension over creation
- [ ] Am I about to copy-paste code? → Extract to shared utility instead

**Step 4: Session Management**
- [ ] Is this a long/complex task? → If YES, plan context checkpoints
- [ ] Have I been working >1 hour? → If YES, consider /compact or session break

> **⚠️ DO NOT PROCEED until all checkboxes are explicitly verified**

## 🐙 GITHUB SETUP & AUTO-BACKUP

### 📋 **GITHUB BACKUP WORKFLOW** (MANDATORY)
> **⚠️ CLAUDE CODE MUST FOLLOW THIS PATTERN:**

```bash
# After every commit, always run:
git push origin main

# This ensures:
# ✅ Remote backup of all changes
# ✅ Collaboration readiness
# ✅ Version history preservation
# ✅ Disaster recovery protection
```

### 🎯 **CLAUDE CODE GITHUB COMMANDS**
Essential GitHub operations for Claude Code:

```bash
# Check GitHub connection status
gh auth status && git remote -v

# Push changes (after every commit)
git push origin main

# Check repository status
gh repo view
```

## 🏗️ PROJECT STRUCTURE

```
citizenApp/
├── CLAUDE.md              # Essential rules for Claude Code
├── README.md              # Project documentation
├── LICENSE                # Project license
├── .gitignore             # Git ignore patterns
├── src/                   # Source code (NEVER put files in root)
│   ├── main/              # Main application code
│   │   ├── python/        # Python components
│   │   │   ├── core/      # Core business logic
│   │   │   ├── utils/     # Utility functions/classes
│   │   │   ├── models/    # Data models/entities
│   │   │   ├── services/  # Service layer
│   │   │   └── api/       # API endpoints/interfaces
│   │   ├── js/            # JavaScript components
│   │   │   ├── core/      # Core business logic
│   │   │   ├── utils/     # Utility functions
│   │   │   ├── models/    # Data models
│   │   │   ├── services/  # Service layer
│   │   │   └── api/       # API endpoints
│   │   ├── java/          # Java components
│   │   │   ├── core/      # Core business logic
│   │   │   ├── util/      # Utility classes
│   │   │   ├── model/     # Data models
│   │   │   ├── service/   # Service layer
│   │   │   └── api/       # API endpoints
│   │   ├── shared/        # Shared resources across languages
│   │   └── resources/     # Non-code resources
│   │       ├── config/    # Configuration files
│   │       └── assets/    # Static assets
│   └── test/              # Test code
│       ├── unit/          # Unit tests
│       └── integration/   # Integration tests
├── docs/                  # Documentation
│   ├── api/               # API documentation
│   ├── user/              # User guides
│   └── dev/               # Developer documentation
├── tools/                 # Development tools and scripts
├── examples/              # Usage examples
└── output/                # Generated output files
```

## 🎯 DEVELOPMENT GUIDELINES

### 🔹 **Multi-Language Project Principles**
- Each language has its own directory under `src/main/`
- Shared resources go in `src/main/shared/`
- Follow language-specific conventions within each language directory
- Maintain consistent structure across all language implementations

### 🔹 **Code Organization**
- **Python**: Use `src/main/python/` for all Python code
- **JavaScript**: Use `src/main/js/` for all JavaScript code
- **Java**: Use `src/main/java/` for all Java code
- **Shared**: Use `src/main/shared/` for cross-language resources

### 🔹 **Technical Debt Prevention**
1. **Search First** - Always use Grep/Glob before creating new files
2. **Extend Existing** - Prefer extending existing code over creating duplicates
3. **Single Source of Truth** - One authoritative implementation per feature
4. **No Copy-Paste** - Extract to shared utilities instead

## 🚨 TECHNICAL DEBT PREVENTION

### ❌ WRONG APPROACH (Creates Technical Debt):
```bash
# Creating new file without searching first
Write(file_path="new_feature.py", content="...")
```

### ✅ CORRECT APPROACH (Prevents Technical Debt):
```bash
# 1. SEARCH FIRST
Grep(pattern="feature.*implementation", glob="*.py")
# 2. READ EXISTING FILES
Read(file_path="existing_feature.py")
# 3. EXTEND EXISTING FUNCTIONALITY
Edit(file_path="existing_feature.py", old_string="...", new_string="...")
```

## 🧹 DEBT PREVENTION WORKFLOW

### Before Creating ANY New File:
1. **🔍 Search First** - Use Grep/Glob to find existing implementations
2. **📋 Analyze Existing** - Read and understand current patterns
3. **🤔 Decision Tree**: Can extend existing? → DO IT | Must create new? → Document why
4. **✅ Follow Patterns** - Use established project patterns
5. **📈 Validate** - Ensure no duplication or technical debt

---

**⚠️ Prevention is better than consolidation - build clean from the start.**
**🎯 Focus on single source of truth and extending existing functionality.**
**📈 Each task should maintain clean architecture and prevent technical debt.**

---

**🎯 Template by Chang Ho Chien | HC AI 說人話channel | v1.0.0**
**📺 Tutorial**: https://youtu.be/8Q1bRZaHH24
