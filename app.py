from uuid import uuid4
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_cors import CORS
import flask_socketio as fsock
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from asyncio import run
from threading import Thread

### DOING:
# - admin panel for user and menu management

### TODO: 
# implement bcrypt for password hashing
# make connector script for clients to connect to socketio server
# implement computer management (add/remove computers, track connection times)
# implement menu management endpoint (add/remove menu items, get menu items)

app = Flask(__name__)
app.secret_key = "myassisonfire"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
CORS(app)

socketio = fsock.SocketIO(app, cors_allowed_origins="*")
db = SQLAlchemy(app)

class User(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    userid      = db.Column(db.String(50), unique=True, nullable=False)
    admin       = db.Column(db.Boolean, default=False)
    fornavn     = db.Column(db.String(50), nullable=False)
    efternavn   = db.Column(db.String(50), nullable=False)
    email       = db.Column(db.String(120), unique=True, nullable=False)
    brugernavn  = db.Column(db.String(50), unique=True, nullable=False)
    adgangskode = db.Column(db.String(200), nullable=False)

class Menuitem(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    navn        = db.Column(db.String(100), nullable=False)
    beskrivelse  = db.Column(db.String(500), nullable=False)
    pris        = db.Column(db.Float, nullable=False)

class Computer(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    pcid            = db.Column(db.String(50), unique=True, nullable=False)
    pcname          = db.Column(db.String(100), nullable=False)
    user            = db.Column(db.String(50), nullable=False)
    connected       = db.Column(db.Boolean, default=True)
    connection_date = db.Column(db.DateTime, nullable=False)

# SOCKET IO ENDPOINTS
@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")
    
@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")
    
@socketio.on('message')
def handle_message(msg):
    type = msg["type"]
    
    if type == "registration":
        exists = Computer.query.filter_by(pcid=msg["pcid"]).first()
        if exists:
            print("Computer already registered")
            return {"type": "registration", "success": False, "message": "Computer already registered"}, 400
        
        try:
            new_pc = Computer(
                pcid=msg["pcid"],
                pcname=msg["pcname"],
                user=msg["user"],
                connection_date=datetime.now()
            )
            db.session.add(new_pc)
            db.session.commit()
            print("Computer registered successfully")
            return {"type": "registration", "success": True, "message": "Computer registered successfully"}, 200
        except Exception as e:
            print("Error registering computer:", e)
            return {"type": "registration", "success": False, "message": str(e)}, 500
    print(f"Received message: {msg}")


# USER FUNCTIONS
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


# MENUITEM FUNCTIONS
def add_menuitem(navn, beskrivelse, pris):
    new_item = Menuitem(navn=navn, beskrivelse=beskrivelse, pris=pris)
    db.session.add(new_item)
    db.session.commit()
    return new_item

def remove_menuitem(item_id):
    item = Menuitem.query.get(item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
        return True
    return False

def get_menuitems():
    return Menuitem.query.all()


# this is for checking if the user is logged in on the frontend, can be used to conditionally render elements based on login status
@app.route('/api/me')
def me():
    if 'user_id' in session:
        return jsonify({'logged_in': True, 'user_id': session['user_id']})
    return jsonify({'logged_in': False})

@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.clear()
    return {"success": True}, 200

# ENDPOINTS
@app.route("/<userid>/home", methods=["GET"])
def home(userid):
    is_admin = False
    if 'user_id' in session:
        user = User.query.filter_by(userid=userid).first()
        is_admin = user.admin if user else False
    return render_template("index.html", userid=userid, is_admin=is_admin)

@app.route("/<userid>/profile", methods=["GET"])
def profile(userid):
    user = User.query.filter_by(userid=userid).first()
    if not user:
        flash("User not found", "danger")
        return redirect(url_for("home", userid=userid))
    return render_template("profile.html", user=user)

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
        userid=str(uuid4()),  # Generate a unique user ID
    )
    db.session.add(new_user)
    db.session.commit()

    return {"message": "User registered successfully"}, 201

@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json()
    user = get_user_by_username(data["brugernavn"])
    
    if user and user.adgangskode == data["adgangskode"]:
        session['user_id'] = user.userid
        return {"success": True, "user_id": user.userid}, 200
    return {"message": "Invalid username or password"}, 401


@app.route("/api/usercreds/<userid>", methods=["GET"])
def api_usercreds(userid):
    if 'user_id' in session:
        admin_check = User.query.filter_by(userid=session['user_id']).first()
        if admin_check.admin == False:
            return {"message": "Unauthorized"}, 401
    else:
        return {"message": "Unauthorized"}, 401
    
    user = User.query.filter_by(userid=userid).first()
    if not user:
        return {"message": "User not found"}, 404
    return user, 200

@app.route("/api/profileinfo", methods=["GET"])
def api_profileinfo():    
    if not 'user_id' in session:
        return {"message": "Unauthorized"}, 401
    
    data = request.get_json()
    userid = data.get("userid")    
    
    user = User.query.filter_by(userid=userid).first()
    if not user:
        return {"message": "User not found"}, 404
    return user, 200

# DEBUG ENDPOINTS
@app.route("/api/test", methods=["GET"])
def api_test():
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
    socketio.run(app, debug=True)
