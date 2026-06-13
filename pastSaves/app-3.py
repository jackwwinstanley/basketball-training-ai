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
            max_tokens=2048,
            messages=[
                {"role": "user", "content": f"""Create a basketball practice plan for a {skill_level} {position} who wants to improve {weaknesses} and has {time_available} minutes available. They have access to: {equipment}.

Format your response EXACTLY like this example — use these exact section headers and structure:

## Warm-Up (10 min)

### Dynamic Stretching
**Duration:** 5 minutes
**Reps/Sets:** 2 sets of 10 each
**Instructions:** Light jogging, leg swings, arm circles to loosen up.

### Ball Handling Warmup
**Duration:** 5 minutes
**Reps/Sets:** 3 sets of 30 seconds
**Instructions:** Stationary dribbling, alternating hands, eyes up.

## Skill Work (25 min)

### Mikan Drill
**Duration:** 8 minutes
**Reps/Sets:** 5 sets of 10 reps
**Instructions:** Alternate layups from each side of the basket without letting the ball hit the floor.

## Shooting (15 min)

### Spot Shooting
**Duration:** 15 minutes
**Reps/Sets:** 10 shots from 5 spots
**Instructions:** Pick 5 spots around the arc. Shoot 10 from each. Track your makes.

## Cool-Down (5 min)

### Static Stretching
**Duration:** 5 minutes
**Reps/Sets:** Hold each stretch 30 seconds
**Instructions:** Quad stretch, hamstring stretch, shoulder stretch. Focus on breathing.

Use real drill names. Be specific with instructions. Include 2-4 drills per section. Adjust number of sections to fill exactly {time_available} minutes."""}
            ]
        )
        plan = message.content[0].text
    return render_template("index.html", plan=plan)

if __name__ == "__main__":
    app.run(debug=True)
