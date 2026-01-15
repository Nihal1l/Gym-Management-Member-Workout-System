# Deployment Guide

## Table of Contents
1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Heroku Deployment](#heroku-deployment)
4. [AWS EC2 Deployment](#aws-ec2-deployment)
5. [Environment Configuration](#environment-configuration)

## Local Development

### Quick Start
```bash
# 1. Clone repository
git clone <repo-url>
cd gym-management-system

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate on Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment
cp .env.example .env
# Edit .env if needed

# 5. Run migrations
python manage.py migrate

# 6. Create test data
python manage.py create_test_data

# 7. Run server
python manage.py runserver
```

Access: `http://localhost:8000/api/v1/`

## Docker Deployment

### Using Docker Compose (Recommended for Development)

```bash
# 1. Build and start containers
docker-compose up --build

# 2. Access services
# API: http://localhost:8000
# Admin: http://localhost:8000/admin
# Database: localhost:5432
```

### Dockerfile Explanation
- **Build Stage**: Installs dependencies in a builder image
- **Final Stage**: Uses only the application code and dependencies
- **Database**: PostgreSQL 15
- **Web Server**: Gunicorn on port 8000
- **Volumes**: Persistent storage for media and static files

### Manual Docker Deployment

```bash
# 1. Build image
docker build -t gym-api:latest .

# 2. Create network
docker network create gym-network

# 3. Run PostgreSQL
docker run -d \
  --name gym-db \
  --network gym-network \
  -e POSTGRES_DB=gym_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=secure_password \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:15

# 4. Run Django App
docker run -d \
  --name gym-api \
  --network gym-network \
  -p 8000:8000 \
  -e DEBUG=False \
  -e SECRET_KEY=your-secret-key \
  -e DB_HOST=gym-db \
  -e DB_NAME=gym_db \
  -e DB_USER=postgres \
  -e DB_PASSWORD=secure_password \
  gym-api:latest
```

## Heroku Deployment

### Prerequisites
- Heroku CLI installed
- GitHub repository

### Deployment Steps

```bash
# 1. Login to Heroku
heroku login

# 2. Create Heroku app
heroku create your-app-name

# 3. Add PostgreSQL add-on
heroku addons:create heroku-postgresql:hobby-dev

# 4. Set environment variables
heroku config:set SECRET_KEY=your-secret-key-change-this
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com

# 5. Deploy code
git push heroku main

# 6. Run migrations
heroku run python manage.py migrate

# 7. Create test data
heroku run python manage.py create_test_data

# 8. View logs
heroku logs --tail
```

### Create Procfile

Create `Procfile` in project root:
```
web: gunicorn gym_management.wsgi
release: python manage.py migrate
```

## AWS EC2 Deployment

### Prerequisites
- EC2 instance running Ubuntu 22.04 LTS
- Security groups allowing HTTP (80), HTTPS (443), SSH (22)
- Domain name (optional, for HTTPS)

### Step 1: Setup EC2 Instance

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.11 python3.11-venv python3-pip \
  postgresql postgresql-contrib nginx git supervisor

# Create app directory
sudo mkdir -p /var/www/gym-api
sudo chown -R $USER:$USER /var/www/gym-api
cd /var/www/gym-api
```

### Step 2: Clone and Setup Application

```bash
# Clone repository
git clone <repo-url> .

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt gunicorn whitenoise
```

### Step 3: Configure Environment

```bash
# Create .env file
cp .env.example .env

# Edit .env with production values
nano .env
```

```env
SECRET_KEY=your-very-secure-random-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,your-ip-address

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=gym_db
DB_USER=gym_user
DB_PASSWORD=secure_db_password
DB_HOST=localhost
DB_PORT=5432
```

### Step 4: Setup PostgreSQL

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE gym_db;
CREATE USER gym_user WITH PASSWORD 'secure_db_password';
ALTER ROLE gym_user SET client_encoding TO 'utf8';
ALTER ROLE gym_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE gym_user SET default_transaction_deferrable TO on;
ALTER ROLE gym_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE gym_db TO gym_user;
\q
```

### Step 5: Run Django Migrations

```bash
source venv/bin/activate
python manage.py migrate
python manage.py create_test_data
python manage.py collectstatic --noinput
```

### Step 6: Setup Gunicorn

Create `/var/www/gym-api/gunicorn_config.py`:
```python
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
```

Test Gunicorn:
```bash
gunicorn -c gunicorn_config.py gym_management.wsgi
```

### Step 7: Setup Supervisor

Create `/etc/supervisor/conf.d/gym-api.conf`:
```ini
[program:gym-api]
directory=/var/www/gym-api
command=/var/www/gym-api/venv/bin/gunicorn -c /var/www/gym-api/gunicorn_config.py gym_management.wsgi
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/gym-api.log
environment=PATH="/var/www/gym-api/venv/bin"
```

```bash
# Register and start
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start gym-api
sudo supervisorctl status
```

### Step 8: Setup Nginx Reverse Proxy

Create `/etc/nginx/sites-available/gym-api`:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location /static/ {
        alias /var/www/gym-api/staticfiles/;
    }

    location /media/ {
        alias /var/www/gym-api/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 90;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/gym-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 9: Setup HTTPS with Let's Encrypt (Optional)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Generate certificate
sudo certbot certonly --nginx -d your-domain.com -d www.your-domain.com

# Update Nginx to use HTTPS
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

## Environment Configuration

### Required Environment Variables

```env
# Django Core
SECRET_KEY=<random-secure-key>
DEBUG=False
ALLOWED_HOSTS=example.com,www.example.com

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=gym_db
DB_USER=gym_user
DB_PASSWORD=<secure-password>
DB_HOST=localhost
DB_PORT=5432

# JWT
JWT_SECRET_KEY=<jwt-secret>

# CORS
CORS_ALLOWED_ORIGINS=https://your-frontend.com

# AWS (if using S3 for media)
USE_S3=True
AWS_ACCESS_KEY_ID=<key>
AWS_SECRET_ACCESS_KEY=<secret>
AWS_STORAGE_BUCKET_NAME=<bucket>
```

## Monitoring & Maintenance

### View Logs
```bash
# Supervisor logs
sudo tail -f /var/log/gym-api.log

# Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Database logs
sudo -u postgres psql -d gym_db -c "SELECT * FROM activity_log LIMIT 10;"
```

### Database Backup

```bash
# Backup database
pg_dump -U gym_user -d gym_db > backup.sql

# Restore from backup
psql -U gym_user -d gym_db < backup.sql
```

### Update Application

```bash
cd /var/www/gym-api
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo supervisorctl restart gym-api
```

## Performance Optimization

### Database Query Optimization
- Use `select_related()` for ForeignKeys
- Use `prefetch_related()` for reverse relations
- Add database indexes (already configured in models)

### Caching
```python
# Add to settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### Static Files
```bash
# Collect static files
python manage.py collectstatic --noinput

# Serve with CDN for production
# Update STATIC_URL to CDN URL in settings.py
```

## Security Checklist

- [ ] Change all default passwords
- [ ] Set `DEBUG=False` in production
- [ ] Use strong `SECRET_KEY`
- [ ] Enable HTTPS/SSL
- [ ] Configure firewall
- [ ] Regular backups
- [ ] Monitor logs
- [ ] Update dependencies
- [ ] Use environment variables for secrets
- [ ] Enable Django security middleware

---

For additional support, consult Django, Gunicorn, and Nginx documentation.
