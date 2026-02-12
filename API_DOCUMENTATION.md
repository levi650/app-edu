# EDU-EXPAND API Documentation

## Overview
EDU-EXPAND provides REST API endpoints for analytics and reporting. All endpoints require authentication.

## Authentication
API authentication uses Django session authentication. Ensure you're logged in to access protected endpoints.

## Base URL
```
http://localhost:8000/api/
```

---

## Analytics Endpoints

### 1. Get Dashboard Data
Retrieve overall KPI metrics.

**Endpoint:** `GET /analytics/api/kpi-data/`

**Authentication:** Required (CommercialRequiredMixin)

**Query Parameters:**
- `date_from` (optional): Start date (YYYY-MM-DD)
- `date_to` (optional): End date (YYYY-MM-DD)
- `owner_id` (optional): Filter by user ID
- `country` (optional): Filter by country code

**Response:**
```json
{
  "total_prospects": 150,
  "converted_count": 12,
  "demos_scheduled": 8,
  "response_rate": 45.5,
  "conversion_rate": 8.0
}
```

**Example Request:**
```bash
curl -H "Cookie: sessionid=your_session_id" \
  "http://localhost:8000/analytics/api/kpi-data/?date_from=2024-01-01&country=NG"
```

---

### 2. Get Country Breakdown
Prospects by country.

**Endpoint:** `GET /analytics/api/country-breakdown/`

**Authentication:** Required

**Query Parameters:** Same as KPI Data

**Response:**
```json
{
  "NG": 85,
  "EG": 45,
  "US": 20
}
```

---

### 3. Get Stage Breakdown
Prospects by pipeline stage.

**Endpoint:** `GET /analytics/api/stage-breakdown/`

**Authentication:** Required

**Query Parameters:** Same as KPI Data

**Response:**
```json
{
  "new": 40,
  "contacted": 35,
  "engaged": 25,
  "interested": 20,
  "demo_scheduled": 15,
  "demo_done": 10,
  "converted": 5
}
```

---

### 4. Get Score Distribution
Prospects grouped by score ranges.

**Endpoint:** `GET /analytics/api/score-distribution/`

**Authentication:** Required

**Query Parameters:** Same as KPI Data

**Response:**
```json
{
  "0-20": 30,
  "20-40": 35,
  "40-60": 45,
  "60-80": 30,
  "80-100": 10
}
```

---

### 5. Get Top Leads
High-priority prospects (score >= 60).

**Endpoint:** `GET /analytics/api/top-leads/`

**Authentication:** Required

**Query Parameters:**
- `limit` (optional): Number of records (default: 10)

**Response:**
```json
[
  {
    "id": 1,
    "name": "University of Lagos",
    "email": "info@unilag.edu.ng",
    "country": "NG",
    "score": 85,
    "priority": "H"
  }
]
```

---

### 6. Get Stale Leads
Prospects with no interaction in 30+ days.

**Endpoint:** `GET /analytics/api/stale-leads/`

**Authentication:** Required

**Query Parameters:** Same as KPI Data

**Response:**
```json
[
  {
    "id": 5,
    "name": "Cairo Business School",
    "email": "contact@cbs.eg",
    "days_without_interaction": 45,
    "last_interaction": "2024-01-15"
  }
]
```

---

## CRM Endpoints

### 1. List Prospects
Get paginated prospect list.

**Endpoint:** `GET /crm/prospects/`

**Authentication:** Required

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `search` (optional): Search by name/email
- `stage` (optional): Filter by stage
- `priority` (optional): Filter by priority (L/M/H)
- `owner_id` (optional): Filter by owner

**Response:**
```json
{
  "count": 50,
  "next": "/crm/prospects/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Test School",
      "email": "test@school.com",
      "stage": "interested",
      "score": 75
    }
  ]
}
```

---

### 2. Get Prospect Detail
Retrieve single prospect details.

**Endpoint:** `GET /crm/prospects/<id>/`

**Authentication:** Required

**Response:**
```json
{
  "id": 1,
  "name": "Test School",
  "email": "test@school.com",
  "contact_name": "Principal",
  "contact_role": "Director",
  "country": "NG",
  "city": "Lagos",
  "stage": "interested",
  "score": 75,
  "priority": "H",
  "budget": 50000,
  "created_at": "2024-01-01T10:00:00Z"
}
```

---

### 3. Create Prospect
Add new prospect.

**Endpoint:** `POST /crm/prospects/`

**Authentication:** Required (CommercialRequiredMixin)

**Request Body:**
```json
{
  "name": "New School",
  "email": "new@school.com",
  "contact_name": "Rector",
  "contact_role": "Director",
  "country": "NG",
  "city": "Abuja",
  "type_of_establishment": "university",
  "phone": "+234xxx",
  "budget": 100000,
  "notes": "Interested in partnership"
}
```

**Response:** (201 Created)
```json
{
  "id": 51,
  "name": "New School",
  "email": "new@school.com",
  "score": 30,
  "priority": "M"
}
```

---

### 4. Update Prospect
Modify prospect data.

**Endpoint:** `PUT /crm/prospects/<id>/`

**Authentication:** Required

**Request Body:** (Similar to Create)

**Response:** (200 OK)

---

### 5. Delete Prospect
Remove prospect.

**Endpoint:** `DELETE /crm/prospects/<id>/`

