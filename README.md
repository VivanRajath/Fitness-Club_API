#  Fitness Club Booking API Assessment for Python Developer(Omnify)

A Django RESTful API for managing fitness class bookings. Clients can view available classes, book sessions (with validations), and fetch their booking history. Designed to enforce time-bound, slot-based, and per-user constraints.

---

## 🚀 Features

- List all available fitness classes
- Book a class (with validations):
  - Validate Emails
  - No duplicate bookings
  - Maximum 2 bookings per 24 hours
  - No bookings within 4 hours of class time
  - Prevent double-booking
  - No Overlapping Sessions
  - Class must have available slots
- View all bookings for a client via email

---

## 📦 Tech Stack

- **Backend**: Django, Django REST Framework
- **Database**: SQLite (default, easy to switch)
- **Tests**: Django `TestCase` + DRF `APIClient`

---

## 🔧 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/VivanRajath/Fitness-Club_API.git
cd Fitness-Club_API
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate  # For Windows
# source venv/bin/activate  # For macOS/Linux
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. (Optional) Seed Sample Data

```bash
python seed_data.py
```

### 6. Run the Server

```bash
python manage.py runserver
```

---

## 📡 API Endpoints

### Get All Classes

```
GET /api/classes/
```

### Book a Class

```
POST /api/book/
```

**Request Body:**

```json
{
  "class_id": 1,
  "client_name": "John Doe",
  "client_email": "john@example.com"
}
```

### Get Bookings by Email

```
GET /api/bookings/?email=john@example.com
```

---

## 🧪 Run Tests

```bash
python manage.py test bookings
```

---


