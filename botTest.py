import json
import datetime
import subprocess
import difflib

# ---------- Load Data ----------
with open("mess_menu.json", "r", encoding="utf-8") as f:
    mess_menu = json.load(f)

with open("faculty_list.json", "r", encoding="utf-8") as f:
    faculty_list = json.load(f)

# ---------- Utility Functions ----------
def get_today_menu():
    today = datetime.date.today().day  # day of the month
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
    # Fuzzy match against all names
    match = difflib.get_close_matches(name_query, all_names, n=1, cutoff=0.6)
    if match:
        for _, faculty in faculty_list.items():
            if faculty["Name"] == match[0]:
                return f"{faculty['Name']} - Cabin: {faculty.get('Office_Address','N/A')} - E-Mail: {faculty.get('EMAIL')}"
    return "No matching faculty found."

def call_gpt(user_input, system_prompt=""):
    try:
        process = subprocess.Popen(
            ["ollama", "run", "phi3:3.8b"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8"
        )
        prompt = f"{system_prompt}\nUser: {user_input}\nAssistant:"
        output, _ = process.communicate(prompt, timeout=20)  # prevent infinite hang
        return output.strip()
    except subprocess.TimeoutExpired:
        process.kill()
        return "The model took too long to respond."

# ---------- Main Loop ----------
SYSTEM_PROMPT = """
You are a factual, concise college assistant.
Rules:
- For mess menu: only show Breakfast, Lunch, Snacks, Dinner.
- For faculty: only show Name and Cabin number (Office_Address).
- If info not found: reply "I don’t have that information."
- No extra descriptions, no hallucinations.
"""

print("College Assistant Bot (type 'exit' to quit)")
while True:
    user_query = input("You: ").strip()
    if user_query.lower() == "exit":
        break

    # Mess menu check
    if "menu" in user_query.lower():
        print("Bot:", get_today_menu())
        continue

    # Faculty check (try fuzzy match on ANY query before fallback)
    faculty_info = get_faculty_info(user_query)
    if faculty_info != "No matching faculty found.":
        print("Bot:", faculty_info)
        continue

    # General fallback → LLM
    response = call_gpt(user_query, SYSTEM_PROMPT)
    print("Bot:", response)
