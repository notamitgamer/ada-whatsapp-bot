import sys
import shutil
import json
import os
import re
from Backend.Chatbot import ChatBot
from Backend.Model import FirstLayerDMM

# ✅ Fix encoding for emojis/unicode output
sys.stdout.reconfigure(encoding='utf-8')

if len(sys.argv) < 3:
    print("No query or sender provided.")
    sys.exit()

query = sys.argv[1]
sender = sys.argv[2]

if query.strip().lower() == "/forgetme":
    guest_file = "Data/GuestNames.json"
    if os.path.exists(guest_file):
        try:
            with open(guest_file, "r") as f:
                names = json.load(f)
        except json.JSONDecodeError:
            names = {}

        if sender in names:
            del names[sender]
            with open(guest_file, "w") as f:
                json.dump(names, f, indent=4)
            response = "🗑️ Your memory has been cleared. I won’t remember you next time."
        else:
            response = "ℹ️ I don’t remember you yet, so there’s nothing to forget."

    else:
        response = "⚠️ No memory file found. Nothing to forget."

    # ✅ Format + print response immediately
    terminal_width = shutil.get_terminal_size().columns
    signature = "- Ada AI"
    final_reply = response + "\n" + " " * (terminal_width - len(signature)) + signature
    print(final_reply)
    sys.exit()


# ✅ First handle name learning before decision model
match = re.match(r"name\s*:\s*(\w+)", query.strip(), re.IGNORECASE)
if match:
    name = match.group(1).capitalize()
    guest_file = "Data/GuestNames.json"

    # 🛠️ Ensure the file exists
    if not os.path.exists(guest_file):
        with open(guest_file, "w") as f:
            json.dump({}, f)

    # 🧠 Load existing names (safe fallback if corrupted)
    with open(guest_file, "r") as f:
        try:
            names = json.load(f)
        except json.JSONDecodeError:
            names = {}

    # 💾 Save the new name
    names[sender] = name
    with open(guest_file, "w") as f:
        json.dump(names, f, indent=4)

    response = f"✅ Got it! I’ll remember you as {name}."
else:
    # 🧠 Use decision model
    decision = FirstLayerDMM(prompt=query)

    if any(d.startswith("identity") for d in decision):
        response = "🤔 I don’t know your name yet!\nIf you'd like me to remember, reply like this:\n`name: YourName`"
    else:
        response = ChatBot(query, sender).strip()

# ✅ Format and print
terminal_width = shutil.get_terminal_size().columns
signature = "- Ada AI"
print(response)
