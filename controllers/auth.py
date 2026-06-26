from flask import Blueprint, render_template, request, redirect, url_for
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

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

        if user.role == "staff" and user.status == "pending":
            return "Waiting for Admin Approval"

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
    return render_template("staff_dashboard.html")


@auth.route("/user/dashboard")
def user_dashboard():
    return render_template("user_dashboard.html")

@auth.route("/admin/add_trek", methods=["GET", "POST"])
def add_trek():

    if request.method == "POST":

        trek = Trek(
            trek_name=request.form["trek_name"],
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
        trek.difficulty = request.form["difficulty"]
        trek.duration_days = request.form["duration_days"]
        trek.available_slots = request.form["available_slots"]

        db.session.commit()

        return redirect(url_for("auth.view_treks"))

    return render_template(
        "edit_trek.html",
        trek=trek
    )