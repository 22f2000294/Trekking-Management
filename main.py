from flask import Flask
from models.models import db, User
from werkzeug.security import generate_password_hash
from controllers.auth import auth
from controllers.api import api
from flask_login import LoginManager  


app = Flask(__name__)

login_manager = LoginManager()       #it helps to redirect on a page when u logged in 
login_manager.init_app(app)
login_manager.login_view = "auth.login"
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

app.secret_key = "trekking-secret-key"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///trekking.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
app.register_blueprint(auth)
app.register_blueprint(api)


with app.app_context():

    db.create_all()

    admin = User.query.filter_by(
        email="rkm_admin@trekking.com"
    ).first()

    if not admin:

        admin_user = User(
            full_name="System Admin",
            email="rkm_admin@trekking.com",
            password=generate_password_hash("@rkm123"),
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


@app.route("/")
def home():

    return "Trekking Management Application"


if __name__ == "__main__":

    app.run(debug=True)