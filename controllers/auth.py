from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from models.models import db, User, Trek, Booking
from sqlalchemy import or_

from models.models import (
    db,
    User,
    Trek,
    Booking
)
                                     #separate API for html pages
auth = Blueprint("auth", __name__)   #creating all the routes inside a blueprint named as auth

#==========================================================
#registration of a new user at diff - diff role

@auth.route("/register", methods=["GET", "POST"])     #when we open page , get request aati hai or jab kuchh changes krke save krte hai toh post request aati hai
def register():

    if request.method == "POST":
        #if already registered and try to login
        full_name = request.form["full_name"]
        email = request.form["email"].strip().lower()   #suppose user enter User@gmail.com and later tries user@gmail.com
        password = request.form["password"]
        role = request.form["role"]

        if len(full_name.strip()) < 2:
            return "Full name must contain at least 3 characters"

        if len(password) < 6:
            return "Password must contain at least 6 characters"

        if role not in ["trekker", "staff"]:
            return "Invalid role selected"
    
        if "@" not in email or "." not in email:
            return "Invalid email address"

        existing_user = User.query.filter_by(      #it checks out the email in database
            email=email
        ).first()

        if existing_user:                         #if exist 
            return "Email already exists"

        if role == "staff": 
            status = "pending"
        else:
            status = "approved"

#==========================================================
#registeration of a new user

        new_user = User(
            full_name=full_name,
            email=email,
            password=generate_password_hash(password),    #DB doesnt save password directly, firstly convert into hash then save 
            role=role,
            status=status
        )

        db.session.add(new_user)     #it means to add new user in DB 
        db.session.commit()          #save the changes in DB permanently

        return "Registration Successful"

    return render_template("register.html")   #redirect to registration page 

#==========================================================
#login existing user

@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":     #internal code execute when form submitted

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()    #check the email in DB

        if not user:
            return "User not found"

        if not check_password_hash(user.password, password):
            return "Incorrect password"
        
        if user.status == "deactivated":
            return "Your account has been deactivated by Admin."

        if user.role == "staff" and user.status == "pending":
            return "Waiting for Admin Approval"
        
        session["user_id"] = user.id    #with the help of user id, check his role and assign his dashboard 
        session["role"] = user.role

        if user.role == "Admin":
            return redirect(url_for("auth.admin_dashboard"))   #redirect to the admin dashboard 

        elif user.role == "staff":
            return redirect(url_for("auth.staff_dashboard"))

        else:
            return redirect(url_for("auth.user_dashboard"))
    return render_template("login.html")

#==========================================================
#route of pending staff 

@auth.route("/admin/pending_staff")
def pending_staff():

    staff_members = User.query.filter_by(         #if role is staff and status is pending, redirect to pending_staff.html
        role="staff",
        status="pending"
    ).all()

    return render_template(
        "pending_staff.html",
        staff_members=staff_members
    )

#==========================================================
#route of approved staff

@auth.route("/approve_staff/<int:user_id>")
def approve_staff(user_id):

    staff = User.query.get(user_id)

    if staff:                             
        staff.status = "approved"
        db.session.commit()             #save the changes  permanently in DB

    return redirect(url_for("auth.pending_staff"))   #call to the pending staff funct from auth

#==========================================================
#route of admin dashboard

@auth.route("/admin/dashboard")
def admin_dashboard():

    total_users = User.query.filter_by(role="trekker").count()

    total_staff = User.query.filter_by(role="staff",status="approved").count()

    total_treks = Trek.query.count()

    total_bookings = Booking.query.count()

    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        total_staff=total_staff,
        total_treks=total_treks,
        total_bookings=total_bookings
    )

#==========================================================
#route of staff dashboard

@auth.route("/staff/dashboard")
def staff_dashboard():

    staff_id = session["user_id"]

    assigned_treks = Trek.query.filter_by(assigned_staff_id=staff_id).all()

    trek_names = []
    participant_counts = []

    for trek in assigned_treks:

        trek_names.append(trek.trek_name)

        participant_count = Booking.query.filter(
            Booking.trek_id == trek.id,
            Booking.booking_status != "Cancelled"
        ).count()

        participant_counts.append(participant_count)


    assigned_treks_count = len(assigned_treks)

    trek_ids = [trek.id for trek in assigned_treks]

    registered_trekkers_count = Booking.query.filter(
        Booking.trek_id.in_(trek_ids)
    ).count()

    return render_template(
        "staff_dashboard.html",
        assigned_treks=assigned_treks,
        assigned_treks_count=assigned_treks_count,
        registered_trekkers_count=registered_trekkers_count,
        trek_names=trek_names,
        participant_counts=participant_counts
    )

