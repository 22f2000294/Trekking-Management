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

auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        full_name = request.form["full_name"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:
            return "Email already exists"

        if role == "staff":
            status = "pending"
        else:
            status = "approved"

        new_user = User(
            full_name=full_name,
            email=email,
            password=generate_password_hash(password),
            role=role,
            status=status
        )

        db.session.add(new_user)
        db.session.commit()

        return "Registration Successful"

    return render_template("register.html")

@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if not user:
            return "User not found"

        if not check_password_hash(user.password, password):
            return "Incorrect password"
        
        if user.status == "deactivated":
            return "Your account has been deactivated by Admin."

        if user.role == "staff" and user.status == "pending":
            return "Waiting for Admin Approval"
        
        session["user_id"] = user.id
        session["role"] = user.role

        if user.role == "Admin":
            return redirect(url_for("auth.admin_dashboard"))

        elif user.role == "staff":
            return redirect(url_for("auth.staff_dashboard"))

        else:
            return redirect(url_for("auth.user_dashboard"))
    return render_template("login.html")

@auth.route("/admin/pending_staff")
def pending_staff():

    staff_members = User.query.filter_by(
        role="staff",
        status="pending"
    ).all()

    return render_template(
        "pending_staff.html",
        staff_members=staff_members
    )

@auth.route("/approve_staff/<int:user_id>")
def approve_staff(user_id):

    staff = User.query.get(user_id)

    if staff:
        staff.status = "approved"
        db.session.commit()

    return redirect(url_for("auth.pending_staff"))

@auth.route("/admin/dashboard")
def admin_dashboard():

    total_users = User.query.filter_by(role="trekker").count()

    total_staff = User.query.filter_by(
        role="staff",
        status="approved"
    ).count()

    total_treks = Trek.query.count()

    total_bookings = Booking.query.count()

    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        total_staff=total_staff,
        total_treks=total_treks,
        total_bookings=total_bookings
    )


@auth.route("/staff/dashboard")
def staff_dashboard():

    staff_id = session["user_id"]

    assigned_treks = Trek.query.filter_by(
        assigned_staff_id=staff_id
    ).all()

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


@auth.route("/staff/update_slots/<int:trek_id>", methods=["GET", "POST"])
def update_slots(trek_id):

    staff_id = session["user_id"]

    trek = Trek.query.filter_by(
        id=trek_id,
        assigned_staff_id=staff_id
    ).first_or_404()

    if request.method == "POST":

        trek.available_slots = request.form["available_slots"]

        db.session.commit()

        return redirect(url_for("auth.staff_dashboard"))

    return render_template(
        "update_slots.html",
        trek=trek
    )


@auth.route("/staff/update_status/<int:trek_id>", methods=["GET", "POST"])
def update_status(trek_id):

    staff_id = session["user_id"]

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


@auth.route("/staff/update_progress/<int:trek_id>", methods=["GET", "POST"])
def update_progress(trek_id):

    staff_id = session["user_id"]

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


@auth.route("/staff/participants/<int:trek_id>")
def view_participants(trek_id):

    staff_id = session["user_id"]

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


@auth.route("/staff/profile", methods=["GET", "POST"])
def staff_profile():

    staff = User.query.get_or_404(session["user_id"])

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
            trek_id=trek.id
        )
    )

@auth.route("/user/dashboard")
def user_dashboard():

    user_id = session["user_id"]

    booked_count = Booking.query.filter_by(
        user_id=user_id,
        booking_status="Booked"
    ).count()

    cancelled_count = Booking.query.filter_by(
        user_id=user_id,
        booking_status="Cancelled"
    ).count()

    completed_count = Booking.query.filter_by(
        user_id=user_id,
        booking_status="Completed"
    ).count()

    return render_template(
        "user_dashboard.html",
        booked_count=booked_count,
        cancelled_count=cancelled_count,
        completed_count=completed_count
    )

@auth.route("/admin/add_trek", methods=["GET", "POST"])
def add_trek():

    if request.method == "POST":

        trek = Trek(
            trek_name=request.form["trek_name"],
            location = request.form["location"],
            difficulty=request.form["difficulty"],
            duration_days=request.form["duration_days"],
            available_slots=request.form["available_slots"]
        )

        db.session.add(trek)
        db.session.commit()

        return redirect(url_for("auth.admin_dashboard"))

    return render_template("add_trek.html")


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