**Authentication:** Required

**Response:** (204 No Content)

---

### 6. Log Interaction
Create interaction record.

**Endpoint:** `POST /crm/prospects/<id>/interactions/`

**Authentication:** Required

**Request Body:**
```json
{
  "interaction_type": "email",
  "summary": "Sent initial inquiry",
  "outcome": "N",
  "interaction_date": "2024-03-15",
  "next_action_date": "2024-03-20"
}
```

**Response:** (201 Created)

---

## Email Endpoints

### 1. List Email Templates
Get all email templates.

**Endpoint:** `GET /emails/templates/`

**Authentication:** Required

**Response:**
```json
[
  {
    "id": 1,
    "name": "Initial Contact",
    "subject": "Partnership Opportunity",
    "variables": ["school_name", "contact_name"]
  }
]
```

---

### 2. Create Email Enrollment
Enroll prospect in sequence.

**Endpoint:** `POST /emails/enrollments/`

**Authentication:** Required

**Request Body:**
```json
{
  "prospect_id": 1,
  "sequence_id": 1
}
```

**Response:** (201 Created)
```json
{
  "id": 1,
  "prospect": 1,
  "sequence": 1,
  "status": "active",
  "next_send_at": "2024-03-20T10:00:00Z"
}
```

---

### 3. Get Email Logs
Retrieve email sending history.

**Endpoint:** `GET /emails/logs/`

**Authentication:** Required

**Query Parameters:**
- `prospect_id` (optional)
- `status` (optional): pending/sent/failed/opened/clicked/replied

**Response:**
```json
[
  {
    "id": 1,
    "to_email": "test@school.com",
    "subject": "Partnership Opportunity",
    "status": "sent",
    "sent_at": "2024-03-15T10:00:00Z"
  }
]
```

---

## CSV Import

### 1. Import Prospects from CSV
Bulk upload prospects via CSV file.

**Endpoint:** `POST /crm/import/`

**Authentication:** Required (CommercialRequiredMixin)

**Content-Type:** multipart/form-data

**Required Columns:**
- name
- email
- country
- contact_name
- contact_role

**Optional Columns:**
- phone
- city
- type_of_establishment
- budget
- website
- linkedin_url
- notes

**Example CSV:**
```csv
name,email,contact_name,contact_role,country,city,type_of_establishment
University of Lagos,info@unilag.edu.ng,Professor Smith,Director,NG,Lagos,university
Cairo University,admin@cu.edu.eg,Dr. Ahmed,Rector,EG,Cairo,university
```

**Response:** (202 Accepted)
```json
{
  "job_id": 1,
  "status": "pending",
  "total_rows": 50,
  "message": "Import job created. Progress available at /crm/import-jobs/1/"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid request data",
  "details": {
    "email": ["This field is required"]
  }
}
```

### 401 Unauthorized
```json
{
  "error": "Authentication required"
}
```

### 403 Forbidden
```json
{
  "error": "You do not have permission to perform this action"
}
```

### 404 Not Found
```json
{
  "error": "Resource not found"
}
```

### 500 Server Error
```json
{
  "error": "Internal server error",
  "reference_id": "error-uuid-12345"
}
```

---

## Rate Limiting
No rate limiting currently implemented. For production, implement rate limiting via:
- Django-ratelimit
- DRF throttling
- Redis-based rate limiting

---

## Pagination
List endpoints support pagination:
```
GET /crm/prospects/?page=2&page_size=25
```

Default page size: 20
Maximum page size: 100

---

## Filtering
Use query parameters for filtering:
```
GET /crm/prospects/?stage=interested&country=NG&priority=H
```

---

## Sorting
Add `ordering` parameter:
```
GET /crm/prospects/?ordering=-score
GET /crm/prospects/?ordering=created_at
```

---

## Testing API Endpoints

### Using cURL
```bash
# Get KPI data
curl -H "Cookie: sessionid=YOUR_SESSION_ID" \
  http://localhost:8000/analytics/api/kpi-data/

# Create prospect
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=YOUR_SESSION_ID" \
  -d '{"name":"Test School","email":"test@school.com","country":"NG","contact_name":"Director","contact_role":"Admin"}' \
  http://localhost:8000/crm/prospects/
```

### Using Python Requests
```python
import requests
from django.contrib.auth import get_user_model

session = requests.Session()
user = User.objects.get(email='test@example.com')

# Login
response = session.post('http://localhost:8000/accounts/admin-portal/login/', {
    'email': 'test@example.com',
    'password': 'password'
})

# Get data
response = session.get('http://localhost:8000/analytics/api/kpi-data/')
print(response.json())
```

### Using JavaScript Fetch
```javascript
// Get KPI data
fetch('/analytics/api/kpi-data/')
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));

// Create prospect
fetch('/crm/prospects/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': getCookie('csrftoken')
  },
  body: JSON.stringify({
    name: 'Test School',
    email: 'test@school.com',
    country: 'NG'
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

---

## Webhook Integration (Future)
Planned webhook support for:
- Prospect created/updated
- Interaction logged
- Email sent/opened/clicked
- Enrollment status changed

---

## Versioning
Current API Version: 1.0
Future: Support for v2, v3 through `/api/v2/`, `/api/v3/`

---

## Support
For API issues, contact: support@edu-expand.com
API Status: http://localhost:8000/api/status/
