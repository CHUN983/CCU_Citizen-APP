# 🏙️ Citizen Urban Planning Participation System

**市民參與城市規劃行動應用系統**

A complete backend API system enabling citizens to participate in urban planning through opinion submissions, voting, commenting, and collaborative decision-making.

## ✅ MVP Status: COMPLETE

All Phase 1 core requirements implemented:
- ✅ User authentication & authorization
- ✅ Opinion submission system
- ✅ Browsing & filtering
- ✅ Comment & vote system
- ✅ Admin moderation panel
- ✅ Notification system
- ✅ Complete API documentation

## 🚀 Quick Start

### Option 1: Using Helper Scripts (Recommended)

```bash
# 1. Setup environment
cp .env.example .env
# Edit .env with your MySQL credentials

# 2. Initialize database
./scripts/init_database.sh

# 3. Start server
./scripts/start_server.sh
```

### Option 2: Manual Setup

See detailed instructions in [docs/user/SETUP_GUIDE.md](docs/user/SETUP_GUIDE.md)

### Access the API

- **API Base**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/api/docs
- **Default Admin**: username: `admin`, password: `admin123`

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

## 📚 Documentation

- **[Setup Guide](docs/user/SETUP_GUIDE.md)** - Installation and configuration
- **[API Documentation](docs/api/API_DOCUMENTATION.md)** - Complete API reference
- **[Project Summary](docs/dev/PROJECT_SUMMARY.md)** - Architecture and technical details
- **[Interactive API Docs](http://localhost:8000/api/docs)** - Try the API in your browser

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python 3.9+)
- **Database**: MySQL 8.0+
- **Authentication**: JWT tokens with bcrypt
- **API Style**: RESTful
- **Documentation**: OpenAPI/Swagger

## 📊 Features

### For Citizens
- Register and manage account
- Submit opinions with location and categories
- Upload media (images, videos, audio) - schema ready
- Comment on other opinions
- Vote and bookmark opinions
- Receive notifications
- Track opinion status

### For Administrators
- Review and approve/reject submissions
- Merge similar opinions
- Moderate comments
- Update categories and tags
- View complete audit trail

## 🔐 Security

- JWT token authentication
- Bcrypt password hashing
- Role-based access control
- SQL injection prevention
- Input validation

## 📈 Project Statistics

- **27** Python files
- **~1,675** lines of code
- **13** database tables
- **20+** API endpoints
- **5** git commits
- **100%** MVP requirements met

## 🔜 Next Steps

1. **Frontend Development** - Build Android/iOS mobile apps
2. **Media Upload** - Implement file upload endpoints
3. **AI Integration** - Add NLP for automatic classification
4. **Analytics Dashboard** - Admin analytics and reporting
5. **Real-time Features** - WebSocket notifications

## 🤝 Contributing

This project follows the CLAUDE.md development guidelines:
- Search before creating new files
- Extend existing code rather than duplicating
- Single source of truth principle
- Commit after each completed task
- Automatic GitHub backup

## 📞 Support

- **GitHub**: https://github.com/CHUN983/CCU_Citizen-APP
- **Issues**: Report bugs or request features via GitHub Issues
- **Documentation**: Check docs/ directory

---

**🎯 Template by Chang Ho Chien | HC AI 說人話channel | v1.0.0**
**📺 Tutorial**: https://youtu.be/8Q1bRZaHH24
**💻 Built with Claude Code**
