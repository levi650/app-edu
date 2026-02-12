# EDU-EXPAND Troubleshooting Guide

## Common Issues & Solutions

---

## 1. Installation & Setup Issues

### Problem: "ModuleNotFoundError: No module named 'django'"

**Cause:** Django not installed or virtual environment not activated

**Solution:**
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Verify Django is installed
python -c "import django; print(django.__version__)"
```

---

### Problem: "No such file or directory: 'db.sqlite3'"

**Cause:** Database not created/migrations not run

**Solution:**
```bash
# Create database and tables
python manage.py migrate

# Verify database created
ls -la db.sqlite3  # or check in File Explorer on Windows
```

---

### Problem: ".env file not found"

**Cause:** Missing environment configuration file

**Solution:**
```bash
# Copy example to actual .env file
cp .env.example .env

# Edit .env with your settings
nano .env  # or use any text editor

# On Windows
copy .env.example .env
```

---

### Problem: "SECRET_KEY is invalid" or "SECRET_KEY too short"

**Cause:** .env file has invalid SECRET_KEY

**Solution:**
```bash
# Generate new secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Update .env file
# Find: SECRET_KEY=
# Replace with: SECRET_KEY=<generated_key_above>
```

---

## 2. Database Issues

### Problem: "ProgrammingError: relation 'crm_prospect' does not exist"

**Cause:** Migrations not applied to database

**Solution:**
```bash
# Check migration status
python manage.py showmigrations

# Apply all pending migrations
python manage.py migrate

# Verify migration status
python manage.py showmigrations --list
```

---

### Problem: "Database locked" error

**Cause:** Another process has SQLite database open (development only)

**Solution:**
```bash
# Stop any running servers
# CTRL+C in terminal

# Delete database and rebuild (development only)
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo

# Restart server
python manage.py runserver
```

---

### Problem: "Connection refused" when using PostgreSQL

**Cause:** PostgreSQL server not running or wrong credentials

**Solution:**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql  # Linux
# or
pg_ctl status  # Mac/Windows with postgresql service

# Start PostgreSQL
sudo systemctl start postgresql  # Linux
pg_ctl start -D /usr/local/var/postgres  # Mac

# Verify connection string in .env
# Format: DATABASE_HOST=localhost DATABASE_PORT=5432 DATABASE_NAME=edu_expand

# Test connection
psql -h localhost -U postgres -d edu_expand
```

---

### Problem: "column 'owner_id' does not exist"

**Cause:** Foreign key migration not applied

**Solution:**
```bash
# List pending migrations
python manage.py showmigrations accounts

# Check if user_client migration is applied
python manage.py showmigrations accounts

# If not, apply it
python manage.py migrate accounts

# If already applied, check database
python manage.py dbshell
# SELECT name FROM sqlite_master WHERE type='table';
```

---

## 3. Server & Runtime Issues

### Problem: "Address already in use" when starting server

**Cause:** Another process using port 8000

**Solution:**
```bash
# Use different port
python manage.py runserver 8001

# Or kill the process using port 8000
# Linux/Mac
lsof -i :8000
kill -9 <PID>

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

---

### Problem: Server crashes with "TemplateDoesNotExist"

**Cause:** Template file missing or incorrect path

**Solution:**
```bash
# Check TEMPLATES setting in settings.py
# Ensure 'DIRS' includes correct path to templates

# Verify template file exists
ls -R templates/  # Linux/Mac
dir /s templates\  # Windows

# Common template paths:
# - templates/base.html
# - templates/crm/prospect_list.html
# - templates/accounts/admin_login.html
```

---

### Problem: "The STATIC_ROOT setting points to a directory that does not exist"

**Cause:** Static files not collected

**Solution:**
```bash
# Collect static files
python manage.py collectstatic --noinput

# Verify staticfiles directory created
ls -la staticfiles/  # Linux/Mac
dir staticfiles\  # Windows
```

---

### Problem: "Module 'crm.models' has no attribute 'get_score_breakdown'"

**Cause:** Scoring module not imported or function typo

**Solution:**
```python
# Correct import
from crm.scoring import calculate_score, get_score_breakdown