#==========================================================
#staff can update slots from using it 

@auth.route("/staff/update_slots/<int:trek_id>", methods=["GET", "POST"])
def update_slots(trek_id):

    staff_id = session["user_id"]    #staff can update slots

    trek = Trek.query.filter_by(
        id=trek_id,
        assigned_staff_id=staff_id
    ).first_or_404()

    if request.method == "POST":

        available_slots = int(request.form["available_slots"])    #call to the function of avail slots

        if available_slots < 0:
            return "Available slots cannot be negative"

        trek.available_slots = available_slots

        db.session.commit()

        return redirect(url_for("auth.staff_dashboard"))

    return render_template(
        "update_slots.html",
        trek=trek
    )

#==========================================================
#staff can update status from using it 

@auth.route("/staff/update_status/<int:trek_id>", methods=["GET", "POST"])
def update_status(trek_id):

    staff_id = session["user_id"]      #staff can update status

    trek = Trek.query.filter_by(
        id=trek_id,
        assigned_staff_id=staff_id
    ).first_or_404()

    if request.method == "POST":

        trek.status = request.form["status"]

        db.session.commit()

        return redirect(url_for("auth.staff_dashboard"))

    return render_template(
        "update_status.html",
        trek=trek
    )

#==========================================================
#staff can update progress from using it 

@auth.route("/staff/update_progress/<int:trek_id>", methods=["GET", "POST"])
def update_progress(trek_id):

    staff_id = session["user_id"]    #staff can update progress 

    trek = Trek.query.filter_by(
        id=trek_id,
        assigned_staff_id=staff_id
    ).first_or_404()

    if request.method == "POST":

        trek.progress_status = request.form["progress_status"]

        db.session.commit()

        return redirect(url_for("auth.staff_dashboard"))

    return render_template(
        "update_progress.html",
        trek=trek
    )

#==========================================================
#staff can view participants from using it 

@auth.route("/staff/participants/<int:trek_id>")
def view_participants(trek_id):

    staff_id = session["user_id"]       #staff can view participants

    # Ensure trek belongs to logged-in staff
    trek = Trek.query.filter_by(
        id=trek_id,
        assigned_staff_id=staff_id
    ).first_or_404()

    bookings = Booking.query.filter_by(
        trek_id=trek.id
    ).all()

    return render_template(
        "view_participants.html",
        trek=trek,
        bookings=bookings
    )

#==========================================================
#staff can view staff profile from using it 

@auth.route("/staff/profile", methods=["GET", "POST"])
def staff_profile():

    staff = User.query.get_or_404(session["user_id"])  #here staff search about other staff by using user id of that staff
                                                        #if not found show 404 error
    if request.method == "POST":

        staff.full_name = request.form["full_name"]
        staff.email = request.form["email"]

        password = request.form["password"]

        if password:
            staff.password = generate_password_hash(password)

        db.session.commit()

        return redirect(url_for("auth.staff_dashboard"))

    return render_template(
        "staff_profile.html",
        staff=staff
    )

#==========================================================
#staff can remove participants from using it 

@auth.route("/staff/remove_participant/<int:booking_id>")
def remove_participant(booking_id):

    staff_id = session["user_id"]

    booking = Booking.query.get_or_404(booking_id)

    trek = Trek.query.filter_by(
        id=booking.trek_id,
        assigned_staff_id=staff_id
    ).first_or_404()

    if booking.booking_status != "Cancelled":

        booking.booking_status = "Cancelled"

        trek.available_slots += 1

        db.session.commit()

    return redirect(
        url_for(
            "auth.view_participants",
            trek_id=trek.id                   #by using trek id staff can view participants and can remove  
        )
    )

#==========================================================
#route of USER DASHBOARD

@auth.route("/user/dashboard")
def user_dashboard():

    user_id = session["user_id"]

    booked_count = Booking.query.filter_by(       #user can see his total bookings
        user_id=user_id,                          
        booking_status="Booked"
    ).count()

    cancelled_count = Booking.query.filter_by(     #user can see his total cancelled bookings
        user_id=user_id,
        booking_status="Cancelled"
    ).count()

    completed_count = Booking.query.filter_by(     #user can see his total completed bookings
        user_id=user_id,
        booking_status="Completed"
    ).count()

    return render_template(
        "user_dashboard.html",
        booked_count=booked_count,
        cancelled_count=cancelled_count,
        completed_count=completed_count
    )

#==========================================================
#route of ADD TREKS 

