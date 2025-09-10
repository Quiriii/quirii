import pandas as pd
import datetime
import subprocess

# Load CSV
df = pd.read_csv("mess_menu.csv")

# Get today's day (1–31)
today_day = datetime.date.today().day

# Lookup row for today's day
row = df[df["Day"] == today_day]

if not row.empty:
    breakfast = row.iloc[0]["Breakfast"]
    lunch = row.iloc[0]["Lunch"]
    snacks = row.iloc[0]["Snacks"]
    dinner = row.iloc[0]["Dinner"]

    menu_text = f"Breakfast: {breakfast}\nLunch: {lunch}\nSnacks: {snacks}\nDinner: {dinner}"
else:
    menu_text = "No menu found for today."

# Prompt
user_query = input("You: ")
prompt = prompt = f"""
You are a college mess menu assistant.
The student asked: "{user_query}"

Today's menu (Day {today_day}):
{menu_text}

Instructions:
- If the query is about today's menu, answer **only with the menu in this format**:

Breakfast: ...
Lunch: ...
Snacks: ...
Dinner: ...

- Do not output JSON, explanations, or extra text.
- If the query is unrelated to the mess menu, just reply:
"I can only help with today's mess menu right now."
"""


# Run Ollama
cmd = ["ollama", "run", "phi3:mini"]
process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, encoding="utf-8")
output, _ = process.communicate(prompt)

print("Bot:", output)
