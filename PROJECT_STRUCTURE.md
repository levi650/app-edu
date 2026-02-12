# EDU-EXPAND Project File Structure

## Complete Directory Overview

```
edu-expand/
│
├── README.md                          # Main documentation
├── QUICK_REFERENCE.md                 # Quick start guide
├── API_DOCUMENTATION.md               # API endpoints reference
├── DEPLOYMENT_GUIDE.md                # Production deployment
├── PROJECT_STRUCTURE.md               # This file
│
├── manage.py                          # Django management script
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment template
├── .env.local.example                 # Local dev environment
├── .gitignore                         # Git ignore rules
│
├── edu_expand/                        # Django project root
│   ├── __init__.py
│   ├── settings.py                    # All Django configuration
│   ├── urls.py                        # Root URL routing
│   ├── wsgi.py                        # Production WSGI app
│   ├── asgi.py                        # ASGI app (async)
│   └── __pycache__/
│
├── accounts/                          # User authentication app
│   ├── migrations/
│   │   ├── 0001_initial.py            # Create User, AuditLog models
│   │   ├── 0002_user_client.py        # Add client FK
│   │   └── __init__.py
│   ├── __init__.py
│   ├── admin.py                       # Django admin config
│   ├── apps.py                        # App config
│   ├── forms.py                       # Forms (authentication, user mgmt)
│   ├── models.py                      # User, AuditLog models
│   ├── urls.py                        # Auth routes
│   ├── views.py                       # Auth views (1000+ lines)
│   └── templates/
│       ├── accounts/
│       │   ├── admin_login.html       # Admin portal login
│       │   ├── client_login.html      # Client portal login
│       │   └── client_portal.html     # Client dashboard
│       └── __pycache__/
│
├── crm/                               # Core CRM app
│   ├── migrations/
│   │   ├── 0001_initial.py            # Prospect, Interaction, Client models
│   │   └── __init__.py
│   ├── management/
│   │   └── commands/
│   │       ├── seed_demo.py           # Demo data seeding
│   │       └── __init__.py
│   ├── __init__.py
│   ├── admin.py                       # Django admin with bulk actions
│   ├── apps.py                        # App config
│   ├── forms.py                       # CRM forms
│   ├── models.py                      # Prospect, Interaction, Client models
│   ├── scoring.py                     # Scoring algorithm (calculate_score)
│   ├── urls.py                        # CRM routes
│   ├── views.py                       # CRM views (900+ lines)
│   └── templates/
│       ├── crm/
│       │   ├── prospect_list.html     # Prospect list with filters
│       │   ├── prospect_form.html     # Create/edit prospect
│       │   ├── prospect_detail.html   # Single prospect detail
│       │   └── interaction_form.html  # Log interaction form
│       └── __pycache__/
│
├── emails/                            # Email automation app
│   ├── migrations/
│   │   ├── 0001_initial.py            # Email models
│   │   └── __init__.py
│   ├── __init__.py
│   ├── admin.py                       # Django admin config
│   ├── apps.py                        # App config
│   ├── forms.py                       # Email forms
│   ├── models.py                      # EmailTemplate, Sequence, Enrollment
│   ├── urls.py                        # Email routes
│   ├── views.py                       # Email views (700+ lines)
│   └── templates/
│       ├── emails/
│       │   └── template_list.html     # Email templates list
│       └── __pycache__/
│
├── analytics/                         # Analytics/reporting app
│   ├── migrations/
│   │   ├── 0001_initial.py            # DashboardView model
│   │   └── __init__.py
│   ├── __init__.py
│   ├── admin.py                       # Django admin config
│   ├── apps.py                        # App config
│   ├── models.py                      # DashboardView model
│   ├── urls.py                        # Analytics routes
│   ├── views.py                       # Analytics views
│   └── templates/
│       ├── analytics/
│       │   └── dashboard.html         # Analytics dashboard (1000+ lines)
│       └── __pycache__/
│
├── enrichment/                        # Data import app
│   ├── migrations/
│   │   ├── 0001_initial.py            # ImportJob model
│   │   └── __init__.py
│   ├── __init__.py
│   ├── admin.py                       # Django admin config
│   ├── apps.py                        # App config
│   ├── models.py                      # ImportJob model
│   ├── urls.py                        # Import routes
│   └── views.py                       # Import views
│
├── templates/                         # Global templates
│   ├── base.html                      # Master template (120+ lines)
│   ├── includes/
│   │   └── form_field.html            # Reusable form field template
│   └── __pycache__/
│
├── static/                            # Static files
│   ├── css/
│   │   ├── styles.css                 # Main styling (350+ lines)
│   │   └── login.css                  # Login page styling (150+ lines)
│   ├── js/
│   │   └── (future: custom JavaScript)
│   └── img/
│       └── (future: image assets)
│
├── media/                             # User-uploaded files
│   └── (created at runtime)
│
├── staticfiles/                       # Collected static files (production)
│   └── (generated by collectstatic)
│
├── logs/                              # Application logs
│   └── (generated at runtime)
│
├── tests/                             # Test files
│   ├── __init__.py
│   ├── test_scoring.py                # Scoring algorithm tests
│   └── (additional tests)
│
└── __pycache__/                       # Python cache
```