@auth.route("/admin/add_trek", methods=["GET", "POST"])
def add_trek():

    if request.method == "POST":

        trek_name = request.form["trek_name"].strip()     #form making for edit
        location = request.form["location"].strip()
        duration_days = int(request.form["duration_days"])
        available_slots = int(request.form["available_slots"])

        if len(trek_name) < 2:
            return "Trek name must contain at least 2 characters"

        if not location:
            return "Location is required"

        if duration_days < 1:
            return "Duration must be at least 1 day"

        if available_slots < 1:
            return "Available slots must be at least 1"

        trek = Trek(
            trek_name=trek_name,             #form fill up after making form
            location=location,
            difficulty=request.form["difficulty"],      #redirect to difficulty form in which we have 3 option 
            duration_days=duration_days,
            available_slots=available_slots
        )

        db.session.add(trek)     #add new treks
        db.session.commit()

        return redirect(url_for("auth.admin_dashboard"))     #changes  appeared at admin dashboard

    return render_template("add_trek.html")

#==========================================================
#route of VIEW TREKS

@auth.route("/admin/treks")
def view_treks():

    search = request.args.get("search")

    if search:

        treks = Trek.query.filter(
            Trek.trek_name.ilike(f"%{search}%")
        ).all()

    else:

        treks = Trek.query.all()

    return render_template(
        "view_treks.html",
        treks=treks
    )

#==========================================================
#route of delete trek

@auth.route("/admin/delete_trek/<int:id>")
def delete_trek(id):

    trek = Trek.query.get_or_404(id)

    db.session.delete(trek)        #delete the trek 
    db.session.commit()

    return redirect(url_for("auth.view_treks"))     #changes appeared in view treks 


#==========================================================
#route of edit trek

@auth.route("/admin/edit_trek/<int:id>", methods=["GET", "POST"])
def edit_trek(id):

    trek = Trek.query.get_or_404(id)     #if avail then show otherwise error 

    if request.method == "POST":

        trek_name = request.form["trek_name"].strip()            #from making
        location = request.form["location"].strip()
        duration_days = int(request.form["duration_days"])
        available_slots = int(request.form["available_slots"])

        if len(trek_name) < 2:
            return "Trek name must contain at least 3 characters"

        if not location:
            return "Location is required"

        if duration_days < 1:
            return "Duration must be at least 1 day"

        if available_slots < 1:
            return "Available slots must be at least 1"

        trek.trek_name = trek_name
        trek.location = location                          #form fill up 
        trek.difficulty = request.form["difficulty"]
        trek.duration_days = duration_days
        trek.available_slots = available_slots

        db.session.commit()

        return redirect(url_for("auth.view_treks"))

    return render_template(
        "edit_trek.html",
        trek=trek
    )


#==========================================================
#route of view staff which is seen by admin

@auth.route("/admin/staff")
def view_staff():

    search = request.args.get("search")

    if search:
                            #if admin search staff by name, then DB shows result only when it satisfy these three condition 
        staff_members = User.query.filter(
            User.role == "staff",
            User.status == "approved",
            User.full_name.ilike(f"%{search}%")   #name will be pick up from search bar 
        ).all()

    else:

        staff_members = User.query.filter_by(      #if not searched by admin then it shows all approved staff
            role="staff",
            status="approved"
        ).all()

    return render_template(
        "view_staff.html",
        staff_members=staff_members
    )

#==========================================================
#route of assign staff by admin for a trek

@auth.route("/admin/assign_staff/<int:trek_id>", methods=["GET", "POST"])
def assign_staff(trek_id):

    trek = Trek.query.get_or_404(trek_id)

    staff_members = User.query.filter_by(
        role="staff",
        status="approved"
    ).all()

    if request.method == "POST":

        trek.assigned_staff_id = request.form["staff_id"]

        db.session.commit()

        return redirect(url_for("auth.view_treks"))

    return render_template(
        "assign_staff.html",
        trek=trek,
        staff_members=staff_members
    )

#==========================================================
#route of remove staff by admin from a trek

@auth.route("/admin/remove_staff/<int:trek_id>")
def remove_staff(trek_id):

    trek = Trek.query.get_or_404(trek_id)

    trek.assigned_staff_id = None  #staff id deleted

    db.session.commit()

    return redirect(url_for("auth.view_treks"))

#==========================================================
#route of view user by admin

@auth.route("/admin/users")
def view_users():

    search = request.args.get("search")

    if search:

        users = User.query.filter(        #admin can search user by mail, name , or user id

            or_(

                User.full_name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.id.cast(db.String).ilike(f"%{search}%")

            )

        ).all()

    else:

        users = User.query.all()   #otherwise show all the users 

    return render_template(
        "view_users.html",
        users=users
    )

#==========================================================
#route to view user treks

