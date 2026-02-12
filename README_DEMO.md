EDU-EXPAND ORI — Demo Guide

Quick demo workflows

1) Start the app and create superuser (if not present).
   - Admin login (seeded by demo): admin@example.com / adminpass
   - Commercial users (seeded): alice.sales@example.com, bob.sales@example.com (password: `password`)

2) Seed demo data (recommended):

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
```

3) Key demo flows
   - Landing page: `/` — marketing hero and CTA.
   - Sign in (Client): `/accounts/client-portal/login/` or admin `/accounts/admin-portal/login/`.
   - CRM prospects: `/crm/prospects/` — list, search, filters.
   - Prospect detail: `/crm/prospects/<id>/` — interactions, score breakdown, email logs.
   - Import jobs: `/enrichment/import-jobs/` — upload CSV and poll status.

4) Demo API endpoints (useful for UI polling)
   - `GET /crm/api/prospects/?page=1` — list prospects (paginated)
   - `GET /crm/api/prospects/<id>/summary/` — quick prospect summary (score, last interaction)
   - `GET /enrichment/api/import-jobs/<id>/status/` — import job status for polling

5) Reset demo data (safe):

```bash
python manage.py seed_demo --reset
# add --force to skip confirmation
```

Notes
- The seeding command uses Faker to generate realistic demo data and marks demo-created records with `AuditLog(action='demo_seed')` so reset only removes demo entries.
- For a production API, replace the lightweight JSON endpoints with Django REST Framework and serializers.

Contact
- For questions about the demo setup, contact the engineering owner.
