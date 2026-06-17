"""
NoDaysOff — AI Basketball Training Platform
Backend: Flask + SQLAlchemy (SQLite) + Flask-Login + Authlib (Google OAuth) + Anthropic Claude API

Required environment variables:
    FLASK_SECRET_KEY      — used to sign session cookies
    GOOGLE_CLIENT_ID       — from Google Cloud Console OAuth credentials
    GOOGLE_CLIENT_SECRET   — from Google Cloud Console OAuth credentials
    ANTHROPIC_API_KEY      — Claude API key for plan generation
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from authlib.integrations.flask_client import OAuth
import anthropic
import os
import json
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)

# ── Config ────────────────────────────────────────────────────────────────────
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-in-production")

# Database — SQLite is fine for low-traffic single-server deployment.
# Swap to RDS MySQL only if this ever needs to scale beyond one EC2 instance:
# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://user:pass@rds-endpoint/NoDaysOff"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///NoDaysOff.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Google OAuth credentials (set as env vars, never hardcoded)
app.config["GOOGLE_CLIENT_ID"] = os.environ.get("GOOGLE_CLIENT_ID")
app.config["GOOGLE_CLIENT_SECRET"] = os.environ.get("GOOGLE_CLIENT_SECRET")

# ── Extensions ────────────────────────────────────────────────────────────────
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login_page"  # redirect target for @login_required when not logged in
oauth = OAuth(app)
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Registers Google as an OAuth provider using its standard discovery document,
# which tells Authlib the correct auth/token endpoints automatically.
google = oauth.register(
    name="google",
    client_id=app.config["GOOGLE_CLIENT_ID"],
    client_secret=app.config["GOOGLE_CLIENT_SECRET"],
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

# ── Models ────────────────────────────────────────────────────────────────────
class User(UserMixin, db.Model):
    """A signed-in user, identified by their Google account."""
    __tablename__ = "users"
    id            = db.Column(db.Integer, primary_key=True)
    google_id     = db.Column(db.String(128), unique=True, nullable=False)
    email         = db.Column(db.String(256), unique=True, nullable=False)
    name          = db.Column(db.String(256))
    picture       = db.Column(db.String(512))
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    sessions      = db.relationship("UserSession", backref="user", lazy=True)
    plans         = db.relationship("Plan", backref="user", lazy=True)

class UserSession(db.Model):
    """
    One row per login. Created at login with logout_at left null,
    then filled in (along with duration_min) when the user logs out.
    This lets the dashboard show "sessions this week" and "avg session length"
    without needing a separate analytics service.
    """
    __tablename__ = "user_sessions"
    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    login_at     = db.Column(db.DateTime, default=datetime.utcnow)
    logout_at    = db.Column(db.DateTime, nullable=True)
    duration_min = db.Column(db.Float, nullable=True)

class Plan(db.Model):
    """A single AI-generated practice plan, stored in full so it can be
    re-rendered later in the Plans Log tab exactly as it first appeared."""
    __tablename__ = "plans"
    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)
    position     = db.Column(db.String(128))
    weaknesses   = db.Column(db.Text)
    time_avail   = db.Column(db.String(32))
    skill_level  = db.Column(db.String(64))
    equipment    = db.Column(db.String(128))
    plan_text    = db.Column(db.Text)  # raw markdown from Claude, parsed client-side by parsePlan()

@login_manager.user_loader
def load_user(user_id):
    """Tells Flask-Login how to reload a user object from the session cookie's user_id."""
    return db.session.get(User, int(user_id))

