from flask import Flask
from models.models import db, User
from werkzeug.security import generate_password_hash
from controllers.auth import auth

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///trekking.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
app.register_blueprint(auth)


with app.app_context():
    db.create_all()

    # Create default admin if not exists
    admin = User.query.filter_by(email="admin@trekking.com").first()

    if not admin:
        admin_user = User(
            full_name="System Admin",
            email="admin@trekking.com",
            password=generate_password_hash("admin123"),
            role="Admin"
        )

        db.session.add(admin_user)
        db.session.commit()

    all_users = User.query.all()

    print("\n===== USERS IN DATABASE =====")
    for user in all_users:
        print(
            user.id,
            user.full_name,
            user.email,
            user.role,
            user.status
        )
    print("=============================\n")
    #print("Default Admin Created Successfully")

@app.route("/")
def home():
    return "Trekking Management Application"

if __name__ == "__main__":
    app.run(debug=True)