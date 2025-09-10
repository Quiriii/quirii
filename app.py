from flask import Flask, request, jsonify, send_from_directory
import json, datetime, difflib, subprocess, os

app = Flask(__name__, static_folder="static")

# ---------- Load Data ----------
with open("mess_menu.json", "r", encoding="utf-8") as f:
    mess_menu = json.load(f)

with open("faculty_list.json", "r", encoding="utf-8") as f:
    faculty_list = json.load(f)


# ---------- Utility Functions ----------
def get_today_menu():
    today = datetime.date.today().day
    for entry in mess_menu:
        if entry.get("Date") == today:
            return (
                f"Breakfast: {entry.get('Breakfast', 'N/A')}\n"
                f"Lunch: {entry.get('Lunch', 'N/A')}\n"
                f"Snacks: {entry.get('Snacks', 'N/A')}\n"
                f"Dinner: {entry.get('Dinner', 'N/A')}"
            )
    return "No mess menu found for today."

def get_faculty_info(name_query):
    all_names = [faculty["Name"] for faculty in faculty_list.values()]
    match = difflib.get_close_matches(name_query, all_names, n=1, cutoff=0.6)
    if match:
        for _, faculty in faculty_list.items():
            if faculty["Name"] == match[0]:
                return f"{faculty['Name']} - Cabin: {faculty.get('Office_Address','N/A')}"
    return "No matching faculty found."

def call_gpt(user_input):
    try:
        process = subprocess.Popen(
            ["ollama", "run", "phi3:3.8b"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8"
        )
        prompt = f"User: {user_input}\nAssistant:"
        output, _ = process.communicate(prompt, timeout=15)
        return output.strip()
    except subprocess.TimeoutExpired:
        process.kill()
        return "The model took too long to respond."


# ---------- API Endpoint ----------
@app.route("/chat", methods=["POST"])
def chat():
    user_query = request.json.get("message", "").strip()

    if "menu" in user_query.lower():
        return jsonify({"response": get_today_menu()})

    faculty_info = get_faculty_info(user_query)
    if faculty_info != "No matching faculty found.":
        return jsonify({"response": faculty_info})

    return jsonify({"response": call_gpt(user_query)})


# ---------- Serve HTML ----------
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


if __name__ == "__main__":
    app.run(debug=True)
