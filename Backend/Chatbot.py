import json  # Ensure the import is used
from json import load, dump
import requests
import datetime
from groq import Groq
import os
from dotenv import dotenv_values
import re


Username = "Amit Dutta"
Assistantname = "Ada"

client = Groq(
    api_key="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")

messages = []

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

SystemChatBot = [{"role": "system", "content": System}]

try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
except FileNotFoundError:
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)
except json.JSONDecodeError:
    print(
        "ChatLog.json is empty or corrupted. Initializing with an empty list.")
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)


def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")

    data = f"Please use this real-time information if needed:\n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
    data += f"Time: {hour} hours, {minute} minutes, {second} seconds.\n"
    return data


def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer


def load_guest_names():
    try:
        with open(r"Data\GuestNames.json", "r") as f:
            return json.load(f)
    except:
        return {}


def save_guest_names(data):
    with open(r"Data\GuestNames.json", "w") as f:
        json.dump(data, f, indent=4)


def extract_name(query):
    # Expecting format: name: Rahul
    match = re.match(r"name:\s*(\w+)", query.strip(), re.IGNORECASE)
    if match:
        return match.group(1).capitalize()
    return None


def ChatBot(Query, sender_number=None):
    try:
        with open(r"Data\ChatLog.json", "r") as f:
            messages = load(f)

        guest_names = load_guest_names()
        is_owner = sender_number == "7278779512@c.us"
        lowered = Query.strip().lower()

        # 🧠 Handle guest identity protection BEFORE AI runs
        identity_patterns = [
            # English
            "what is my name",
            "what's my name",
            "do you know my name",
            "who am i",
            "do you know who i am",
            "tell me about me",
            "what do you know about me",
            "who is chatting with you",
            "who is the user",
            "what is the user's name",

            # Roman Bengali (Benglish)
            "amar naam ki",
            "amar nam ki",
            "ami ke",
            "amar shomporke bolo",
            "amar somporke bolo",
            "tumi ki amake chino",
            "ami tomar sathe kothay bolchi",
            "ami tomar sathe kotha bolchi",
            "ke bolche",
            "ke chat korche",
            "ke message pathalo",

            # Bengali script
            "আমার নাম কি",
            "আমি কে",
            "আমাকে চিনো",
            "তুমি জানো আমি কে",
            "কে বলছে",
            "তুমি কে",
            "তুমি কি জানো আমি কে",
            "আমার সম্পর্কে বল",
            "আমাকে চিনতে পারো",
            "কে মেসেজ পাঠালো"
        ]

        for phrase in identity_patterns:
            if not is_owner and phrase in lowered:
                return "🤔 I don’t know your name yet!\nIf you'd like me to remember, reply like this:\n`name: YourName`"

        # 🧠 Learn name if user sends "name: X"
        learned_name = extract_name(Query)
        if not is_owner and learned_name:
            guest_names[sender_number] = learned_name
            save_guest_names(guest_names)
            return f"✅ Got it! I’ll remember you as {learned_name}."

        # 🎉 Greet known guests
        guest_name = guest_names.get(sender_number)
        if not is_owner and guest_name and lowered in ["hi", "hello", "hey"]:
            return f"👋 Welcome back, {guest_name}!"

        # 🤖 Run AI model
        messages.append({"role": "user", "content": Query})
        full_messages = SystemChatBot + [{
            "role": "system",
            "content": RealtimeInformation()
        }] + messages

        completion = client.chat.completions.create(model="llama3-70b-8192",
                                                    messages=full_messages,
                                                    max_tokens=1024,
                                                    temperature=0.7,
                                                    top_p=1)

        Answer = completion.choices[0].message.content.strip()

        if is_owner:
            Answer += "\n" + " " * 72 + "- Ada AI"

        messages.append({"role": "assistant", "content": Answer})
        with open(r"Data\ChatLog.json", "w") as f:
            dump(messages, f, indent=4)

        return Answer

    except Exception as e:
        print(f"ERROR:", e)
        with open(r"Data\ChatLog.json", "w") as f:
            dump([], f, indent=4)
        return "An error occurred, please try again."


if __name__ == "__main__":
    while True:
        user_input = input("Enter Your Question: ")
        response = ChatBot(user_input)
        print(response)  # Print the response to the user