# Check function exists in crm/scoring.py
# Function signatures should be:
# def calculate_score(prospect):
# def get_score_breakdown(prospect):
```

---

## 4. Authentication & Permission Issues

### Problem: "Cannot create superuser - email required"

**Cause:** Custom User model requires email field

**Solution:**
```bash
# When creating superuser, provide email
python manage.py createsuperuser
# Email: admin@example.com
# Password: (enter password)
```

---

### Problem: "Login fails with correct credentials"

**Cause:** Cache issue or corrupted session

**Solution:**
```bash
# Clear session cache
python manage.py cleanupsessions

# Create superuser again
python manage.py createsuperuser

# Try login at:
# http://localhost:8000/accounts/admin-portal/login/
```

---

### Problem: "403 Forbidden - Permission Denied"

**Cause:** User role doesn't have required permission

**Solution:**
```bash
# Check user role
python manage.py shell
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(email='your@email.com')
print(user.get_role_display())  # Should show: Admin/Commercial/Client

# Change role if needed
user.role = User.ADMIN
user.save()
exit()
```

---

### Problem: "Client portal shows 'Access Denied'"

**Cause:** Client user logged in but not associated with a Client organization

**Solution:**
```python
# In Django shell
from django.contrib.auth import get_user_model
from crm.models import Client

User = get_user_model()
client_user = User.objects.get(email='client@example.com')

# Check if client is assigned
print(client_user.client)  # Should show Client object

# If None, assign a client
client = Client.objects.first()  # Get any client
client_user.client = client
client_user.save()
```

---

## 5. Email Configuration Issues

### Problem: "SMTPAuthenticationError - invalid email or password"

**Cause:** Wrong email credentials in .env

**Solution:**
```bash
# For Gmail, use App Password (not regular password)
# 1. Enable 2-factor authentication
# 2. Go to myaccount.google.com/apppasswords
# 3. Generate app-specific password
# 4. Update .env:
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=app-specific-password-here
```

---

### Problem: "SMTPNotSupportedError - SMTP requires a secure connection"

**Cause:** TLS not enabled for SMTP

**Solution:**
```bash
# Update .env to enable TLS
EMAIL_USE_TLS=True
EMAIL_PORT=587  # TLS port

# NOT 25 or 465 (which use different auth methods)
```

---

### Problem: "Email sending fails but no error message"

**Cause:** EMAIL_BACKEND set to console backend

**Solution:**
```bash
# In .env, check EMAIL_BACKEND
# For development (prints to console):
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# For production (actually sends):
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
```

---

### Problem: "Test email doesn't send when importing prospects"

**Cause:** Celery not running (async emails require Celery)

**Solution:**
```bash
# For now, emails are sent synchronously during import
# If using Celery:
celery -A edu_expand worker -l info

# Or disable async:
CELERY_ENABLED=False  # in .env
```

---

## 6. Data & Import Issues

### Problem: "CSV import shows '0 imported' despite uploading file"

**Cause:** CSV file has missing required columns

**Solution:**
```bash
# Required CSV columns:
# - name
# - email
# - country
# - contact_name
# - contact_role

# Check your CSV file has these columns
# Optional columns:
# - phone, city, type_of_establishment, budget, website, linkedin_url, notes

# Example: 
# name,email,country,contact_name,contact_role
# "University of Lagos","info@unilag.edu.ng","NG","Prof Smith","Director"
```

---

### Problem: "CSV import fails with encoding error"

**Cause:** File encoding not UTF-8

**Solution:**
```bash
# Save CSV as UTF-8 encoding
# In Excel: File → Save As → CSV UTF-8 (.csv)
# Or use conversion:
iconv -f ISO-8859-1 -t UTF-8 input.csv > output.csv
```

---

### Problem: "Duplicate prospects created on import"

**Cause:** No deduplication by email address

**Solution:**
```python
# Current import deduplicates by email
# If same email imported twice, second one skipped

