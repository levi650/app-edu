# EDU-EXPAND Quick Reference Guide

## Installation & Setup (5 minutes)

```bash
# 1. Clone and navigate
git clone https://github.com/your-org/edu-expand.git
cd edu-expand

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your settings

# 5. Create database
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser
# Email: admin@example.com
# Password: (choose strong password)

# 7. Load demo data (optional)
python manage.py seed_demo

# 8. Start server
python manage.py runserver

# 9. Access application
# Admin portal: http://localhost:8000/accounts/admin-portal/login/
# Client portal: http://localhost:8000/accounts/client-portal/login/
```

---

## Key Features

### 1. Prospect Management
- **Add Prospect:** CRM → Prospects → Add → Fill form
- **Search:** Use search bar with name/email
- **Filter:** By stage, priority, country
- **Score:** Auto-calculated (0-100), updated when interactions added
- **Export:** Select prospects → Actions → Export to CSV

### 2. Interactions
- **Log:** Click prospect → New Interaction → Select type
- **Types:** Email, Call, Meeting, WhatsApp, LinkedIn, SMS, Other
- **Outcomes:** Positive, Neutral, Negative
- **Follow-up:** Set next action date

### 3. Email Automation
- **Templates:** Create reusable email templates with variables
- **Sequences:** Create multi-step drip campaigns
- **Enroll:** Assign prospects to sequences
- **Variables:** {{prospect_name}}, {{school_name}}, etc.

### 4. Analytics Dashboard
- **KPIs:** Total prospects, conversion rate, response rate
- **Charts:** By country, by stage, score distribution
- **Filters:** Date range, owner, country
- **Top Leads:** Score >= 60
- **Stale Leads:** No interaction 30+ days

### 5. CSV Import
- **Supported:** Name, Email, Phone, Country, Contact info
- **Upload:** CRM → Import → Select file → Preview → Import
- **Validation:** Automatic duplicate detection
- **Status:** Track import progress in Jobs

---

## User Roles & Permissions

### Admin
- Full system access
- User management
- Report generation
- System configuration

### Commercial (Sales)
- See own prospects only
- CRUD own prospects
- Log interactions
- See analytics for own prospects
- Enroll in sequences

### Client (Partner)
- View account information
- View assigned information only
- Cannot modify data

---

## Common Tasks

### Task: Add New Prospect
1. Navigate to CRM → Prospects
2. Click "+ New Prospect"
3. Fill fields (Name, Email, Country required)
4. Click "Save"

### Task: Log Interaction
1. Open prospect detail
2. Click "New Interaction" (right sidebar)
3. Select type (Email, Call, etc.)
4. Enter summary
5. Optional: Set outcome & follow-up date
6. Click "Save"

### Task: Create Email Campaign
1. Go to Emails → Templates
2. Click "+ New Template"
3. Enter subject, body (with variables like {{prospect_name}})
4. Save template
5. Go to Sequences → Create Sequence
6. Add steps (template + delay)
7. Save sequence
8. Enroll prospects

### Task: Export Data
1. Go to CRM → Prospects
2. Select prospects (checkbox)
3. Click "Actions" dropdown
4. Select "Export CSV"
5. File downloads

### Task: View Analytics
1. Go to Analytics → Dashboard
2. Select filters (optional)
3. View KPI cards
4. Scroll down for charts
5. Click chart legends to toggle data

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `/` | Search |
| `?` | Help |
| `n` | New prospect |
| `e` | Export |
| `g h` | Go to home |
| `g p` | Go to prospects |
| `g a` | Go to analytics |

---

## API Reference

### List Prospects
```bash
curl -H "Cookie: sessionid=..." \
  "http://localhost:8000/crm/prospects/"
```

### Get KPI Data
```bash
curl -H "Cookie: sessionid=..." \
  "http://localhost:8000/analytics/api/kpi-data/"
```

### Create Prospect
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=..." \
  -d '{"name":"Test","email":"test@example.com","country":"NG"}' \
  "http://localhost:8000/crm/prospects/"
