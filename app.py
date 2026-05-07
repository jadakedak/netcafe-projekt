from flask import Flask, render_template, request, redirect, url_for, flash
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "myassisonfire"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
CORS(app)

db = SQLAlchemy(app)

class User(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    fornavn     = db.Column(db.String(50), nullable=False)
    efternavn   = db.Column(db.String(50), nullable=False)
    email       = db.Column(db.String(120), unique=True, nullable=False)
    brugernavn  = db.Column(db.String(50), unique=True, nullable=False)
    adgangskode = db.Column(db.String(200), nullable=False)

# FUNCTIONS
def remove_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return True
    return False

def get_user_by_email(email):
    return User.query.filter_by(email=email).first()

def get_user_by_username(username):
    return User.query.filter_by(brugernavn=username).first()

def clear_users():
    num_rows_deleted = db.session.query(User).delete()
    db.session.commit()
    return num_rows_deleted


# ENDPOINTS
@app.route("/reset", methods=["GET"])
def index():
    clear_users()
    return render_template("index.html")

@app.route("/register", methods=["GET"])
def register():
    return render_template("register.html")

@app.route("/login", methods=["GET"])
def login():
    return render_template("login.html")

@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json()

    if User.query.filter_by(email=data["email"]).first():
        return {"message": "Email already in use"}, 409

    if User.query.filter_by(brugernavn=data["username"]).first():
        return {"message": "Username already taken"}, 409

    new_user = User(
        fornavn=data["fornavn"],
        efternavn=data["efternavn"],
        email=data["email"],
        brugernavn=data["username"],
        adgangskode=data["password"],  # hash with bcrypt before production
    )
    db.session.add(new_user)
    db.session.commit()

    return {"message": "User registered successfully"}, 201


# DEBUG ENDPOINTS
@app.route("/api/test", methods=["GET"])
def api_test():
    # here i will list all users in the database along with their parameters
    users = User.query.all()
    user_list = []
    for user in users:
        user_list.append({
            "id": user.id,
            "fornavn": user.fornavn,
            "efternavn": user.efternavn,
            "email": user.email,
            "brugernavn": user.brugernavn,
            "adgangskode": user.adgangskode
        })
    return {"users": user_list}


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
