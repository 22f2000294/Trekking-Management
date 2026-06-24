from flask import Blueprint, render_template, request, redirect, url_for
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from models.models import db, User

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
            return render_template("admin_dashboard.html")

        elif user.role == "staff":
            return render_template("staff_dashboard.html")

        else:
            return render_template("user_dashboard.html")
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