# ── Complete Drill Library ─────────────────────────────────────────────────────
# Maps every drill name Claude is allowed to use to its YouTube video_id and
# start timestamp (in seconds), plus category/level for organizing the prompt.
# Claude is instructed to only output names from this dict; fuzzy_match_drill()
# below corrects any names it slightly mis-renders so the video embed still works.
DRILL_LIBRARY = {
    # Ball Handling - Beginner
    "Pound Dribble": {"video_id": "CLoWxOvlHkk", "start": 90, "category": "Ball Handling", "level": "Beginner"},
    "Figure Eight Dribble": {"video_id": "CLoWxOvlHkk", "start": 123, "category": "Ball Handling", "level": "Beginner"},
    "V Dribble": {"video_id": "CLoWxOvlHkk", "start": 160, "category": "Ball Handling", "level": "Beginner"},
    "In-Out Dribble": {"video_id": "CLoWxOvlHkk", "start": 194, "category": "Ball Handling", "level": "Beginner"},
    "Between the Legs Dribble": {"video_id": "CLoWxOvlHkk", "start": 232, "category": "Ball Handling", "level": "Beginner"},
    "Behind the Back Dribble": {"video_id": "CLoWxOvlHkk", "start": 292, "category": "Ball Handling", "level": "Beginner"},
    "Walking Between the Legs": {"video_id": "CLoWxOvlHkk", "start": 347, "category": "Ball Handling", "level": "Beginner"},
    "Walking Behind the Back": {"video_id": "CLoWxOvlHkk", "start": 393, "category": "Ball Handling", "level": "Beginner"},
    "Pound Cross": {"video_id": "u8LSHc0s0Do", "start": 55, "category": "Ball Handling", "level": "Beginner"},
    "Behind the Back Stationary": {"video_id": "u8LSHc0s0Do", "start": 148, "category": "Ball Handling", "level": "Beginner"},
    "In and Out Stationary": {"video_id": "u8LSHc0s0Do", "start": 198, "category": "Ball Handling", "level": "Beginner"},
    "Side Dribble": {"video_id": "u8LSHc0s0Do", "start": 245, "category": "Ball Handling", "level": "Beginner"},
    "Around the World": {"video_id": "u8LSHc0s0Do", "start": 308, "category": "Ball Handling", "level": "Beginner"},
    "Line Trace Dribble": {"video_id": "js5tAJ9jm4o", "start": 33, "category": "Ball Handling", "level": "Beginner"},
    "Cone Loop Arounds": {"video_id": "js5tAJ9jm4o", "start": 121, "category": "Ball Handling", "level": "Beginner"},
    "Wall Touch Retreat Dribble": {"video_id": "js5tAJ9jm4o", "start": 198, "category": "Ball Handling", "level": "Beginner"},
    "Wall In and Out Dribble": {"video_id": "js5tAJ9jm4o", "start": 259, "category": "Ball Handling", "level": "Beginner"},
    # Ball Handling - Intermediate
    "Figure Eight No Dribble": {"video_id": "q-tg_pGEXfU", "start": 16, "category": "Ball Handling", "level": "Intermediate"},
    "Behind the Back Catch Drill": {"video_id": "q-tg_pGEXfU", "start": 91, "category": "Ball Handling", "level": "Intermediate"},
    "Crossover and Thigh Tap": {"video_id": "q-tg_pGEXfU", "start": 190, "category": "Ball Handling", "level": "Intermediate"},
    "High Pound Dribbles": {"video_id": "q-tg_pGEXfU", "start": 266, "category": "Ball Handling", "level": "Intermediate"},
    "Side to Side Bounce Over Object": {"video_id": "q-tg_pGEXfU", "start": 327, "category": "Ball Handling", "level": "Intermediate"},
    "Figure Eight With Footwork Steps": {"video_id": "q-tg_pGEXfU", "start": 426, "category": "Ball Handling", "level": "Intermediate"},
    "Backward Figure Eight Escape Footwork": {"video_id": "q-tg_pGEXfU", "start": 482, "category": "Ball Handling", "level": "Intermediate"},
    "High Medium Low Dribbling While Walking": {"video_id": "q-tg_pGEXfU", "start": 598, "category": "Ball Handling", "level": "Intermediate"},
    "Skip to Side Turnover Dribble": {"video_id": "q-tg_pGEXfU", "start": 632, "category": "Ball Handling", "level": "Intermediate"},
    "Crossover and Speed Stop Footwork": {"video_id": "q-tg_pGEXfU", "start": 702, "category": "Ball Handling", "level": "Intermediate"},
    "Dribble Lunges": {"video_id": "HLHhVyiOExA", "start": 67, "category": "Ball Handling", "level": "Intermediate"},
    "Crossover Into Jumper": {"video_id": "HLHhVyiOExA", "start": 840, "category": "Ball Handling", "level": "Intermediate"},
    "Between Legs Into Jumper": {"video_id": "HLHhVyiOExA", "start": 924, "category": "Ball Handling", "level": "Intermediate"},
    "Behind Back Into Jumper": {"video_id": "HLHhVyiOExA", "start": 948, "category": "Ball Handling", "level": "Intermediate"},
    # Ball Handling - Advanced
    "Pound Dribble with Weight Shift": {"video_id": "oADaM2L1YLc", "start": 16, "category": "Ball Handling", "level": "Advanced"},
    "Crossover Side to Side": {"video_id": "oADaM2L1YLc", "start": 55, "category": "Ball Handling", "level": "Advanced"},
    "Pound and Joke Cross": {"video_id": "oADaM2L1YLc", "start": 86, "category": "Ball Handling", "level": "Advanced"},
    "Splits Between the Legs": {"video_id": "oADaM2L1YLc", "start": 221, "category": "Ball Handling", "level": "Advanced"},
    "Double Crossover": {"video_id": "ktoebYTz1-k", "start": 38, "category": "Ball Handling", "level": "Advanced"},
    "Front Back Rhythm Dribble": {"video_id": "ktoebYTz1-k", "start": 150, "category": "Ball Handling", "level": "Advanced"},
    "Between and Behind Combo": {"video_id": "ktoebYTz1-k", "start": 190, "category": "Ball Handling", "level": "Advanced"},
    # Ball Handling - Elite
    "Hot Freestyle Hop Dribble": {"video_id": "yEbzA3-Q-sY", "start": 111, "category": "Ball Handling", "level": "Elite"},
    "Rotational Pull Back Dribble": {"video_id": "yEbzA3-Q-sY", "start": 197, "category": "Ball Handling", "level": "Elite"},
    "Even Stance Explosion": {"video_id": "yEbzA3-Q-sY", "start": 329, "category": "Ball Handling", "level": "Elite"},
    "Pound Pocket Right Hand": {"video_id": "mpn994jqzdA", "start": 8, "category": "Ball Handling", "level": "Elite"},
    "Double Pat to Pocket": {"video_id": "mpn994jqzdA", "start": 335, "category": "Ball Handling", "level": "Elite"},
    "Continuous Between the Legs Fast": {"video_id": "zKacrZQvprA", "start": 6, "category": "Ball Handling", "level": "Elite"},
    "Rocking Between the Legs": {"video_id": "zKacrZQvprA", "start": 335, "category": "Ball Handling", "level": "Elite"},
    "Pace Change Between Two Fast Three Slow": {"video_id": "zKacrZQvprA", "start": 484, "category": "Ball Handling", "level": "Elite"},
    # Shooting - Beginner
    "Loop Around Block Shooting": {"video_id": "0feXGPKiAYs", "start": 44, "category": "Shooting", "level": "Beginner"},
    "Baseline Shooting": {"video_id": "0feXGPKiAYs", "start": 124, "category": "Shooting", "level": "Beginner"},
    "Wall Shooting": {"video_id": "0feXGPKiAYs", "start": 213, "category": "Shooting", "level": "Beginner"},
    "Hot Lava Shooting": {"video_id": "0feXGPKiAYs", "start": 302, "category": "Shooting", "level": "Beginner"},
    "Block Form Shooting": {"video_id": "vQsycsq1ib8", "start": 34, "category": "Shooting", "level": "Beginner"},
    "One Hand Shooting to Yourself": {"video_id": "MAvdDUUTLB4", "start": 9, "category": "Shooting", "level": "Beginner"},
    "Close Range Form Shots": {"video_id": "MAvdDUUTLB4", "start": 200, "category": "Shooting", "level": "Beginner"},
    "Corner to Corner Game Like Shots": {"video_id": "MAvdDUUTLB4", "start": 384, "category": "Shooting", "level": "Beginner"},
    # Shooting - Intermediate
    "Ball Pick Ups": {"video_id": "akSJjN8UIj0", "start": 25, "category": "Shooting", "level": "Intermediate"},
    "Dribble Pull Ups": {"video_id": "akSJjN8UIj0", "start": 135, "category": "Shooting", "level": "Intermediate"},
    "3-2-1 Shooting Drill": {"video_id": "akSJjN8UIj0", "start": 279, "category": "Shooting", "level": "Intermediate"},
    "4 by 7 Shooting Drill": {"video_id": "akSJjN8UIj0", "start": 412, "category": "Shooting", "level": "Intermediate"},
    "Free Throw Conditioning": {"video_id": "akSJjN8UIj0", "start": 648, "category": "Shooting", "level": "Intermediate"},
    "Flare Shooting": {"video_id": "gX07sPg7tWo", "start": 40, "category": "Shooting", "level": "Intermediate"},
    "Trail Shooting": {"video_id": "gX07sPg7tWo", "start": 95, "category": "Shooting", "level": "Intermediate"},
    "Three Point Combo Drill": {"video_id": "gX07sPg7tWo", "start": 295, "category": "Shooting", "level": "Intermediate"},
    # Shooting - Advanced
    "Cold Three Point Shooting": {"video_id": "jR0iJmStMPs", "start": 79, "category": "Shooting", "level": "Advanced"},
    "Corner to Wing Three Point Shooting": {"video_id": "jR0iJmStMPs", "start": 279, "category": "Shooting", "level": "Advanced"},
    "One Dribble Uphill Hop Shot": {"video_id": "pq4DdAqX3yg", "start": 9, "category": "Shooting", "level": "Advanced"},
    "Floater Mid Range Catch and Shoot Series": {"video_id": "pq4DdAqX3yg", "start": 156, "category": "Shooting", "level": "Advanced"},
    "Five Minute Around the World Shooting": {"video_id": "pq4DdAqX3yg", "start": 328, "category": "Shooting", "level": "Advanced"},
    # Shooting - Elite
    "One Dribble Variable Form Shooting": {"video_id": "GYMWi86DHhE", "start": 94, "category": "Shooting", "level": "Elite"},
    "High Speed Chase and Shoot": {"video_id": "GYMWi86DHhE", "start": 304, "category": "Shooting", "level": "Elite"},
    "Rotational Balance Hop Shooting": {"video_id": "GYMWi86DHhE", "start": 468, "category": "Shooting", "level": "Elite"},
    "Energy Transfer Pull Down Shooting": {"video_id": "GYMWi86DHhE", "start": 801, "category": "Shooting", "level": "Elite"},
    "Dribble into Drop Step Shooting": {"video_id": "8uhumn1FVYY", "start": 0, "category": "Shooting", "level": "Elite"},
    "Drive and Drop Step Turn": {"video_id": "8uhumn1FVYY", "start": 872, "category": "Shooting", "level": "Elite"},
    # Defense - Beginner
    "Lateral Line Jumps Warmup": {"video_id": "xoMov-_xDB4", "start": 92, "category": "Defense", "level": "Beginner"},
    "Four Cone Defensive Change of Direction": {"video_id": "xoMov-_xDB4", "start": 202, "category": "Defense", "level": "Beginner"},
    "Shuttle Slide and Sprint Drill": {"video_id": "xoMov-_xDB4", "start": 242, "category": "Defense", "level": "Beginner"},
    "Hip Flip Into Sprint": {"video_id": "xoMov-_xDB4", "start": 269, "category": "Defense", "level": "Beginner"},
    "Kobe Bryant Cutoff Drill": {"video_id": "xoMov-_xDB4", "start": 293, "category": "Defense", "level": "Beginner"},
    # Defense - Intermediate
    "Defensive Slides No Hip Turn Drill": {"video_id": "yxXEC_5xxYE", "start": 0, "category": "Defense", "level": "Intermediate"},
    "Four Cone Hip Cutoff Partner Drill": {"video_id": "yxXEC_5xxYE", "start": 154, "category": "Defense", "level": "Intermediate"},
    "Ice Skaters": {"video_id": "m01zzaw80Jo", "start": 72, "category": "Defense", "level": "Intermediate"},
    "Lateral Lunge 45 Degree Push": {"video_id": "m01zzaw80Jo", "start": 187, "category": "Defense", "level": "Intermediate"},
    "Diamond Closeout Cushion Slide Finisher": {"video_id": "m01zzaw80Jo", "start": 612, "category": "Defense", "level": "Intermediate"},
    # Defense - Advanced
    "Closeout Touch and Defend Drill": {"video_id": "mTkNmMqfTWs", "start": 78, "category": "Defense", "level": "Advanced"},
    "Shell Drill Baseline Drive Defense": {"video_id": "mTkNmMqfTWs", "start": 544, "category": "Defense", "level": "Advanced"},
    "No Paint Drill": {"video_id": "mTkNmMqfTWs", "start": 1083, "category": "Defense", "level": "Advanced"},
    # Defense - Elite
    "One on One Defensive Slides No Hip Opening": {"video_id": "o1Eid7669zY", "start": 0, "category": "Defense", "level": "Elite"},
    "Pinky Drag Low Stance Drill": {"video_id": "o1Eid7669zY", "start": 310, "category": "Defense", "level": "Elite"},
    "Steal and Deflection Timing Practice": {"video_id": "o1Eid7669zY", "start": 495, "category": "Defense", "level": "Elite"},
    # Post Moves
    "Face Up Rip Through": {"video_id": "1BkPSQL1ZzM", "start": 14, "category": "Post Moves", "level": "Beginner"},
    "Low Post Position Stability Drill": {"video_id": "FkoOzqGmJ3c", "start": 27, "category": "Post Moves", "level": "Beginner"},
    "Bump and Jump Hook": {"video_id": "JANMMKsws5E", "start": 117, "category": "Post Moves", "level": "Intermediate"},
    "Up and Under": {"video_id": "JANMMKsws5E", "start": 124, "category": "Post Moves", "level": "Intermediate"},
    "Dribble Drop Step Baseline": {"video_id": "JANMMKsws5E", "start": 153, "category": "Post Moves", "level": "Intermediate"},
    "Mid Post Rip Spin": {"video_id": "aRm82j__ogo", "start": 26, "category": "Post Moves", "level": "Intermediate"},
    "Turnaround Jump Shot": {"video_id": "rfRENRC5lIk", "start": 129, "category": "Post Moves", "level": "Advanced"},
    "Shot Fake One Dribble Middle Turnaround": {"video_id": "rfRENRC5lIk", "start": 233, "category": "Post Moves", "level": "Advanced"},
    # Finishing
    "Modified Mikan Inside Hand Drill": {"video_id": "Ajzf6XgUYO8", "start": 39, "category": "Finishing", "level": "Intermediate"},
    "Two Foot Change of Direction Baseline Finish": {"video_id": "Ajzf6XgUYO8", "start": 93, "category": "Finishing", "level": "Intermediate"},
    "Layups From Anywhere": {"video_id": "Ajzf6XgUYO8", "start": 270, "category": "Finishing", "level": "Intermediate"},
    "Same Foot Same Hand Finish": {"video_id": "n67j58oHcdA", "start": 17, "category": "Finishing", "level": "Intermediate"},
    "Unpredictability Quicksand Finish": {"video_id": "D3pimUFPaIU", "start": 48, "category": "Finishing", "level": "Advanced"},
    "Two Foot Contact Finish": {"video_id": "D3pimUFPaIU", "start": 119, "category": "Finishing", "level": "Advanced"},
    "Cuff Euro Step Finish": {"video_id": "zh2JLinO-ws", "start": 56, "category": "Finishing", "level": "Elite"},
    "No Jump High Speed Touch Finish": {"video_id": "zh2JLinO-ws", "start": 268, "category": "Finishing", "level": "Elite"},
    "Eyes Closed Late Open Finishing": {"video_id": "zh2JLinO-ws", "start": 332, "category": "Finishing", "level": "Elite"},
}

