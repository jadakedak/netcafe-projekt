import socketio
import os
from random import choice

# THIS IS THE SCRIPT THAT RUNS ON THE COMPUTERS 
# THAT ARE PART OF THE NETCAFÉ

sio = socketio.Client()
id_path = os.path.join(os.environ["PROGRAMDATA"], "Netcafe", "id.txt")

def generateid(length=16):
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return ''.join(choice(chars) for _ in range(length))

def Getclientid():
    os.makedirs(os.path.dirname(id_path), exist_ok=True)
    if os.path.exists(id_path):
        with open(id_path, "r") as f:
            return f.read().strip()
    new_id = generateid()
    with open(id_path, "w") as f:
        f.write(new_id)
    return new_id

@sio.event
def connect():
    data = {
        "type": "registration",
        "pcid": Getclientid(),
        "pcname": os.getenv("COMPUTERNAME", "Unknown-PC"),
        "user": os.getlogin(),
    }
    sio.send(data)
    print("Connected to server")

@sio.event
def disconnect():
    data = {
        "type": "disconnect",
        "pcid": Getclientid(),
    }
    sio.send(data)
    print("Disconnected from server")
    
@sio.event
def message(msg):
    if msg.get("type") == "registration":
        if msg.get("success"):
            print("Computer registered successfully")
        else:
            print(f"Failed to register computer: {msg.get('message')}")
    
    print(f"Received message: {msg}")

sio.connect("http://localhost:5000")
sio.wait()