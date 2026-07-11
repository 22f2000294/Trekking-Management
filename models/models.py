from werkzeug.security import generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()  #It acts as a translator b/w python and DB


#Instruction to DB to create DB table for USERS

class User(db.Model):     
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20),default="approved")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bookings = db.relationship(         #defines relationship b/w user and bookings bcoz  1 user can have multi bookings
        "Booking",
        backref="user",
        lazy=True
    )

    assigned_treks = db.relationship(     #defines relationship b/w staff and treks bcoz  1 staff can be assign multi treks
    "Trek",
    foreign_keys="Trek.assigned_staff_id",
    backref="assigned_staff",
    lazy=True
    )

#Instruction to DB to create DB table for STAFF

class StaffProfile(db.Model):           
    __tablename__ = "staff_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey("users.id"),nullable=False)
    phone = db.Column(db.String(15))
    experience_years = db.Column(db.Integer)
    specialization = db.Column(db.String(100))

#Instruction to DB to create DB table for TREKS

class Trek(db.Model):
    __tablename__ = "treks"
    id = db.Column(db.Integer, primary_key=True)
    trek_name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    difficulty = db.Column(db.String(50))
    duration_days = db.Column(db.Integer)
    available_slots = db.Column(db.Integer)
    status = db.Column(db.String(20),default="Open")
    progress_status = db.Column(db.String(20),default="Not Started")
    assigned_staff_id = db.Column(db.Integer,db.ForeignKey("users.id"))

    bookings = db.relationship(           #defines relationship b/w trek and bookings bcoz  1 trek can have multi booking
        "Booking",
        backref="trek",
        lazy=True
    )

#Instruction to DB to create DB table for BOOKINGS

class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey("users.id"),nullable=False)
    trek_id = db.Column(db.Integer,db.ForeignKey("treks.id"),nullable=False)
    booking_date = db.Column(db.DateTime,default=datetime.utcnow)
    booking_status = db.Column(db.String(20),default="Booked")
    payment_status = db.Column(db.String(20),default="Unpaid")

#Instruction to DB to create DB table for REVIEWS
class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey("users.id"))
    trek_id = db.Column(db.Integer,db.ForeignKey("treks.id"))
    rating = db.Column(db.Integer)
    comment = db.Column(db.Text)