---

## File Count Summary

| Category | Count | Purpose |
|----------|-------|---------|
| Django Apps | 5 | accounts, crm, analytics, emails, enrichment |
| Models | 15+ | All database models |
| Views | 50+ | Request handlers |
| Forms | 20+ | User input forms |
| Templates | 12+ | HTML pages |
| Static Files | 2 | CSS files |
| Migrations | 6 | Database schema |
| URLs | 75+ | Routing configuration |
| Admin Configs | 5 | Django admin |
| Tests | 1 | Test suite starter |

**Total Lines of Code:** 30,000+

---

## Key Files Explained

### settings.py (300+ lines)
Master Django configuration file containing:
- Installed apps list
- Database settings
- Email configuration
- Static/media file paths
- Security settings
- Middleware configuration
- Template backends
- Caching setup

### urls.py (Root)
Main URL router that includes:
- Admin URLs
- Accounts app URLs
- CRM app URLs
- Email app URLs
- Analytics app URLs
- Enrichment app URLs

### models.py (Per App)
Database models with:
- Field definitions
- Relationships (FK, M2M)
- Methods and properties
- Model Meta options
- String representations (__str__)

### views.py (Per App)
Business logic containing:
- Class-based views (CBV)
- Request handling
- Response generation
- Permission checks
- Form processing

### forms.py (Per App)
User input validation with:
- Django ModelForm definitions
- Custom validation
- Field customization
- Error messages

### templates/ (HTML)
User interface pages with:
- Bootstrap 5 styling
- Crispy forms integration
- Chart.js for analytics
- Responsive design

### static/css/ (Stylesheets)
CSS files with:
- Bootstrap customization
- Custom classes
- Responsive design
- Login page styling

### migrations/ (Database)
Schema versioning with:
- Auto-generated migration files
- Manual migration edits
- Rollback capability
- Schema history

---

## Database Schema Overview

### accounts_user (Custom User Model)
```
id, email (unique), password, first_name, last_name
is_active, is_staff, is_superuser
role (admin/commercial/client)
phone, company, created_at, updated_at
client (FK to crm_client, nullable)
```

### crm_prospect
```
id, name, email, phone, country, city
contact_name, contact_role
type_of_establishment
stage (0-7), score (0-100), priority (H/M/L)
budget, website, linkedin_url
owner (FK to accounts_user)
notes, created_at, updated_at, last_interaction_at
```

### crm_interaction
```
id, prospect (FK), interaction_type (0-6)
summary, outcome (P/N/U)
interaction_date, next_action_date
created_by (FK to accounts_user), created_at
```

### crm_client (Converted Prospect)
```
id, name, email, country_code
contact_person, primary_contact_email
assigned_user (FK to accounts_user), nullable
subscription_status, monthly_fee
contracts_json
notes, created_at, updated_at
```

### emails_emailtemplate
```
id, name, subject, body_html, body_text
variables (JSON array)
created_by (FK to accounts_user)
created_at, updated_at
```

### emails_emailsequence
```
id, name, description, is_active
created_by (FK to accounts_user)
created_at, updated_at
```

### emails_sequencestep
```
id, sequence (FK), order
delay_days, template (FK to emailtemplate)
```

### emails_enrollment
```
id, prospect (FK), sequence (FK)
status (A/P/C/X), enrolled_at, next_send_at
```

### analytics_dashboardview
```
id, user (FK), viewed_at
```