@auth.route("/admin/delete_trek/<int:id>")
def delete_trek(id):

    trek = Trek.query.get_or_404(id)

    db.session.delete(trek)
    db.session.commit()

    return redirect(url_for("auth.view_treks"))


@auth.route("/admin/edit_trek/<int:id>", methods=["GET", "POST"])
def edit_trek(id):

    trek = Trek.query.get_or_404(id)

    if request.method == "POST":

        trek.trek_name = request.form["trek_name"]
        trek.location = request.form["location"]
        trek.difficulty = request.form["difficulty"]
        trek.duration_days = request.form["duration_days"]
        trek.available_slots = request.form["available_slots"]

        db.session.commit()

        return redirect(url_for("auth.view_treks"))

    return render_template(
        "edit_trek.html",
        trek=trek
    )


@auth.route("/admin/staff")
def view_staff():

    search = request.args.get("search")

    if search:

        staff_members = User.query.filter(
            User.role == "staff",
            User.status == "approved",
            User.full_name.ilike(f"%{search}%")
        ).all()

    else:

        staff_members = User.query.filter_by(
            role="staff",
            status="approved"
        ).all()

    return render_template(
        "view_staff.html",
        staff_members=staff_members
    )

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


@auth.route("/admin/remove_staff/<int:trek_id>")
def remove_staff(trek_id):

    trek = Trek.query.get_or_404(trek_id)

    trek.assigned_staff_id = None

    db.session.commit()

    return redirect(url_for("auth.view_treks"))

@auth.route("/admin/users")
def view_users():

    search = request.args.get("search")

    if search:

        users = User.query.filter(

            or_(

                User.full_name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.id.cast(db.String).ilike(f"%{search}%")

            )

        ).all()

    else:

        users = User.query.all()

    return render_template(
        "view_users.html",
        users=users
    )


@auth.route("/user/treks")
def user_treks():

    search = request.args.get("search")
    difficulty = request.args.get("difficulty")

    query = Trek.query.filter_by(status="Open")

    if search:
        query = query.filter(
            Trek.location.ilike(f"%{search}%")
        )

    if difficulty:
        query = query.filter(
            Trek.difficulty == difficulty
        )

    treks = query.all()

    return render_template(
        "user_treks.html",
        treks=treks
    )

@auth.route("/user/book_trek/<int:trek_id>")
def book_trek(trek_id):

    user_id = session["user_id"]

    trek = Trek.query.get_or_404(trek_id)

    if trek.status != "Open":
        return "Booking is allowed only for Open treks"

    if trek.available_slots <= 0:
        return "No slots available for this trek"

    existing_booking = Booking.query.filter(
        Booking.user_id == user_id,
        Booking.trek_id == trek_id,
        Booking.booking_status != "Cancelled"
    ).first()

    if existing_booking:
        return "You have already booked this trek"

    booking = Booking(
        user_id=user_id,
        trek_id=trek_id,
        booking_status="Booked"
    )

    db.session.add(booking)
    trek.available_slots -= 1
    db.session.commit()

    return "Trek Booked Successfully"


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


@auth.route("/admin/bookings")
def view_bookings():

    bookings = Booking.query.all()

    return render_template(
        "view_bookings.html",
        bookings=bookings
    )


@auth.route("/admin/trekking_history")
def admin_trekking_history():

    completed_bookings = Booking.query.filter_by(
        booking_status="Completed"
    ).all()

    return render_template(
        "admin_trekking_history.html",
        bookings=completed_bookings
    )


@auth.route("/admin/complete_booking/<int:booking_id>")
def complete_booking(booking_id):

    booking = Booking.query.get_or_404(booking_id)

    booking.booking_status = "Completed"

    db.session.commit()

    return redirect(url_for("auth.view_bookings"))


@auth.route("/admin/mark_paid/<int:booking_id>")
def mark_paid(booking_id):

    booking = Booking.query.get_or_404(booking_id)

    booking.payment_status = "Paid"

    db.session.commit()

    return redirect(url_for("auth.view_bookings"))

@auth.route("/admin/deactivate_user/<int:user_id>")
def deactivate_user(user_id):

    user = User.query.get_or_404(user_id)

    user.status = "deactivated"

    db.session.commit()

    return redirect(url_for("auth.view_users"))


@auth.route("/admin/activate_user/<int:user_id>")
def activate_user(user_id):

    user = User.query.get_or_404(user_id)

    user.status = "approved"

    db.session.commit()

    return redirect(url_for("auth.view_users"))

