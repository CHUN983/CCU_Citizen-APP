# Configuration Files

## Database Setup

1. Create MySQL database:
```sql
CREATE DATABASE citizen_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. Run schema.sql to initialize tables:
```bash
mysql -u root -p citizen_app < schema.sql
```

Or use the Python init script:
```bash
python -m src.main.python.utils.database
```

## Environment Variables

Copy `.env.example` to `.env` and update with your settings:
```bash
cp .env.example .env
```

Required variables:
- DB_HOST: MySQL host (default: localhost)
- DB_PORT: MySQL port (default: 3306)
- DB_USER: MySQL username
- DB_PASSWORD: MySQL password
- DB_NAME: Database name (default: citizen_app)
- JWT_SECRET_KEY: Secret key for JWT tokens (change in production!)