def get_drill_names_for_prompt():
    """Group drill names by 'Category - Level' so the Claude prompt can be
    organized into readable sections rather than one flat list of 200+ names."""
    organized = {}
    for name, info in DRILL_LIBRARY.items():
        key = f"{info['category']} - {info['level']}"
        organized.setdefault(key, []).append(name)
    result = ""
    for category, names in organized.items():
        result += f"\n{category}:\n"
        for n in names:
            result += f"  - {n}\n"
    return result

def fuzzy_match_drill(name):
    """
    Claude occasionally renames or slightly rewords a drill (e.g. drops a word,
    pluralizes, or merges two names) even when told to copy them exactly.
    Since the frontend looks up videos by exact name match against DRILL_LIBRARY,
    any drift would silently break the video embed for that drill.

    This scores every library name by word overlap with what Claude returned and
    substitutes the closest match if the overlap is confident enough (>=0.5).
    If nothing scores high enough, the original text is kept as-is rather than
    risk swapping in a wrong drill.
    """
    if name in DRILL_LIBRARY:
        return name  # exact match — nothing to fix
    # Normalize for comparison
    name_lower = name.lower().strip()
    best_match = None
    best_score = 0
    for lib_name in DRILL_LIBRARY.keys():
        lib_lower = lib_name.lower()
        # Word overlap score
        name_words = set(name_lower.split())
        lib_words  = set(lib_lower.split())
        if not name_words:
            continue
        overlap = len(name_words & lib_words)
        score = overlap / max(len(name_words), len(lib_words))
        # Bonus if one name is a substring of the other (catches truncations/extensions)
        if name_lower in lib_lower or lib_lower in name_lower:
            score += 0.3
        if score > best_score:
            best_score = score
            best_match = lib_name
    # Only substitute if reasonably confident — avoids swapping in an unrelated drill
    if best_score >= 0.5 and best_match:
        return best_match
    return name  # no good match found; leave as-is (frontend will show "search YouTube" link)

