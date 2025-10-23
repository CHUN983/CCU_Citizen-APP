# Setup Guide - Citizen Urban Planning Participation System

## Prerequisites

- Python 3.9 or higher
- MySQL 8.0 or higher
- pip (Python package manager)

## Installation Steps

### 1. Clone the Repository

```bash
cd /root/project/citizenApp
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup MySQL Database

Create a new MySQL database:

```sql
CREATE DATABASE citizen_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your database credentials:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=citizen_app
JWT_SECRET_KEY=your-strong-secret-key-here
```

### 6. Initialize Database Schema

Run the schema initialization:

```bash
mysql -u root -p citizen_app < src/main/resources/config/schema.sql
```

Or use Python:

```bash
python -m src.main.python.utils.database
```

### 7. Start the API Server

```bash
# Development server
python -m uvicorn src.main.python.core.app:app --reload --host 0.0.0.0 --port 8000

# Or using the shortcut
python src/main/python/core/app.py
```

### 8. Access the API

- **API Base**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs
- **ReDoc Documentation**: http://localhost:8000/api/redoc

## Default Admin Account

After database initialization, a default admin account is created:

- **Username**: `admin`
- **Password**: `admin123`

**⚠️ IMPORTANT**: Change this password immediately in production!

## Testing the API

### 1. Register a New User

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Test User"
  }'
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

Save the `access_token` from the response.

### 3. Create an Opinion

```bash
curl -X POST "http://localhost:8000/opinions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "title": "Need more parking spaces",
    "content": "We need more parking spaces in the downtown area",
    "category_id": 1,
    "status": "draft"
  }'
```

### 4. Get Opinions

```bash
curl -X GET "http://localhost:8000/opinions?page=1&page_size=20"
```

## Development

### Project Structure

```
citizenApp/
├── src/main/python/
│   ├── api/              # API route handlers
│   ├── core/             # Application core
│   ├── models/           # Pydantic models
│   ├── services/         # Business logic
│   └── utils/            # Utilities (database, security)
├── src/main/resources/
│   └── config/           # Configuration files
├── docs/                 # Documentation
├── requirements.txt      # Python dependencies
└── .env                  # Environment variables
```

### Running Tests

```bash
pytest src/test/
```

### Code Style

Follow PEP 8 guidelines. Use tools like:

```bash
# Format code
black src/

# Lint code
flake8 src/

# Type checking
mypy src/
```

## Troubleshooting

### Database Connection Error

- Verify MySQL is running
- Check database credentials in `.env`
- Ensure database `citizen_app` exists

### Import Errors

- Activate virtual environment
- Install all requirements: `pip install -r requirements.txt`

### Port Already in Use

Change the port in the start command:

```bash
uvicorn src.main.python.core.app:app --port 8001
```

## Next Steps

1. Read the [API Documentation](../api/API_DOCUMENTATION.md)
2. Explore the interactive API docs at http://localhost:8000/api/docs
3. Start building your frontend application
4. Configure production settings (CORS, security, etc.)

## Production Deployment

Before deploying to production:

1. ✅ Change default admin password
2. ✅ Set strong JWT_SECRET_KEY
3. ✅ Configure CORS properly
4. ✅ Use environment-specific configuration
5. ✅ Set up HTTPS/SSL
6. ✅ Configure database backups
7. ✅ Set up logging and monitoring
8. ✅ Use a production ASGI server (gunicorn + uvicorn)
