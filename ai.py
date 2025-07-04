import sys
import shutil
import json
import os
import re
from Backend.Chatbot import ChatBot
from Backend.Model import FirstLayerDMM

sys.stdout.reconfigure(encoding='utf-8')

if len(sys.argv) < 3:
    print("No query or sender provided.")
    sys.exit()

query = sys.argv[1].strip()
sender = sys.argv[2].strip()

ADMIN_PASSWORD = "6969"
ADMIN_FILE = "Data/Admin.json"
GUEST_FILE = "Data/GuestNames.json"

# 🔐 Load admin list
if os.path.exists(ADMIN_FILE):
    with open(ADMIN_FILE, "r") as f:
        try:
            admins = json.load(f)
        except json.JSONDecodeError:
            admins = []
else:
    admins = []

# 👥 Load guest names
if os.path.exists(GUEST_FILE):
    with open(GUEST_FILE, "r") as f:
        try:
            names = json.load(f)
        except json.JSONDecodeError:
            names = {}
else:
    names = {}

# 💬 Logic
if query.lower() == "/forgetme":
    if sender in names:
        del names[sender]
        with open(GUEST_FILE, "w") as f:
            json.dump(names, f, indent=4)
        response = "🗑️ Your memory has been cleared. I won’t remember you next time."
    else:
        response = "ℹ️ I don’t remember you yet, so there’s nothing to forget."

elif query.lower() == "/logout":
    was_admin = sender in admins
    if was_admin:
        admins.remove(sender)
        with open(ADMIN_FILE, "w") as f:
            json.dump(admins, f, indent=4)
        if sender in names:
            del names[sender]
            with open(GUEST_FILE, "w") as f:
                json.dump(names, f, indent=4)
        response = "✅ You are now logged out. Admin access and name forgotten."
    else:
        response = "⚠️ You're not logged in as admin."

elif query.lower() == "/admin":
    response = "🔐 Please reply with the admin password."

elif query.strip() == ADMIN_PASSWORD:
    if sender not in admins:
        admins.append(sender)
        with open(ADMIN_FILE, "w") as f:
            json.dump(admins, f, indent=4)

        # Automatically set name after login
        names[sender] = "Amit Dutta"
        with open(GUEST_FILE, "w") as f:
            json.dump(names, f, indent=4)

        response = "✅ Access granted! You're now recognized as admin, Amit Dutta."
    else:
        response = "✅ You are already an admin."

elif match := re.match(r"name\s*:\s*(\w+)", query, re.IGNORECASE):
    name = match.group(1).capitalize()
    names[sender] = name
    with open(GUEST_FILE, "w") as f:
        json.dump(names, f, indent=4)
    response = f"✅ Got it! I’ll remember you as {name}."

elif query.lower() in [
        "who am i", "what is my name", "amar naam ki", "ami ke", "আমি কে",
        "আমার নাম কি"
]:
    if sender in names:
        response = f"You're {names[sender]}!"
    else:
        response = "🤔 I don’t know your name yet!\nIf you'd like me to remember, reply like this:\n`name: YourName`"

else:
    is_admin = sender in admins
    response = ChatBot(query, sender if is_admin else None).strip()

# 🖨️ Print nicely
terminal_width = shutil.get_terminal_size().columns
signature = "- Ada AI"
print(response + "\n" + " " * (terminal_width - len(signature)) + signature)
