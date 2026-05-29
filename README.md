# FoodRescue.pk — Web Application

**Assignment 4 | Software Engineering Concepts**
**Air University Islamabad | BSSE-2 Section B | Spring 2026**

| Student | Roll No | Module |
|---------|---------|--------|
| Ansa Nisar | 2502912 | Module 1 — Login & Registration (Major) — Web |
| Fatima Bibi | 2502854 | Module 2 — Food Listing Management (Minor) — Web |

**Supervisor:** Dr. Zulfiqar Ali

---

## Tech Stack
- **Backend:** Python 3.12 / Django 5.1.4
- **Database:** SQLite3
- **Frontend:** HTML5, CSS3 (Poppins font, green theme)
- **Charts:** Chart.js (CDN)

---

## Setup Instructions

### Step 1 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 2 — Create database tables
```bash
python manage.py makemigrations accounts
python manage.py makemigrations listings
python manage.py migrate
```

### Step 3 — Create admin account
```bash
python manage.py createsuperuser
```

### Step 4 — Run server
```bash
python manage.py runserver
```

### Step 5 — Open browser
```
http://127.0.0.1:8000
```

---

## Test Accounts (create via registration)

| Role | How to create |
|------|--------------|
| Donor | Register at /register/donor/ |
| NGO | Register at /register/ngo/ then approve via admin |
| Admin | python manage.py createsuperuser |

---

## Modules Implemented

### Module 1 — Login & Registration (Ansa Nisar)
- Landing page with stats
- Donor registration (instant approval)
- NGO registration (admin approval required)
- Role-based login with status checks
- Admin panel (approve/reject/suspend users)
- Password change & profile update
- In-app notifications
- Session management (30 min timeout)

### Module 2 — Food Listing Management (Fatima Bibi)
- Create food listings (photo upload, category, pickup window)
- Auto-expire listings after pickup window
- Edit & delete active listings
- NGO live feed with filters (category, area, sort)
- Claim food with pickup scheduling
- Mark claim complete / cancel claim
- Donation history
- Analytics with charts (Chart.js)
- CSV export
- Certificates page (unlocks at 15 completions)

---

## Project Structure
```
foodrescue2/
├── manage.py
├── requirements.txt          ← Django==5.1.4
├── README.md
├── foodrescue/
│   ├── settings.py
│   └── urls.py
├── accounts/                 ← Module 1
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── templates/accounts/
├── listings/                 ← Module 2
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── templates/listings/
├── templates/
│   └── base.html
└── static/css/style.css
```