```

*See API_DOCUMENTATION.md for complete API reference*

---

## URL Map

### Authentication
- `/accounts/admin-portal/login/` - Admin login
- `/accounts/client-portal/login/` - Client login
- `/accounts/register/` - Registration
- `/accounts/password-reset/` - Password reset
- `/accounts/logout/` - Logout

### CRM
- `/crm/prospects/` - Prospect list
- `/crm/prospects/add/` - Create prospect
- `/crm/prospects/<id>/` - Prospect detail
- `/crm/prospects/<id>/edit/` - Edit prospect
- `/crm/prospects/<id>/delete/` - Delete prospect
- `/crm/prospects/<id>/interactions/` - Log interaction
- `/crm/import/` - CSV import
- `/crm/clients/` - Converted clients list

### Email Automation
- `/emails/templates/` - Email templates
- `/emails/sequences/` - Email sequences
- `/emails/enrollments/` - Prospect enrollments
- `/emails/logs/` - Email send logs

### Analytics
- `/analytics/` - Dashboard
- `/analytics/api/kpi-data/` - KPI API
- `/analytics/api/country-breakdown/` - Country breakdown API
- `/analytics/api/top-leads/` - Top leads API

### Admin
- `/admin/` - Django admin interface

---

## Database Models

### Prospect
- name, email, phone, country, city
- contact_name, contact_role
- type_of_establishment (university/private/training/public/other)
- stage (new/contacted/engaged/interested/demo_scheduled/demo_done/converted/lost)
- score (0-100), priority (H/M/L)
- budget, website, linkedin_url
- owner (FK to User), notes
- created_at, updated_at

### Interaction
- prospect (FK)
- interaction_type (email/call/meeting/whatsapp/linkedin/sms/other)
- summary (required)
- outcome (positive/neutral/negative)
- created_by (FK to User)
- created_at, interaction_date, next_action_date

### EmailTemplate
- name, subject, body_html, body_text
- variables (JSON array)
- created_by (FK to User)
- created_at, updated_at

### EmailSequence
- name, description, is_active
- created_by (FK to User)

### Enrollment
- prospect (FK), sequence (FK)
- status (active/paused/completed/cancelled)
- next_send_at

---

## Scoring Algorithm

### Components
- **Country Bonus:** Nigeria/Egypt +30, Others +10
- **Establishment:** University +20, Private/Training +15, Public +10, Other +5
- **Contact Role:** Decision maker +10
- **Stage:** Demo scheduled +15, Demo done +20, Converted +100
- **Interactions:** Email +10, Call +5, Positive outcome +15
- **Penalty:** No interaction 30+ days -30, Never contacted -10

### Priority
- **High (H):** Score >= 60
- **Medium (M):** Score 30-59
- **Low (L):** Score < 30

---

## Configuration Files

### .env
Main environment configuration
```
DEBUG=True
SECRET_KEY=...
DATABASE_ENGINE=sqlite3
```

### settings.py
Django configuration
```
- INSTALLED_APPS: Lists all apps
- DATABASES: Database settings
- EMAIL_*: Email configuration
- STATIC_*/MEDIA_*: File storage
```

### requirements.txt
Python dependencies

### manage.py
Django management script

---

## Troubleshooting

### Server won't start
```bash
# Check for syntax errors
python manage.py check

# Check migrations
python manage.py showmigrations

# Rerun migrations
python manage.py migrate
```

### Database errors
```bash
# Reset database (development only)
rm db.sqlite3
python manage.py migrate
python manage.py seed_demo
```

### Static files not loading
```bash
# Collect static files
python manage.py collectstatic --noinput
```

### Can't login
```bash
# Create new superuser
python manage.py createsuperuser

# Reset password in shell
python manage.py shell
from django.contrib.auth import get_user_model
User = get_user_model()
u = User.objects.get(email='your@email.com')
u.set_password('newpass')
u.save()
```

### Email not sending
```bash
# Check SMTP settings in .env
# Test in shell:
python manage.py shell
from django.core.mail import send_mail
send_mail('Test', 'Body', 'from@example.com', ['to@example.com'])
```

---

## Performance Tips

### Database
- Index frequently filtered fields
- Use select_related() for foreign keys
- Use prefetch_related() for reverse relations
- Monitor slow queries

### Caching
- Enable Redis caching
- Cache prospect list (5-minute TTL)
- Cache analytics data (1-hour TTL)

### Files
- Compress static files
- Use CDN for media
- Optimize images

---

## Security Best Practices

1. **Change Secret Key** before production
2. **Set DEBUG=False** in production
3. **Use HTTPS** on all pages
4. **Strong Passwords** for all accounts
5. **Regular Backups** (daily minimum)
6. **Update Dependencies** monthly
7. **Restrict Admin** to trusted IPs
8. **Audit Logs** for all changes
9. **API Keys** in .env not code
10. **SQL Injection** prevention (uses Django ORM)

---

## Support

- **Documentation:** See README.md and API_DOCUMENTATION.md
- **Issues:** Check GitHub issues
- **Email:** support@edu-expand.com
- **Phone:** [Your support number]

---

## Version Info

- **EDU-EXPAND:** v1.0.0
- **Django:** 5.0.1
- **Python:** 3.11+
- **Database:** PostgreSQL 14+ (SQLite for dev)
- **Last Updated:** 2024-03-15

---

## Quick Commands

```bash
# Start development server
python manage.py runserver

# Create superuser
python manage.py createsuperuser

# Run migrations
python manage.py migrate

# Load demo data
python manage.py seed_demo

# Run tests
python manage.py test

# Open Python shell
python manage.py shell

# Access Django admin
# GO TO: http://localhost:8000/admin/

# Celery worker (async tasks)
celery -A edu_expand worker -l info

# Redis server (requires Redis installed)
redis-server
```

---

Last Updated: 2024-03-15
Version: 1.0.0
