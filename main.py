from flask import Flask
from models.models import db, User
from werkzeug.security import generate_password_hash

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///trekking.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

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

        print("Default Admin Created Successfully")

@app.route("/")
def home():
    return "Trekking Management Application"

if __name__ == "__main__":
    app.run(debug=True)