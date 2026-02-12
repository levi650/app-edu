# EDU-EXPAND CRM - Production-Ready Django Application

A comprehensive CRM system designed for international prospecting and lead management, focused on Nigeria and Egypt. EDU-EXPAND includes prospect management, email automation, analytics, and a robust user authentication system with separate admin and client portals.

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [Environment Variables](#environment-variables)
- [Running the Project](#running-the-project)
- [Database Migrations](#database-migrations)
- [Seed Demo Data](#seed-demo-data)
- [URL Routes & Screens](#url-routes--screens)
- [User Roles & Permissions](#user-roles--permissions)
- [Key Features Guide](#key-features-guide)
- [5-Minute Demo Script](#5-minute-demo-script)

---

## ✨ Features

### CRM Module
- **Prospect Pipeline Management**: Track prospects through 8 stages (New → Contacted → Engaged → Interested → Demo Scheduled → Demo Done → Converted → Lost)
- **Prospect CRUD**: Create, read, update, delete prospects with full details
- **Interaction Logging**: Track emails, calls, meetings, WhatsApp, LinkedIn, SMS interactions
- **Scoring System**: Deterministic rule-based scoring (0-100) with breakdown and history
- **Priority Levels**: Auto-calculated (High/Medium/Low) based on score
- **Search & Filtering**: By name, email, country, stage, priority, owner

### Authentication & Portals
- **Custom User Model**: Email-based authentication
- **Three User Roles**:
  - **Admin**: Full system control, user management
  - **Commercial/Sales**: Manage prospects, interactions, view analytics
  - **Client**: Limited portal to view their own data
- **Separate Login Portals**:
  - Admin: `/accounts/admin-portal/login/`
  - Client: `/accounts/client-portal/login/`
- **Security**: Password reset, change password, audit logs

### Analytics & KPIs
- **Dashboard**: Real-time KPI cards and charts
- **KPIs**:
  - Total prospects
  - Prospects by stage
  - Conversion rate
  - Demos scheduled
  - Response rate
  - High priority leads
- **Visualizations**: Chart.js charts for country, stage, and score distribution
- **Reports**: Top leads, stale leads (no interaction 30+ days)
- **Filtering**: By date range, owner, country

### Email Automation
- **Email Templates**: Create reusable templates with variables ({{prospect_name}}, etc.)
- **Email Sequences**: Drip campaigns with multi-step sequences
- **Enrollment Management**: Enroll/pause/resume/cancel prospect enrollments
- **Email Logging**: Track sent, opened, clicked, replied emails
- **SMTP Configuration**: Via environment variables (Gmail, custom SMTP)
- **Auto-Interactions**: Sending email creates interaction automatically

### Scoring System
Rules-based algorithm:
- **Country bonus**: Nigeria/Egypt +30 pts, others +10 pts
- **Establishment type**: University +20, Private/Training +15, Public +10, Other +5
- **Decision maker role**: +10 pts
- **Stage weights**: Demo scheduled +15, Demo done +20, Converted +100
- **Interactions**: Email +10, Call +5, Positive outcome +15, Recent activity +5-10
- **Penalties**: No interaction 30+ days -30, Never contacted -10

Priority levels:
- High: Score ≥ 60
- Medium: 30-59
- Low: < 30

### Prospect Import & Enrichment
- **CSV Import**: Upload prospects from CSV
- **Data Cleaning**: Validates emails, removes empty values, deduplicates
- **Column Mapping**: Flexible CSV column mapping
- **Import History**: Track import jobs with success/failure counts

### Client Portal
- **Client Dashboard**: View organization profile
- **Communications History**: View email logs (read-only)
- **Restricted Access**: Only sees their own data

### Admin Back-Office
- **User Management**: Create/edit/delete commercial and client users
- **Bulk Actions**: Assign owner, change stage, recalc score, enroll sequences
- **Reference Data**: Built-in Nigeria & Egypt support
- **Audit Logs**: Track all system changes with user, timestamp, changes

---

## 🛠 Tech Stack

- **Backend**: Django 5.0+
- **Database**: PostgreSQL (recommended) or SQLite (dev)
- **Frontend**: Bootstrap 5, Chart.js
- **Python Version**: 3.11+
- **Email**: SMTP (Gmail, custom servers)
- **Optional**: Celery + Redis for async tasks

---

## 📁 Project Structure

```
edu_expand_crm/
├── manage.py                          # Django management script
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment variables template
├── README.md                          # This file
│
├── edu_expand/                        # Django project settings
│   ├── __init__.py
│   ├── settings.py                    # Main settings
│   ├── urls.py                        # Root URL config
│   ├── wsgi.py                        # WSGI application
│   └── asgi.py                        # ASGI application
│
├── accounts/                          # User authentication app
│   ├── models.py                      # User, AuditLog models
│   ├── views.py                       # Auth views (login, registration, password reset)
│   ├── forms.py                       # Auth forms
│   ├── urls.py
│   ├── admin.py                       # Django admin config
│   └── management/
│       └── commands/
│           └── seed_demo.py           # Demo data seeding
│
├── crm/                               # Core CRM app
│   ├── models.py                      # Prospect, Interaction, Client models
│   ├── views.py                       # CRM views (prospects, interactions, import)
│   ├── forms.py                       # CRM forms
│   ├── urls.py
│   ├── scoring.py                     # Scoring algorithm
│   └── admin.py                       # Django admin config
│
├── analytics/                         # Analytics & reporting app
│   ├── models.py                      # DashboardView model
│   ├── views.py                       # Dashboard and KPI endpoints
│   ├── urls.py
│   └── admin.py
│
├── emails/                            # Email automation app
│   ├── models.py                      # EmailTemplate, Sequence, Enrollment, EmailLog
│   ├── views.py                       # Email CRUD and management
│   ├── forms.py
│   ├── urls.py
│   └── admin.py
│
├── enrichment/                        # Data enrichment app
│   ├── models.py                      # ImportJob model
│   ├── views.py
│   ├── urls.py
│   └── admin.py
│
├── templates/                         # Django templates
│   ├── base.html                      # Main template
│   ├── accounts/
│   │   ├── admin_login.html
│   │   ├── client_login.html
│   │   ├── admin_dashboard.html
│   │   ├── client_dashboard.html
│   │   └── ...
│   ├── crm/
│   │   ├── prospect_list.html
│   │   ├── prospect_detail.html
│   │   ├── prospect_form.html
│   │   └── ...
│   ├── analytics/
│   │   ├── dashboard.html
│   │   └── ...
│   ├── emails/
│   │   ├── template_list.html
│   │   ├── sequence_list.html
│   │   └── ...
│   └── ...
│
├── static/                            # Static files (CSS, JS, images)
│   ├── css/
│   │   ├── styles.css
│   │   └── login.css
│   ├── js/
│   │   └── charts.js
│   └── img/
│
├── media/                             # User-uploaded media (imports, etc.)
│
├── logs/                              # Application logs
│   └── edu_expand.log
│
└── tests/                             # Unit and integration tests
    ├── test_models.py
    ├── test_views.py
    ├── test_scoring.py
    └── test_permissions.py
```

---

## 🚀 Installation & Setup

### 1. Prerequisites

- Python 3.11 or higher
- pip package manager
- Virtual environment (recommended)
- PostgreSQL (optional, SQLite works for local development)

### 2. Clone or Create Project

```bash
# If starting from scratch, create a directory:
mkdir edu_expand_crm
cd edu_expand_crm

# Or clone the repository
git clone <repository_url>
cd edu_expand_crm
```

### 3. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Create .env File

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your configuration (see section below)
```

---

## ⚙️ Environment Variables

Create a `.env` file in the root directory:

```bash
# Django Settings
DEBUG=True
SECRET_KEY=your-random-secret-key-here-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite for local development)
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# For PostgreSQL production:
# DB_ENGINE=django.db.backends.postgresql
# DB_NAME=edu_expand
# DB_USER=postgres
# DB_PASSWORD=your_password
# DB_HOST=localhost
# DB_PORT=5432

# Email Configuration (Gmail example)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
# For production:
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=your-email@gmail.com
# EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@edu-expand.com

# Security (set to True in production with HTTPS)
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False

# Celery (optional)
CELERY_ENABLED=False
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Languages
LANGUAGES=en,ar
DEFAULT_LANGUAGE=en
```

**Important**: 
- Generate a secure `SECRET_KEY` for production using: `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`
- For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833)

---

## 🔧 Running the Project

### 1. Database Migrations

```bash
# Create migration files
python manage.py makemigrations

# Apply migrations to database
python manage.py migrate
```

### 2. Create Superuser (Admin)

```bash
python manage.py createsuperuser
# Follow the prompts to create an admin user
```

### 3. Seed Demo Data (Optional)

```bash
python manage.py seed_demo
# Creates:
# - Admin user:  admin@edu-expand.com / admin123
# - 2 Commercial users: sales1@, sales2@ / sales123
# - 15 sample prospects (Nigeria & Egypt)
# - Sample email templates and sequences
```

### 4. Collect Static Files (Production)

```bash
python manage.py collectstatic --noinput
```

### 5. Run Development Server

```bash
python manage.py runserver
# Server runs at http://localhost:8000
```

### 6. Access Application

- **Admin Portal**: http://localhost:8000/accounts/admin-portal/login/
- **Client Portal**: http://localhost:8000/accounts/client-portal/login/
- **Django Admin**: http://localhost:8000/admin/

---

## 📊 URL Routes & Screens

### Public Routes
| Route | Description |
|-------|-------------|
| `/accounts/register/` | Client registration |
| `/accounts/password-reset/` | Password reset request |
| `/accounts/password-reset/confirm/<token>/` | Reset password confirmation |

### Admin/Commercial Portal (Auth Required)
| Route | Description |
|-------|-------------|
| `/accounts/admin-portal/login/` | Admin login |
| `/accounts/admin-portal/dashboard/` | Admin dashboard |
| `/accounts/admin-portal/users/` | User management |
| `/accounts/admin-portal/audit-logs/` | Audit log view |
| `/crm/prospects/` | Prospect list (with filters) |
| `/crm/prospects/create/` | Create new prospect |
| `/crm/prospects/<id>/` | Prospect detail |
| `/crm/prospects/<id>/edit/` | Edit prospect |
| `/crm/prospects/<id>/recalc-score/` | Recalculate score |
| `/crm/prospects/<id>/interactions/add/` | Log interaction |
| `/crm/import/` | CSV prospect import |
| `/crm/clients/` | Client list |
| `/analytics/dashboard/` | Analytics dashboard |
| `/analytics/api/kpis/` | KPI data (JSON) |
| `/emails/templates/` | Email templates |
| `/emails/sequences/` | Email sequences |
| `/emails/enrollments/` | Campaign enrollments |

### Client Portal (Auth Required)
| Route | Description |
|-------|-------------|
| `/accounts/client-portal/login/` | Client login |
| `/accounts/client-portal/dashboard/` | Client dashboard |
| `/accounts/client-portal/profile/` | Client profile |
| `/accounts/client-portal/communications/` | Email communications |

### Django Admin
| Route | Description |
|-------|-------------|
| `/admin/` | Django admin panel |

---

## 👥 User Roles & Permissions

### Admin
- **Permissions**: Full system access
- **Views**: User management, audit logs, all CRM features
- **Login**: `/accounts/admin-portal/login/`

### Commercial (Sales Team)
- **Permissions**: Manage own prospects, create interactions, view analytics
- **Views**: Prospect list (filtered to owner), create/edit prospects, email campaigns
- **Login**: `/accounts/admin-portal/login/` (same portal, different role)

### Client
- **Permissions**: Read-only access to their organization data
- **Views**: Organization profile, email communication history
- **Login**: `/accounts/client-portal/login/`

**Row-Level Security**: Commercial users see only their prospects. Admin sees all.

---

## 🎯 Key Features Guide

### Prospect Management
1. **Create Prospect**: `/crm/prospects/create/`
   - Fill in basic info (name, country, contact, email, etc.)
   - System auto-assigns stage (New) and owner
   - Score is auto-calculated based on rules

2. **View Prospect Detail**: `/crm/prospects/<id>/`
   - See all interactions and emails
   - View scoring breakdown
   - Log new interactions
   - Manual score recalculation

3. **Search & Filter**: `/crm/prospects/`
   - By name, email, phone
   - By country (Nigeria/Egypt + others)
   - By stage, priority, owner
   - Pagination (20 per page)

### Scoring System
- **Auto-calculated** on prospect create and interaction log
- **Rule-based** with clear breakdown
- **Recalculation**: Manual via "Recalc Score" button, or bulk action
- **Decay**: Penalized if no interaction 30+ days

### Email Automation
1. **Create Template**: `/emails/templates/create/`
   - Subject, HTML body, plain text
   - Add variables: {{prospect_name}}, {{school_name}}, etc.

2. **Create Sequence**: `/emails/sequences/create/`
   - Add sequential steps with delays
   - Assign templates to steps

3. **Enroll Prospect**: From prospect detail or bulk action
   - Select sequence
   - Auto-sends based on schedule
   - Track in Email Logs

### Analytics Dashboard
- **KPI Cards**: Total prospects, conversion rate, demos, response rate
- **Charts**: By country, by stage, score distribution
- **Reports**: Top leads (high priority), stale leads (30+ days no contact)
- **Filters**: Date range, owner, country

### CSV Import
1. Navigate to `/crm/import/`
2. Upload CSV with columns: `name, email, phone, country, city, contact_name, contact_role`
3. Select owner for imported prospects
4. System validates, deduplicates, imports
5. Track import status in Import Jobs list

---

## ✅ 5-Minute Demo Script

**Goal**: Show all core features working.  
**Time**: ~5 minutes

### Step 1: Login as Admin (30 seconds)
1. Go to http://localhost:8000/accounts/admin-portal/login/
2. Enter: `admin@edu-expand.com` / `admin123`
3. Visit admin dashboard to show system overview

### Step 2: View Prospects (1 minute)
1. Click "Prospects" in navbar
2. Show prospect list with filters
3. Try filtering by Nigeria, "High" priority
4. Click on a prospect to view details
5. Show interactions timeline + scoring breakdown

### Step 3: Log Interaction (1 minute)
1. In prospect detail, scroll to "Log Interaction"
2. Select type (email/call/meeting), enter summary, select outcome (positive)
3. Submit - show interaction added
4. Refresh - notice score recalculated, stage auto-updated if positive outcome

### Step 4: Analytics Dashboard (1.5 minutes)
1. Click "Analytics" in navbar
2. Show KPI cards (total prospects, conversion rate)
3. Scroll down to see charts (by country, by stage)
4. Filter by country=Nigeria to show responsive filtering
5. Show "Top Leads" and "Stale Leads" sections

### Step 5: Email Templates & Sequences (1 minute)
1. Click "Emails" → "Templates"
2. Show example template with variables
3. Click "Sequences" → Show "New Lead Sequence"
4. Show multi-step sequence with delays

### Step 6: Logout & Client Portal (optional)
1. Logout
2. Login to client portal: `/accounts/client-portal/login/`
3. Show limited client view (only see own organization data)

---

## 🧪 Testing

Run tests:

```bash
# All tests
python manage.py test

# Specific test file
python manage.py test accounts.tests.test_models

# Specific test class
python manage.py test accounts.tests.TestUserModel

# With coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

**Test Coverage**:
- Permission tests (client blocked from admin data)
- Scoring algorithm tests
- CSV import validation
- Email sending logic
- Prospect filtering

---

## 🔒 Security Checklist

- [ ] Change `SECRET_KEY` in production
- [ ] Set `DEBUG=False` in production
- [ ] Use `SECURE_SSL_REDIRECT=True` with HTTPS
- [ ] Set `SESSION_COOKIE_SECURE=True`
- [ ] Set `CSRF_COOKIE_SECURE=True`
- [ ] Use PostgreSQL (not SQLite) in production
- [ ] Configure email SMTP with app passwords
- [ ] Set strong `ALLOWED_HOSTS`
- [ ] Review audit logs regularly
- [ ] Use environment variables for all secrets
- [ ] Enable HTTPS/TLS
- [ ] Set up proper backups

---

## 📝 Logging

Application logs are written to `logs/edu_expand.log`.  
Configure logging level in `settings.py`.

View logs:
```bash
tail -f logs/edu_expand.log
```

---

## 🚢 Deployment (Quick Guide)

### Heroku
```bash
heroku create your-app-name
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

### Docker
```bash
docker build -t edu-expand .
docker run -p 8000:8000 -e DEBUG=False edu-expand python manage.py runserver 0.0.0.0:8000
```

### Traditional VPS (Ubuntu)
```bash
# Install PostgreSQL, Python, dependencies
# Clone project, create venv, install requirements
# Run migrations
python manage.py collectstatic
# Use Gunicorn + Nginx
gunicorn edu_expand.wsgi:application --bind 0.0.0.0:8000
```

---

## 📞 Support & Troubleshooting

### Migration Issues
```bash
# If migrations fail, reset (dev only):
python manage.py migrate crm zero  # Reset migrations
python manage.py migrate
```

### Clear Cache
```bash
python manage.py clear_cache
```

### Debug SQL Queries
```python
# In Django shell:
from django.db import connection
from django.test.utils import CaptureQueriesContext

with CaptureQueriesContext(connection) as queries:
    # Your code here
print(len(queries), "queries")
```

---

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Bootstrap 5 Docs](https://getbootstrap.com/docs/5.0/)
- [Chart.js Docs](https://www.chartjs.org/docs/latest/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)

---

## 📄 License

This project is proprietary and confidential.

---

## 📞 Contact

For questions or issues, contact the development team.

---

**Last Updated**: February 2026  
**Version**: 1.0.0  
**Status**: Production-Ready ✅
