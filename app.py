from uuid import uuid4
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_cors import CORS
import flask_socketio as fsock
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from random import randint

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
edit_mode = False

CLOUD_SERVER_URL = "http://159.65.92.59:3000"

class User(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    userid      = db.Column(db.String(50), unique=True, nullable=False)
    admin       = db.Column(db.Boolean, default=False)
    fornavn     = db.Column(db.String(50), nullable=False)
    efternavn   = db.Column(db.String(50), nullable=False)
    email       = db.Column(db.String(120), unique=True, nullable=False)
    brugernavn  = db.Column(db.String(50), unique=True, nullable=False)
    adgangskode = db.Column(db.String(200), nullable=False)
    credits     = db.Column(db.Integer, nullable=False)
    transactions = db.relationship("Transactions", foreign_keys="Transactions.user_id", primaryjoin="User.userid == Transactions.user_id")


class Menuitem(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    item_id     = db.Column(db.String(50), unique=True, nullable=False)
    navn        = db.Column(db.String(100), nullable=False)
    beskrivelse = db.Column(db.String(500), nullable=False)
    billede_sti = db.Column(db.String(200), nullable=True)  # URL til billede (kunne være på fil server)
    pris        = db.Column(db.Float, nullable=False)

class Computer(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    pcid            = db.Column(db.String(50), unique=True, nullable=False)
    pcname          = db.Column(db.String(100), nullable=False)
    user            = db.Column(db.String(50), nullable=False)
    connected       = db.Column(db.Boolean, default=True)
    connection_date = db.Column(db.DateTime, nullable=False)

class Transactions(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.String(50), index=True, nullable=False)
    transaction_id  = db.Column(db.String(50), unique=True, nullable=False)
    item            = db.Column(db.String(50), nullable=False)
    amount          = db.Column(db.Integer, nullable=False)
    total           = db.Column(db.Integer, nullable=True)
    purchased_at    = db.Column(db.DateTime, nullable=False)

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
def remove_menuitem(item_id):
    item = Menuitem.query.get(item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
        return True
    return False

def get_menuitems():
    return Menuitem.query.all()


# TRANSACTION FUNCTIONS
def generate_Tansid(length):
    id = ""
    chars = "ABCDEFGHIJKLMNOPQRSTUVXYZ1234567890"
    for i in range(length):
        id += chars[randint(0, len(chars) - 1)]
    return id

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

@app.route("/", methods=["GET"])
def landing_page():
    session.clear()
    return {"message": "session is cleared!"}

# ENDPOINTS
@app.route("/<userid>/home", methods=["GET"])
def home(userid):
    is_admin = False
    if not 'user_id' in session:
        return redirect(url_for("login"))
    
    user = User.query.filter_by(userid=userid).first()
    is_admin = user.admin if user else False
    return render_template("index.html", userid=userid, is_admin=is_admin)

@app.route("/<userid>/admin", methods=["GET"])
def admin(userid):
    user = User.query.filter_by(userid=userid).first()
    if not user or not user.admin:
        flash("Unauthorized access", "danger")
        return redirect(url_for("home", userid=userid))
    return render_template("admin.html", userid=userid)

@app.route("/<userid>/profile", methods=["GET"])
def profile(userid):
    user = User.query.filter_by(userid=userid).first()
    if not user:
        flash("User not found", "danger")
        return redirect(url_for("home", userid=userid))
    return render_template("profile.html", user=user)

@app.route("/<userid>/creditshop", methods=["GET"])
def creditshop(userid):
    if not 'user_id' in session:
        return redirect(url_for("login"))
    return render_template("/creditshop.html", userid=userid)

@app.route("/<userid>/menu", methods=["GET"])
def menu(userid):
    if not 'user_id' in session:
        return redirect(url_for("login"))
    return render_template("menu.html", userid=userid)

@app.route("/<userid>/cart", methods=["GET"])
def cart(userid):
    if not 'user_id' in session:
        return redirect(url_for("login"))
    if not session.get("cart"):
        session["cart"] = {}
    return render_template("/cart.html", userid=userid, cart=session["cart"])

@app.route("/register", methods=["GET"])
def register():
    return render_template("register.html")

@app.route("/login", methods=["GET"])
def login():
    return render_template("login.html")


# USER API ENDPOINTS
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
        credits=data["credits"]
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


# BUYING ENDPOINTS
@app.route("/api/buy/credits", methods=["POST"])
def buy_credits():
    data = request.get_json()
    try:
        amount = int(data.get("amount"))
        user = User.query.filter_by(userid=session['user_id']).first()
        user.credits += amount

        db.session.commit()
        return {"success": True, "message": f"successfully bought {amount} credits!"}, 200
    except Exception as e:
        return {"success": False, "message": str(e)}, 500
    
@app.route("/api/checkout", methods=["POST"])
def checkout():
    if not 'user_id' in session:
        return redirect(url_for("login"))
    data = request.get_json()

    price_total = data.get("price_total")
    quantity_total = data.get("quantity_total")
    item = data.get("item")
    user = User.query.filter_by(userid=session["user_id"]).first()

    if user.credits < price_total:
        return {"success": False, "message": "Insufficient credits"}

    transid = generate_Tansid(10)
    user.credits -= price_total
    session["cart"] = {}

    new_transaction = Transactions(user_id=session["user_id"], transaction_id=transid, item=item, amount=quantity_total, total=price_total, purchased_at=datetime.now())
    db.session.add(new_transaction)
    
    db.session.commit()

    return {"success": True, "message": "Checkout successful"}

    
    
@app.route("/api/users", methods=["GET"])
def api_users():
    if 'user_id' in session:
        admin_check = User.query.filter_by(userid=session['user_id']).first()
        if admin_check.admin == False:
            return {"message": "Unauthorized"}, 401
    else:
        return {"message": "Unauthorized"}, 401
    
    users = User.query.all()
    user_list = []
    for user in users:
        user_list.append({
            "id": user.id,
            "fornavn": user.fornavn,
            "is_admin": user.admin,
            "efternavn": user.efternavn,
            "email": user.email,
            "brugernavn": user.brugernavn,
            "adgangskode": user.adgangskode
        })
    return {"users": user_list}, 200

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


# TRANSACTION ENDPOINTS
@app.route("/api/transactions/insert", methods=["POST"])
def insert_transaction():
    if not 'user_id' in session:
        return redirect(url_for("login"))
    try:
        data = request.get_json()
        
        userid  = session["user_id"]
        transid = generate_Tansid(10)
        item    = data.get("item")
        amount  = data.get("amount")
        total   = data.get("total")
        
        new_transaction = Transactions(user_id=userid, transaction_id=transid, item=item, amount=amount, total=total, purchased_at=datetime.now())
        db.session.add(new_transaction)
        db.session.commit()
        
        return {"success": True, "message": "transaction has been logged to database!", "transaction_id": transid}
    except Exception as e:
        print(e)
        return {"success": False, "message": "IT FAILED"}

@app.route("/api/transactions/history", methods=["GET"])
def transaction_history():
    try:
        user = User.query.filter_by(userid=session["user_id"]).first()
        transactions = [{"transaction_id": t.transaction_id, "item": t.item, "amount": t.amount, "total": t.total, "purchased_at": t.purchased_at} for t in user.transactions]
        return {"success": True, "transactions": transactions}
    except Exception:
        return {"success": False, "message": "failed to load transactions!"}


# MENU API ENDPOINTS
@app.route("/api/menu/items", methods=["GET"])
def api_menu_items():
    if not 'user_id' in session:
        return {"message": "Unauthorized"}, 401

    items = Menuitem.query.all()
    item_list = []
    for item in items:
        item_list.append({
            "id": item.item_id,
            "navn": item.navn,
            "beskrivelse": item.beskrivelse,
            "pris": item.pris,
            "billede_sti": item.billede_sti
        })
    return {"items": item_list}, 200

@app.route("/api/menu/add_cart/<itemid>", methods=["PUT"])
def add_cart(itemid):
    if not 'user_id' in session:
        return redirect(url_for("login"))
    try:
        cart = session.get("cart", {})
        cart[itemid] = cart.get(itemid, 0) + 1
        session["cart"] = cart
        session.modified = True
        return {"success": True, "message": "item added to cart!", "quantity": cart[itemid]}, 200
    except Exception as e:
        return {"success": False, "message": str(e)}, 500

@app.route("/api/menu/items/get", methods=["POST"])
def api_get_menu_items():
    if not 'user_id' in session:
        return {"message": "Unauthorized"}, 401
    
    data = request.get_json()
    item_list = []
    
    for itemid in data["items"]:
        quantity = data["items"][itemid]
        item = Menuitem.query.filter_by(item_id=itemid).first()
        item_list.append({
            "id": itemid,
            "navn": item.navn,
            "beskrivelse": item.beskrivelse,
            "pris": item.pris,
            "billede_sti": item.billede_sti,
            "quantity": quantity
        })
    return item_list
    
@app.route("/api/menu/item/get/<item_id>", methods=["GET"])
def api_get_menu_item(item_id):
    if not 'user_id' in session:
        return {"message": "Unauthorized"}, 401

    item = Menuitem.query.filter_by(item_id=item_id).first()
    if not item:
        return {"message": "Menu item not found"}, 404
    
    return {
        "id": item.item_id,
        "navn": item.navn,
        "beskrivelse": item.beskrivelse,
        "pris": item.pris,
        "billede_sti": item.billede_sti
    }, 200

@app.route("/api/menu/get_cart", methods=["GET"])
def get_cart():
    if not 'user_id' in session:
        return redirect(url_for("login"))
    try:
        if not session.get("cart"):
            session["cart"] = {}
        return {"success": True, "cart": session["cart"]}
    except:
        return {"success": False, "cart": []}


# ADMIN ONLY
@app.route("/api/menu/items/add", methods=["POST"])
def api_add_menu_item():
    if not 'user_id' in session:
        return {"message": "Unauthorized"}, 401
    if not User.query.filter_by(userid=session['user_id']).first().admin:
        return {"message": "Unauthorized"}, 401

    data = request.get_json()
    item_id = str(uuid4())  # Generate a unique item ID
    navn = data.get("navn")
    beskrivelse = data.get("beskrivelse")
    pris = data.get("pris")
    billede_sti = data.get("billede_sti")
    
    new_item = Menuitem(navn=navn, item_id=item_id, beskrivelse=beskrivelse, pris=pris, billede_sti=billede_sti)
    db.session.add(new_item)
    db.session.commit()

    return {"success": True, "message": "Menu item added successfully", "item_id": item_id}, 201

@app.route("/api/menu/items/remove/<item_id>", methods=["DELETE"])
def api_remove_menu_item(item_id):
    if not 'user_id' in session:
        return {"message": "Unauthorized"}, 401
    if not User.query.filter_by(userid=session['user_id']).first().admin:
        return {"message": "Unauthorized"}, 401

    item = Menuitem.query.filter_by(item_id=item_id).first()
    if not item:
        return {"message": "Menu item not found"}, 404

    db.session.delete(item)
    db.session.commit()

    return {"success": True, "message": "Menu item removed successfully"}, 200

@app.route("/api/menu/items/edit/<item_id>", methods=["PUT"])
def api_edit_menu_item(item_id):
    if not 'user_id' in session:
        return {"message": "Unauthorized"}, 401
    if not User.query.filter_by(userid=session['user_id']).first().admin:
        return {"message": "Unauthorized"}, 401

    data = request.get_json()
    print(data)
    item = Menuitem.query.filter_by(item_id=item_id).first()
    if not item:
        return {"success": False, "message": "Menu item not found"}, 404

    item.navn = data["navn"]
    item.beskrivelse = data["beskrivelse"]
    item.pris = data["pris"]
    item.billede_sti = data["billede_sti"]

    db.session.commit()
    return {"success": True, "message": "Menu item updated successfully"}, 200

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