@auth.route("/user/treks")
def user_treks():

    search = request.args.get("search")            #call to search function
    difficulty = request.args.get("difficulty")    #call to difficulty funct

    query = Trek.query.filter_by(status="Open")    #query to DB to show only that treks whose status is open

    if search:
        query = query.filter(                     #user can search treks by location
            Trek.location.ilike(f"%{search}%")
        )

    if difficulty:                               #user can search treks by location
        query = query.filter(
            Trek.difficulty == difficulty
        )

    treks = query.all()                          #otherwise show all treks

    return render_template(
        "user_treks.html",
        treks=treks
    )

#==========================================================
#route of book trek

@auth.route("/user/book_trek/<int:trek_id>")
def book_trek(trek_id):

    user_id = session["user_id"]

    trek = Trek.query.get_or_404(trek_id)

    if trek.status != "Open":
        return "Booking is allowed only for Open treks"

    if trek.available_slots <= 0:
        return "No slots available for this trek"

    existing_booking = Booking.query.filter(        #if user already booked the trek
        Booking.user_id == user_id,
        Booking.trek_id == trek_id,
        Booking.booking_status != "Cancelled"
    ).first()

    if existing_booking:
        return "You have already booked this trek"

    booking = Booking(            #booking a new trek
        user_id=user_id,
        trek_id=trek_id,
        booking_status="Booked"
    )

    db.session.add(booking)
    trek.available_slots -= 1
    db.session.commit()

    return "Trek Booked Successfully"

#==========================================================
#route of user can view my bookings

@auth.route("/user/bookings")
def my_bookings():

    user_id = session["user_id"]

    bookings = Booking.query.filter_by(
        user_id=user_id
    ).all()

    return render_template(
        "my_bookings.html",
        bookings=bookings
    )

#==========================================================
#route of cancel booking

@auth.route("/user/cancel_booking/<int:booking_id>")
def cancel_booking(booking_id):

    user_id = session["user_id"]

    booking = Booking.query.filter_by(
        id=booking_id,
        user_id=user_id
    ).first_or_404()

    if booking.booking_status != "Cancelled":

        booking.booking_status = "Cancelled"

        booking.trek.available_slots += 1

        db.session.commit()

    return redirect(url_for("auth.my_bookings"))

#==========================================================
#route of user trekking history

@auth.route("/user/trekking_history")
def trekking_history():

    user_id = session["user_id"]

    completed_bookings = Booking.query.filter_by(
        user_id=user_id,
        booking_status="Completed"
    ).all()

    return render_template(
        "trekking_history.html",
        bookings=completed_bookings
    )

#==========================================================
#route of user profile

@auth.route("/user/profile", methods=["GET", "POST"])
def user_profile():

    user = User.query.get_or_404(session["user_id"])

    if request.method == "POST":

        user.full_name = request.form["full_name"]
        user.email = request.form["email"]
        password = request.form["password"]

        if password:
            user.password = generate_password_hash(password)

        db.session.commit()

        return redirect(url_for("auth.user_dashboard"))

    return render_template(
        "user_profile.html",
        user=user
    )

#==========================================================
#route of view bookings by admin

@auth.route("/admin/bookings")
def view_bookings():

    bookings = Booking.query.all()

    return render_template(
        "view_bookings.html",
        bookings=bookings
    )

#==========================================================
#route of admin can view trekking history 

@auth.route("/admin/trekking_history")
def admin_trekking_history():

    completed_bookings = Booking.query.filter_by(
        booking_status="Completed"
    ).all()

    return render_template(
        "admin_trekking_history.html",
        bookings=completed_bookings
    )

#==========================================================
#route of admin can view complete booking

@auth.route("/admin/complete_booking/<int:booking_id>")
def complete_booking(booking_id):

    booking = Booking.query.get_or_404(booking_id)

    booking.booking_status = "Completed"

    db.session.commit()

    return redirect(url_for("auth.view_bookings"))

#==========================================================
#route of mark paid by admin

@auth.route("/admin/mark_paid/<int:booking_id>")
def mark_paid(booking_id):

    booking = Booking.query.get_or_404(booking_id)

    booking.payment_status = "Paid"

    db.session.commit()

    return redirect(url_for("auth.view_bookings"))

#==========================================================
#route of deactivate user by admin

@auth.route("/admin/deactivate_user/<int:user_id>")
def deactivate_user(user_id):

    user = User.query.get_or_404(user_id)

    user.status = "deactivated"

    db.session.commit()

    return redirect(url_for("auth.view_users"))

#==========================================================
#route of activate user by admin

@auth.route("/admin/activate_user/<int:user_id>")
def activate_user(user_id):

    user = User.query.get_or_404(user_id)

    user.status = "approved"

    db.session.commit()

    return redirect(url_for("auth.view_users"))

