import socketio
import os
from random import choice

# THIS IS THE SCRIPT THAT RUNS ON THE COMPUTERS 
# THAT ARE PART OF THE NETCAFÉ

sio = socketio.Client()
id_path = os.path.join(os.environ["PROGRAMDATA"], "Netcafe", "id.txt")

PING_TIMEOUT_SECONDS = 300 # Every 5 minutes I.E 300 seconds

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

def ping():
    sio.send({"type": "ping", "id": Getclientid()})

@sio.event
def connect():
    data = {
        "type": "registration",
        "pcid": Getclientid(),
        "pcname": os.getenv("COMPUTERNAME", "Unknown-PC"),
        "user": os.getlogin(),
    }
    sio.send(data)
    sio.start_background_task(ping_loop)
    print("Connected to server")

def ping_loop():
    while True:
        sio.sleep(PING_TIMEOUT_SECONDS)
        ping()

@sio.event
def disconnect():
    print("Disconnected from server")

@sio.event
def message(msg):
    if msg.get("type") == "registration":
        if msg.get("success"):
            print("Computer registered successfully")
        else:
            print(f"Failed to register computer: {msg.get('message')}")
    elif msg.get("type") == "pong":
        print("received ping response!")
    elif msg.get("type") == "PINGERROR":
        print("ping failed!")
    else:
        print("unkown message")

def handle_command(command):
    if command == "OFF":
        print("computer is turning off!")
    elif command == "ON":
        print("computer is turning on!")

@sio.event
def command(command):
    if command["target"] == Getclientid():
        try:
            output = handle_command(command["message"])
            if output:
                return {"success": True, "message": "command was executed!", "output": output}
            return {"success": True, "message": "command was executed!"}
        except Exception as e:
            return {"success": False, "message": "command execution failed", "error": str(e)}
    
sio.connect("http://localhost:5000")
sio.wait()