def fix_drill_names_in_plan(plan_text):
    """Post-process Claude's full plan text, correcting every '### Drill Name'
    header in place using fuzzy_match_drill(). Runs once per generated plan
    right before saving to the database, so corrections persist in the log too."""
    import re
    def replace_drill(match):
        original = match.group(1).strip()
        fixed = fuzzy_match_drill(original)
        return f"### {fixed}"
    return re.sub(r'^### (.+)$', replace_drill, plan_text, flags=re.MULTILINE)

# ── Auth routes ───────────────────────────────────────────────────────────────
@app.route("/login")
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    return render_template("login.html")

@app.route("/auth/google")
def auth_google():
    """Kicks off the OAuth flow — sends the user to Google's login page."""
    redirect_uri = url_for("auth_callback", _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route("/auth/callback")
def auth_callback():
    """
    Google redirects here after the user approves login, with a code that
    Authlib exchanges for an access token + user profile (userinfo).
    First-time visitors get a new User row; returning users are matched by
    their stable Google account id (google_id), not email, since email can change.
    """
    token = google.authorize_access_token()
    user_info = token.get("userinfo")

    user = User.query.filter_by(google_id=user_info["sub"]).first()
    if not user:
        user = User(
            google_id=user_info["sub"],
            email=user_info["email"],
            name=user_info.get("name", ""),
            picture=user_info.get("picture", ""),
        )
        db.session.add(user)
        db.session.commit()

    # Start a new UserSession row now; it stays open (logout_at = None) until
    # the user actually logs out, at which point duration is calculated.
    new_session = UserSession(user_id=user.id)
    db.session.add(new_session)
    db.session.commit()
    session["session_id"] = new_session.id  # remembered in the cookie so /logout can find it

    login_user(user)
    return redirect(url_for("index"))

@app.route("/logout")
@login_required
def logout():
    # Close out the session record opened in auth_callback and compute how
    # long the user was actually logged in — this is what powers the
    # "avg session length" stat on the dashboard.
    sess_id = session.get("session_id")
    if sess_id:
        user_sess = db.session.get(UserSession, sess_id)
        if user_sess:
            user_sess.logout_at = datetime.utcnow()
            delta = user_sess.logout_at - user_sess.login_at
            user_sess.duration_min = round(delta.total_seconds() / 60, 1)
            db.session.commit()
    logout_user()
    return redirect(url_for("login_page"))

# ── Drill library endpoint ────────────────────────────────────────────────────
# Separate from /api/stats so the frontend can load DRILL_LIBRARY immediately
# on page load without waiting on the (slightly heavier) stats query first —
# this fixed a race condition where a freshly generated plan rendered before
# the video lookup data had arrived, showing "no video" for every drill.
@app.route("/api/drills")
def api_drills():
    return jsonify(DRILL_LIBRARY)

# ── API routes for dashboard stats ───────────────────────────────────────────
@app.route("/api/stats")
@login_required
def api_stats():
    """
    Single endpoint that powers the entire Dashboard tab, Plans Log tab, and
    Calendar tab — all three are derived from the same UserSession/Plan rows
    rather than separate queries, since the data overlaps heavily.
    """
    user_id = current_user.id
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)

    all_sessions = UserSession.query.filter_by(user_id=user_id).all()
    week_sessions = [s for s in all_sessions if s.login_at >= week_ago]
    # avg_session_min only counts sessions that have actually been closed out
    # (duration_min set on logout) — an in-progress session shouldn't skew the average
    completed = [s for s in all_sessions if s.duration_min is not None]
    avg_min = round(sum(s.duration_min for s in completed) / len(completed), 1) if completed else 0

    all_plans = Plan.query.filter_by(user_id=user_id).order_by(Plan.created_at.desc()).all()

    # Calendar tab needs unique login dates (not full timestamps) so multiple
    # logins on the same day still only light up one square
    login_dates = list(set(s.login_at.strftime("%Y-%m-%d") for s in all_sessions))

    plans_data = [{
        "id": p.id,
        "date": p.created_at.strftime("%b %d, %Y · %I:%M %p"),
        "position": p.position,
        "weaknesses": p.weaknesses,
        "time": p.time_avail,
        "skill_level": p.skill_level,
        "plan_text": p.plan_text,  # full markdown — re-parsed client-side in the Plans Log tab
    } for p in all_plans]

    return jsonify({
        "sessions_this_week": len(week_sessions),
        "total_sessions": len(all_sessions),
        "avg_session_min": avg_min,
        "total_plans": len(all_plans),
        "login_dates": login_dates,
        "plans": plans_data,
        "drill_library": DRILL_LIBRARY,
    })

