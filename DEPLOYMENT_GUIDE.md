# EDU-EXPAND Deployment Guide

## Overview
This guide covers deploying EDU-EXPAND to production environments including AWS, Heroku, DigitalOcean, and traditional servers.

## Table of Contents
1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Environment Setup](#environment-setup)
3. [Database Preparation](#database-preparation)
4. [Static Files & Media](#static-files--media)
5. [Deployment Platforms](#deployment-platforms)
6. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Pre-Deployment Checklist

### Security
- [ ] Set `DEBUG=False` in production settings
- [ ] Generate strong `SECRET_KEY` (use Django secret key generator)
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Enable HTTPS/SSL certificates
- [ ] Set secure cookies: `SESSION_COOKIE_SECURE=True`
- [ ] Set CSRF cookie secure: `CSRF_COOKIE_SECURE=True`
- [ ] Enable HSTS: `SECURE_HSTS_SECONDS=31536000`
- [ ] Configure X-Frame-Options: `X_FRAME_OPTIONS='DENY'`
- [ ] Disable password reset if using corporate SSO
- [ ] Review permissions and role assignments

### Performance
- [ ] Configure caching (Redis recommended)
- [ ] Enable database connection pooling
- [ ] Optimize static files (minify CSS/JS)
- [ ] Configure CDN for static assets
- [ ] Set up database backups
- [ ] Configure log rotation

### Dependencies
- [ ] Review `requirements.txt` and remove dev packages for production
- [ ] Pin specific package versions
- [ ] Run security checks: `pip install safety && safety check`
- [ ] Update all packages: `pip list --outdated`

### Testing
- [ ] Run full test suite: `python manage.py test`
- [ ] Test scoring algorithm with production-like data
- [ ] Test email sending with SMTP settings
- [ ] Test CSV import with sample files
- [ ] Verify all admin features work
- [ ] Test user authentication (admin, commercial, client)

### Documentation
- [ ] Update README with production URLs
- [ ] Document email credentials (separate from code)
- [ ] Document admin procedures
- [ ] Create runbook for operations team
- [ ] Document backup and restore procedures

---

## Environment Setup

### Production .env Configuration

```bash
# Django Core
DEBUG=False
SECRET_KEY=your-super-secret-production-key-min-50-chars
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (PostgreSQL recommended)
DATABASE_ENGINE=postgresql
DATABASE_HOST=your-postgres-server.com
DATABASE_PORT=5432
DATABASE_NAME=edu_expand_prod
DATABASE_USER=postgres
DATABASE_PASSWORD=very-strong-password
DB_SSL_MODE=require

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com  # or your email service
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@yourdomain.com
EMAIL_HOST_PASSWORD=app-specific-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Cache
CACHE_BACKEND=django.core.cache.backends.redis.RedisCache
REDIS_URL=redis://your-redis-server:6379/0

# Celery (for async tasks)
CELERY_BROKER_URL=redis://your-redis-server:6379/1
CELERY_RESULT_BACKEND=redis://your-redis-server:6379/2
CELERY_ENABLED=True

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True

# Storage
STATIC_ROOT=/app/staticfiles
STATIC_URL=https://cdn.yourdomain.com/static/
MEDIA_ROOT=/app/media
MEDIA_URL=https://cdn.yourdomain.com/media/

# Monitoring
SENTRY_DSN=https://your-sentry-dsn@sentry.io/1234567
LOG_LEVEL=INFO
```

### Production Requirements
Create `requirements-prod.txt`:

```
Django==5.0.1
psycopg2-binary==2.9.9  # PostgreSQL driver
redis==5.0.1
celery==5.3.4
django-crispy-forms==2.1
crispy-bootstrap5==2.0.0
django-filter==23.5
python-decouple==3.8
Pillow==10.1.0
Gunicorn==21.2.0
WhiteNoise==6.6.0
sentry-sdk==1.39.1
django-storages==1.14.2  # For S3 storage
boto3==1.34.1  # For AWS S3
```

---

## Database Preparation

### PostgreSQL Setup

```bash
# Create database and user
createdb edu_expand_prod
createuser edu_expand_user
psql -c "ALTER USER edu_expand_user WITH PASSWORD 'strong-password';"
psql -c "ALTER ROLE edu_expand_user SET client_encoding TO 'utf8';"
psql -c "ALTER ROLE edu_expand_user SET default_transaction_isolation TO 'read committed';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE edu_expand_prod TO edu_expand_user;"
```

### Run Migrations

```bash
# On deployment server
python manage.py migrate --noinput

# Create superuser
python manage.py createsuperuser --noinput \
  --email admin@yourdomain.com \
  --username admin

# Set password separately
python manage.py shell
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(email='admin@yourdomain.com')
user.set_password('strong-password')
user.save()
exit()
```

### Backup Strategy

```bash
# Daily backup script (cron job)
#!/bin/bash
BACKUP_DIR=/backups/edu-expand
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -U postgres edu_expand_prod | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete
```

---

## Static Files & Media

### Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### AWS S3 Configuration (Optional)

```python
# settings.py
if ENVIRONMENT == 'production':
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
            "OPTIONS": {
                "bucket_name": "edu-expand-media",
                "region_name": "us-east-1",
            }
        },
        "staticfiles": {
            "BACKEND": "storages.backends.s3boto3.S3StaticStorage",
            "OPTIONS": {
                "bucket_name": "edu-expand-static",
                "region_name": "us-east-1",
            }
        }
    }
```

---

## Deployment Platforms

### 1. AWS EC2 Deployment

#### Architecture
```
Domain (Route 53)
    ↓
Load Balancer (ELB)
    ↓
EC2 Instance (Ubuntu 22.04)
    ├─ Django/Gunicorn
    ├─ Nginx (reverse proxy)
    ├─ PostgreSQL
    └─ Redis
    ↓
S3 (Static Files)
RDS (Database)
```

#### Steps

1. **Launch EC2 Instance**
```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-venv postgresql redis-server nginx git
```

2. **Setup Application**
```bash
# Clone repository
git clone https://github.com/your-org/edu-expand.git
cd edu-expand

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements-prod.txt

# Configure environment
nano .env  # Add production settings

# Run migrations
python manage.py migrate
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser
```

3. **Setup Gunicorn**
```bash
# Create systemd service
sudo nano /etc/systemd/system/edu-expand.service

[Unit]
Description=EDU-EXPAND Django Application
After=network.target

[Service]
Type=notify
User=ubuntu
WorkingDirectory=/home/ubuntu/edu-expand
Environment="PATH=/home/ubuntu/edu-expand/venv/bin"
ExecStart=/home/ubuntu/edu-expand/venv/bin/gunicorn \
    --workers 4 \
    --bind unix:/run/gunicorn.sock \
    edu_expand.wsgi:application

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable edu-expand
sudo systemctl start edu-expand
```

4. **Configure Nginx**
```bash
sudo nano /etc/nginx/sites-available/edu-expand

upstream edu_expand {
    server unix:/run/gunicorn.sock;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    client_max_body_size 20M;

    location /static/ {
        alias /home/ubuntu/edu-expand/staticfiles/;
    }

    location /media/ {
        alias /home/ubuntu/edu-expand/media/;
    }

    location / {
        proxy_pass http://edu_expand;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/edu-expand /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

5. **Setup SSL/TLS**
```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Generate certificate
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

### 2. Heroku Deployment

#### Setup
```bash
# Create Procfile
echo "web: gunicorn edu_expand.wsgi --log-file -" > Procfile

# Create runtime.txt
echo "python-3.11.8" > runtime.txt

# Create heroku app
heroku create your-app-name

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Add Redis
heroku addons:create heroku-redis:premium-0

# Set environment variables
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=your-secret-key
heroku config:set ALLOWED_HOSTS=your-app.herokuapp.com

# Deploy
git push heroku main

# Run migrations
heroku run python manage.py migrate

# Create superuser
heroku run python manage.py createsuperuser
```

### 3. DigitalOcean App Platform

Create `app.yaml`:
```yaml
name: edu-expand
services:
- name: web
  github:
    repo: your-org/edu-expand
    branch: main
  build_command: pip install -r requirements-prod.txt && python manage.py collectstatic --noinput
  run_command: gunicorn edu_expand.wsgi:application
  envs:
  - key: DEBUG
    value: "False"
  - key: SECRET_KEY
    value: ${SECRET_KEY}
databases:
- name: postgres
  engine: PG
  version: "14"
- name: redis
  engine: REDIS
  version: "7"
```

---

## Monitoring & Maintenance

### Logging
```python
# settings.py production logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/edu-expand/django.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}
```

### Error Tracking
```python
# settings.py
import sentry_sdk
sentry_sdk.init(
    dsn=env('SENTRY_DSN'),
    traces_sample_rate=0.1,
    environment="production"
)
```

### Health Checks
```bash
# Create healthcheck endpoint
# urls.py
path('health/', views.HealthCheckView.as_view(), name='health_check'),
```

### Monitoring Commands
```bash
# Check database integrity
python manage.py dbshell < integrity_check.sql

# Monitor Celery tasks
celery -A edu_expand inspect active

# Check Redis connection
redis-cli ping

# Monitor system resources
top
free -h
df -h
```

### Scheduled Maintenance
```bash
# Weekly database optimization
VACUUM ANALYZE;

# Monthly cleanup of old logs
python manage.py cleanupsessions

# Quarterly security updates
pip list --outdated
```

---

## Troubleshooting

### Deployment Issues

**Issue: Static files not showing**
```bash
python manage.py collectstatic --clear --noinput
```

**Issue: Database connection errors**
```bash
# Verify PostgreSQL is running
sudo systemctl status postgresql

# Check connection string
psql -h localhost -U user -d database
```

**Issue: Email not sending**
```bash
# Test SMTP in Django shell
python manage.py shell
from django.core.mail import send_mail
send_mail('Test', 'Hello', 'from@example.com', ['to@example.com'])
```

**Issue: High memory usage**
```bash
# Reduce Gunicorn workers
--workers 2

# Increase swap space
sudo fallocate -l 2G /swapfile
```

---

## Performance Optimization

### Database
```bash
# Add indexes for common queries
CREATE INDEX idx_prospect_owner ON crm_prospect(owner_id);
CREATE INDEX idx_prospect_stage ON crm_prospect(stage);
CREATE INDEX idx_prospect_country ON crm_prospect(country);
```

### Caching
```python
# Cache prospect list
from django.views.decorators.cache import cache_page

@cache_page(60 * 5)  # 5 minutes
def prospect_list(request):
    ...
```

### Query Optimization
```python
# Use select_related and prefetch_related
prospects = Prospect.objects.select_related('owner').prefetch_related('interactions')
```

---

## Scaling Considerations

### Horizontal Scaling
- Add load balancer (ELB, HAProxy)
- Run multiple Gunicorn instances
- Use managed database (RDS)
- Use managed Redis (ElastiCache)

### Vertical Scaling
- Increase instance size
- Configure database connection pooling
- Implement query caching

### Asynchronous Tasks
```bash
# Scale Celery workers
celery -A edu_expand worker -c 4
```

---

## Support & Backup

### Emergency Contact
- Ops Team: ops@yourdomain.com
- On-Call: Check PagerDuty

### Backup Verification
```bash
# Test restore
dropdb test_edu_expand
createdb test_edu_expand
gunzip --stdout backup_20240315.sql.gz | psql test_edu_expand
```

### Disaster Recovery
- [Insert RTO/RPO requirements]
- [Insert backup locations]
- [Insert restore procedure]