# To merge duplicates:
python manage.py shell
from crm.models import Prospect
dupes = Prospect.objects.values('email').annotate(count=Count('id')).filter(count__gt=1)
# Manually merge or delete duplicates
```

---

## 7. Data Integrity Issues

### Problem: "Prospect score not updating after interaction added"

**Cause:** Score is not automatically recalculated

**Solution:**
```bash
# Recalculate score manually
python manage.py shell
from crm.models import Prospect
prospect = Prospect.objects.get(id=1)
prospect.recalculate_score()
prospect.save()

# Or recalculate all
for p in Prospect.objects.all():
    p.recalculate_score()
    p.save()
```

---

### Problem: "Interaction doesn't appear in prospect detail"

**Cause:** Interaction created for wrong prospect

**Solution:**
```python
# Check interaction relationship
python manage.py shell
from crm.models import Prospect, Interaction
prospect = Prospect.objects.get(id=1)
interactions = prospect.interactions.all()
print(interactions)  # Should show interactions

# If empty, check if interaction has correct prospect_id
interaction = Interaction.objects.get(id=1)
print(interaction.prospect_id)
```

---

### Problem: "Cannot delete prospect - 'violates referential integrity'"

**Cause:** Prospect has related records (interactions, enrollments)

**Solution:**
```bash
# Option 1: Delete related records first
python manage.py shell
from crm.models import Prospect, Interaction
prospect = Prospect.objects.get(id=1)
prospect.interactions.all().delete()
prospect.enrollments.all().delete()
prospect.delete()

# Option 2: Use Django admin (handles cascade automatically)
# Go to /admin/crm/prospect/
# Select prospect and delete
```

---

## 8. Performance Issues

### Problem: "Prospect list page very slow (5+ seconds)"

**Cause:** N+1 query problem (loading owner for each prospect)

**Solution:**
```python
# In crm/views.py, update ProspectListView.get_queryset():
def get_queryset(self):
    return Prospect.objects.select_related('owner').filter(...)
    # select_related for ForeignKey
    # prefetch_related for ManyToMany/Reverse FK

# Check queries generated
python manage.py shell
from django.conf import settings
settings.DEBUG = True
from django.db import connection
# Run query
from crm.models import Prospect
list(Prospect.objects.all())
print(f"Total queries: {len(connection.queries)}")
for query in connection.queries:
    print(query['sql'])
```

---

### Problem: "Analytics dashboard takes 10+ seconds to load"

**Cause:** Expensive aggregation queries

**Solution:**
```bash
# Enable caching in settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'TIMEOUT': 300,  # 5 minutes
    }
}

# Cache dashboard views
# Add @cache_page(60*5) decorator to DashboardView
```

---

### Problem: "Server memory usage growing continuously"

**Cause:** Memory leak or unbounded result sets

**Solution:**
```bash
# Check for unbounded queries
# Ensure all QuerySets use .filter() or are paginated

# Use paginate_by in class-based views
paginate_by = 20