# ── Main app route ────────────────────────────────────────────────────────────
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    plan = None
    plan_id = None
    plan_meta = None

    if request.method == "POST":
        position     = request.form["position"]
        weaknesses   = request.form["weaknesses"]
        time_avail   = request.form["time"]
        skill_level  = request.form.get("skill_level", "Intermediate")
        equipment    = request.form.get("equipment", "Full gym")

        drill_list = get_drill_names_for_prompt()  # currently unused below but kept for an
                                                     # earlier category-grouped prompt variant

        # Claude is given the full flat list of valid drill names and told to copy
        # them exactly. This (plus fix_drill_names_in_plan() afterward) is what
        # keeps every drill in a generated plan mapped to a real YouTube timestamp
        # instead of Claude inventing plausible-sounding drill names.
        valid_drills = list(DRILL_LIBRARY.keys())
        valid_drills_str = "\n".join("- " + d for d in valid_drills)

        message = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=2048,
            messages=[{"role": "user", "content": f"""
Create a basketball practice plan for a {skill_level} {position} who wants to improve {weaknesses} 
and has {time_avail} minutes available. They have access to: {equipment}.

<important>
CRITICAL RULE: You MUST use ONLY the drill names listed below, copied EXACTLY character for character. 
Do not rename, shorten, combine, or invent any drills. If a drill name does not appear in this list, 
do not use it.
</important>

<VALID_DRILL_NAMES>
(copy exactly):
{valid_drills_str}
</VALID_DRILL_NAMES>

Choose drills appropriate for {skill_level} skill level that target {weaknesses}.

Format your response EXACTLY like this — do not deviate from this structure:

<format>
## Warm-Up (10 min)

### Pound Dribble
**Duration:** 5 minutes
**Reps/Sets:** 3 sets of 30 seconds
**Instructions:** Get in a wide stance, pound the ball hard at ankle, hip, and shoulder height. Keep eyes up.

## Skill Work (20 min)

### Figure Eight Dribble
**Duration:** 8 minutes
**Reps/Sets:** 4 sets of 45 seconds
**Instructions:** Keep the ball low through the legs, alternate directions. Focus on fingertip control.

## Cool-Down (5 min)

### Side Lunges
**Duration:** 5 minutes
**Reps/Sets:** 2 sets of 10 each side
**Instructions:** Deep lunge position, feel the stretch in hamstrings and groin.
</format>

Rules:
<rules>
- Only use drill names from the VALID DRILL NAMES list above, spelled exactly as shown
- Include 2-4 drills per section
- Fill exactly {time_avail} minutes total across all sections
- Do not add any drills not in the list
</rules>
"""}]
        )
        plan = message.content[0].text

        # ── Debug logging (kept on purpose) ──────────────────────────────────
        # Logs every drill name Claude returned, before and after correction,
        # with whether each one matched the library. Useful for sanity-checking
        # in production via `journalctl -u nodaysoff -f` if videos ever stop
        # showing up — shows immediately whether Claude or the matcher is at fault.
        import re
        drill_headers = re.findall(r'^### (.+)$', plan, flags=re.MULTILINE)
        for dh in drill_headers:
            in_lib = dh.strip() in DRILL_LIBRARY
            app.logger.warning(f"DRILL: '{dh.strip()}' | IN_LIBRARY: {in_lib}")

        plan = fix_drill_names_in_plan(plan)

        drill_headers_fixed = re.findall(r'^### (.+)$', plan, flags=re.MULTILINE)
        for dh in drill_headers_fixed:
            in_lib = dh.strip() in DRILL_LIBRARY
            app.logger.warning(f"FIXED: '{dh.strip()}' | IN_LIBRARY: {in_lib}")

        # Save the corrected plan (not the raw Claude output) so the Plans Log
        # always replays exactly what the user saw, videos included.
        new_plan = Plan(
            user_id=current_user.id,
            position=position,
            weaknesses=weaknesses,
            time_avail=time_avail,
            skill_level=skill_level,
            equipment=equipment,
            plan_text=plan,
        )
        db.session.add(new_plan)
        db.session.commit()
        plan_id = new_plan.id
        plan_meta = {
            "position": position,
            "skill_level": skill_level,
            "date": new_plan.created_at.strftime("%b %d, %Y · %I:%M %p"),
        }

    # On GET this just renders the dashboard shell; on POST it also passes the
    # freshly generated plan so index.html can render it immediately without
    # waiting for a second round trip.
    return render_template(
        "index.html",
        plan=plan,
        plan_id=plan_id,
        plan_meta=plan_meta,
        user=current_user,
    )

# ── Init DB ───────────────────────────────────────────────────────────────────
# Creates NoDaysOff.db and all tables on first run if they don't already exist;
# safe to leave in on every startup since create_all() no-ops on existing tables.
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