### accounts_auditlog
```
id, action, model_name, object_id
user (FK), old_values (JSON), new_values (JSON)
timestamp, ip_address
```

---

## Development Workflow

### 1. Add New Feature
```bash
# Create new app if needed
python manage.py startapp feature_name

# Create models
# Edit feature_name/models.py

# Create forms
# Edit feature_name/forms.py

# Create views
# Edit feature_name/views.py

# Create templates
# Create feature_name/templates/feature_name/

# Create URLs
# Edit feature_name/urls.py

# Include in main urls.py
# Edit edu_expand/urls.py

# Create migration
python manage.py makemigrations

# Apply migration
python manage.py migrate

# Update admin
# Edit feature_name/admin.py
```

### 2. Modify Existing Model
```bash
# Update models.py

# Create migration
python manage.py makemigrations crm

# Review migration
# cat crm/migrations/000X_auto.py

# Apply migration
python manage.py migrate
```

### 3. Fix Bug
```bash
# Create test case
# Edit tests/test_something.py

# Reproduce issue

# Fix code

# Run tests
python manage.py test

# Verify fix
```

---

## Dependencies Explained

### Core Framework
- **Django 5.0.1:** Web framework
- **psycopg2-binary:** PostgreSQL driver
- **Gunicorn:** Production WSGI server
- **WhiteNoise:** Static files serving

### Frontend
- **django-crispy-forms:** Form rendering
- **crispy-bootstrap5:** Bootstrap integration
- **django-filter:** Filtering functionality
- **Chart.js:** Analytics charts (via CDN)
- **Bootstrap 5:** CSS framework (via CDN)

### Utilities
- **python-decouple:** Environment config
- **Pillow:** Image handling
- **redis:** Caching/sessions
- **Celery:** Async tasks

### Optional/Production
- **sentry-sdk:** Error tracking
- **django-storages:** Cloud storage
- **boto3:** AWS S3 integration

---

## Configuration Hierarchy

1. **System Environment**
   - OS environment variables
   - System config files

2. **.env File**
   - Application-specific config
   - Secrets and API keys
   - Database credentials

3. **settings.py**
   - Django default settings
   - App configuration
   - Constant values
   - Reads from .env

4. **App Config (apps.py)**
   - Per-app settings
   - Signal handlers

5. **Model Meta**
   - Database constraints
   - Model-level config

---

## Deployment Checklist File Locations

- [ ] Update .env with production values
- [ ] Set DEBUG=False in settings.py
- [ ] Generate strong SECRET_KEY
- [ ] Configure database (settings.py)
- [ ] Setup email (settings.py)
- [ ] Collect static files: `python manage.py collectstatic`
- [ ] Run migrations: `python manage.py migrate`
- [ ] Create superuser: `python manage.py createsuperuser`
- [ ] Configure Gunicorn
- [ ] Setup Nginx reverse proxy
- [ ] Enable HTTPS/SSL
- [ ] Setup monitoring (Sentry)
- [ ] Configure backups
- [ ] Setup logging

---

## Performance Optimization Locations

### Database
- `crm/models.py` - Add database indexes
- `settings.py` - Configure connection pooling
- `crm/views.py` - Use select_related/prefetch_related

### Caching
- `settings.py` - Cache backend config
- `analytics/views.py` - Add @cache_page decorators
- `crm/views.py` - Cache prospect list

### Static Files
- `static/css/` - Minify CSS
- `static/js/` - Minify JavaScript
- `settings.py` - Configure CDN

### Query Optimization
- `crm/views.py` - Use .values() for aggregation
- `analytics/views.py` - Limit query results
- All views - Paginate large result sets

---

## Testing Locations

Unit tests: `tests/test_*.py`
Integration tests: Models + Views together
E2E tests: Full user workflows

Current test file: `tests/test_scoring.py` (Scoring algorithm tests)

---

## Documentation Files

- `README.md` - Main documentation (setup, features, usage)
- `QUICK_REFERENCE.md` - Quick start and common tasks
- `API_DOCUMENTATION.md` - REST API endpoints
- `DEPLOYMENT_GUIDE.md` - Production deployment steps
- `PROJECT_STRUCTURE.md` - This file (file organization)

---

## Last Updated
March 15, 2024

## Version
EDU-EXPAND v1.0.0
