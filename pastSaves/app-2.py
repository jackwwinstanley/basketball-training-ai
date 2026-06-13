from flask import Flask, render_template, request
import anthropic
import os

app = Flask(__name__)
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

@app.route("/", methods=["GET", "POST"])
def index():
    plan = None
    if request.method == "POST":
        position = request.form["position"]
        weaknesses = request.form["weaknesses"]
        time_available = request.form["time"]
        skill_level = request.form.get("skill_level", "Intermediate")
        equipment = request.form.get("equipment", "Full gym")

        message = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": f"Create a basketball practice plan for a {skill_level} {position} who wants to improve {weaknesses} and has {time_available} minutes available. They have access to: {equipment}. Be specific, structured, and include drill names, rep counts, and time breakdowns."}
            ]
        )
        plan = message.content[0].text
    return render_template("index.html", plan=plan)

if __name__ == "__main__":
    app.run(debug=True)
