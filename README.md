# 🏔️ Trekking Management Application

A web-based Trekking Management System developed using **Flask**, **SQLite**, **SQLAlchemy**, **Bootstrap**, and **Flask-Login**. The application helps administrators manage treks, staff, bookings, and users while allowing trekkers to book treks and staff members to manage assigned treks.

---

## 📌 Features

### 👨‍💼 Admin
- Admin Login
- Dashboard with statistics
- Add, Edit and Delete Treks
- View all Treks
- Approve or Reject Staff Registrations
- Assign Staff to Treks
- View All Users
- View All Bookings
- Manage Trek Progress

### 👨‍💻 Staff
- Staff Registration
- Login after Admin Approval
- View Assigned Treks
- Update Trek Progress Status
- View Trek Participants

### 🥾 Trekker
- User Registration & Login
- View Available Treks
- Book Trek
- View Booking History
- Update Profile
- Give Ratings & Reviews

---

# 🛠️ Technology Stack

 Technology  Purpose 

 Python      Programming Language 
 Flask       Web Framework 
 SQLite      Database 
 SQLAlchemy   ORM 
 Flask-Login   User Authentication 
 Bootstrap 5   Responsive UI 
 HTML5        Frontend 
 CSS3         Styling 
  Jinja2      Template Engine 



# 📂 Project Structure


Trekking-Management/
│
├── app.py
├── models/
│   └── models.py
│
├── controllers/
│   ├── auth.py
│   ├── admin.py
│   ├── trek.py
│   ├── booking.py
│   └── staff.py
│
├── templates/
│   ├── login.html
│   ├── register.html
│   ├── admin_dashboard.html
│   ├── staff_dashboard.html
│   ├── user_dashboard.html
│   └── ...
│
├── static/
│   ├── css/
│   ├── images/
│   └── js/
│
├── instance/
│   └── trekking.sqlite
│
└── README.md




# 🗄️ Database Design

The application contains the following database tables.

## Users

Stores all registered users.

 Field         Type 

 id            Integer 
 full_name     String 
 email         String 
 password      String (Hashed) 
 role          Admin / Staff / Trekker 
 status        Approved / Pending 
 created_at    DateTime 



## Staff Profiles

Stores additional staff information.

 Field         Type 

 id            Integer 
 user_id       Foreign Key 
 phone         String 
 experience_years   Integer 
 specialization     String 



## Treks

Stores trek details.

 Field          Type 

 id             Integer 
 trek_name      String 
 location       String 
 difficulty     Easy / Moderate / Hard 
 duration_days  Integer 
  available_slots  Integer 
 status             Open / Closed 
 progress_status    Not Started / Ongoing / Completed 
 assigned_staff_id    Foreign Key 



## Bookings

Stores trek booking information.

 Field            Type 

 id               Integer 
 user_id          Foreign Key 
 trek_id          Foreign Key 
 booking_date     DateTime 
 booking_status   Booked 
 payment_status   Paid / Unpaid 



## Reviews

Stores user feedback.

 Field          Type 

 id             Integer 
 user_id        Foreign Key 
 trek_id        Foreign Key
 rating         Integer 
 comment        Text 



# 🔗 Database Relationships

- One User ➜ Many Bookings
- One Trek ➜ Many Bookings
- One Staff ➜ Many Assigned Treks
- One User ➜ One Staff Profile
- One User ➜ Many Reviews
- One Trek ➜ Many Reviews

---

# 🔒 Authentication

- Passwords are securely stored using **Werkzeug Password Hashing**.
- User authentication is handled using **Flask-Login**.
- Role-based access is implemented for:
  - Admin
  - Staff
  - Trekker



# 🚀 Installation

## Clone Repository

```bash
git clone https://github.com/yourusername/Trekking-Management.git
```

Move into project directory

```bash
cd Trekking-Management
```

Create Virtual Environment

```bash
python -m venv venv
```

Activate Virtual Environment

### Windows

```bash
venv\Scripts\activate
```

### Linux / Mac

```bash
source venv/bin/activate
```

Install Dependencies

```bash
pip install -r requirements.txt
```

Run Application

```bash
python app.py
```

Open Browser

```
http://127.0.0.1:5000
```

---

# 📸 Application Modules

- Login
- Registration
- Admin Dashboard
- Staff Dashboard
- User Dashboard
- Trek Management
- Booking Management
- Staff Approval
- Trek Assignment
- Reviews & Ratings
- Profile Management

---

# 📈 Future Enhancements

- Online Payment Gateway
- Email Notifications
- Trek Images Upload
- GPS Location Integration
- Weather Forecast API
- Certificate Generation
- QR Code Based Booking
- Admin Analytics Dashboard