# Check for circular imports
python -m py_compile edu_expand/*.py

# Monitor memory
free -h  # Linux
get-process python | select -expand WS  # PowerShell

# Restart Django shell periodically
```

---

## 9. Frontend & Template Issues

### Problem: "CSS styles not applied (page looks plain)"

**Cause:** Static files not loaded

**Solution:**
```bash
# Step 1: Collect static files
python manage.py collectstatic --noinput

# Step 2: Verify Bootstrap CDN accessible
# In base.html, check Bootstrap CDN link loads
# Open browser console (F12) and check for 404 errors

# Step 3: Check static files in development
# Ensure STATIC_URL = '/static/' in settings.py
# Ensure STATIC_ROOT points to staticfiles directory

# Step 4: Hard refresh browser
# CTRL+SHIFT+R (Windows/Linux)
# CMD+SHIFT+R (Mac)
```

---

### Problem: "Chart.js not displaying in analytics dashboard"

**Cause:** Chart.js CDN not loaded or JavaScript error

**Solution:**
```bash
# Check 1: Chart.js CDN in base.html
# Should have: <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

# Check 2: JavaScript errors in browser console (F12)

# Check 3: Data endpoint returns valid JSON
curl http://localhost:8000/analytics/api/kpi-data/

# Check 4: JavaScript syntax in analytics/dashboard.html
# Look for typos in: var ctx = document.getElementById(...).getContext('2d');
```

---

### Problem: "Form fields not rendering properly"

**Cause:** Crispy forms not rendering correctly

**Solution:**
```bash
# Check 1: Crispy forms installed
pip install django-crispy-forms crispy-bootstrap5

# Check 2: Add to INSTALLED_APPS in settings.py
'crispy_forms',
'crispy_bootstrap5',

# Check 3: Set crispy template pack
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Check 4: Template loads crispy tags
# {% load crispy_forms_tags %}
# {{ form|crispy }}
```

---

## 10. Testing Issues

### Problem: "Tests fail with 'no such table' error"

**Cause:** Test database not created with all migrations

**Solution:**
```bash
# Run migrations before tests
python manage.py migrate

# Or run specific test
python manage.py test crm.models

# Run with verbose output
python manage.py test --verbosity=2
```

---

### Problem: "Test creates data but doesn't clean up"

**Cause:** TestCase not rolling back database

**Solution:**
```python
# Use TestCase (not SimpleTestCase)
from django.test import TestCase

class ScoreTest(TestCase):  # Not SimpleTestCase
    def setUp(self):
        # Create test data
        pass
    
    # Data automatically cleaned up after test
```

---

## 11. Deployment Issues

### Problem: "DEBUG=True in production shows sensitive info"

**Cause:** Settings not set to production values

**Solution:**
```bash
# In .env:
DEBUG=False

# In settings.py, verify:
DEBUG = env('DEBUG', default=False)

# Check no hardcoded True
grep -r "DEBUG = True" .
```

---

### Problem: "CSS/JavaScript 404 errors in production"

**Cause:** STATIC_URL not configured for production

**Solution:**
```bash
# Collect static files
python manage.py collectstatic --noinput

# Update settings.py for production
STATIC_URL = 'https://cdn.yourdomain.com/static/'
STATIC_ROOT = '/var/www/edu-expand/staticfiles/'

# Or use WhiteNoise middleware
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    ...
]
```

---

### Problem: "Email not sending in production"

**Cause:** SMTP credentials not in .env

**Solution:**
```bash
# Update .env on production server
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=app-specific-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Test email sending
python manage.py shell
from django.core.mail import send_mail
send_mail('Test', 'Hello', 'from@example.com', ['to@example.com'])
```

---

## 12. Getting Help

### Additional debug info

```bash
# Django check command
python manage.py check

# Show installed apps
python manage.py shell
from django.apps import apps
print([app.name for app in apps.get_app_configs()])

# Show database tables
python manage.py dbshell
.tables

# Show migrations status
python manage.py showmigrations

# Run with Python debugger
python -m pdb manage.py runserver

# Enable query logging
SHELL PLUS DEBUG=True
```

### Where to find logs

```
# Development logs
- Console output (terminal where you ran runserver)
- /logs/edu_expand.log (if configured)

# Production logs
- /var/log/edu-expand/django.log
- Gunicorn logs
- Nginx error.log
- Sentry (if configured)
```

### Useful debugging URLs

```
# Admin interface - check models/data
http://localhost:8000/admin/

# Django debug toolbar (if installed)
# Shows queries, templates, cache, etc.

# Check logs
tail -f /logs/edu_expand.log

# Monitor processes
ps aux | grep python
```

---

## Contact Support

If issue persists:
1. Check this guide completely
2. Review application logs
3. Run `python manage.py check`
4. Check environment configuration
5. Contact: support@edu-expand.com

Include in support request:
- Error message (full traceback)
- Steps to reproduce
- .env configuration (SANITIZED - remove secrets)
- `python manage.py --version`
- `python --version`
- Operating system

---

Last Updated: March 15, 2024
Version: 1.0.0
