# NoDaysOff — AI Basketball Training Platform

A full-stack web application that generates personalized basketball 
practice plans using AI, with embedded video demonstrations for every drill.

**Live at:** [nodaysoff.pro](https://nodaysoff.pro)

---

## Features

- **AI-generated practice plans** — powered by Claude API, personalized 
  by position, skill level, focus area, and available time
- **200+ drill video library** — YouTube embeds starting at exact 
  timestamps for every drill
- **Google OAuth authentication** — secure sign-in with Gmail
- **Session tracking** — logs every login with duration and activity
- **Training calendar** — visual heatmap of training days
- **Plans history** — full log of every generated plan with 
  persistent drill completion tracking
- **Mobile responsive** — works on phone, tablet, and desktop

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Database | SQLite / SQLAlchemy |
| Auth | Google OAuth 2.0 (Authlib) |
| AI | Anthropic Claude API |
| Frontend | HTML, CSS, Vanilla JavaScript |
| Server | Gunicorn + Nginx |
| Hosting | AWS EC2 (t3.micro) |
| SSL | Let's Encrypt |

---

## Architecture
---

## Running Locally

**Prerequisites:** Python 3.12+

**1. Clone the repo**
```bash
git clone https://github.com/YOURUSERNAME/basketball-training-ai.git
cd basketball-training-ai
```

**2. Install dependencies**
```bash
pip install flask flask-login flask-sqlalchemy authlib requests anthropic gunicorn
```

**3. Set environment variables**
```bash
export FLASK_SECRET_KEY="your-secret-key"
export GOOGLE_CLIENT_ID="your-google-client-id"
export GOOGLE_CLIENT_SECRET="your-google-client-secret"
export ANTHROPIC_API_KEY="your-anthropic-key"
```

**4. Run**
```bash
python3 app.py
```

Visit `http://localhost:5000`

---

## Deployment

Deployed on AWS EC2 (Ubuntu 24.04, t3.micro) with:
- Nginx as reverse proxy
- Gunicorn as WSGI server
- Let's Encrypt SSL certificate
- Systemd service for auto-restart on reboot

---

## Author

Jack Winstanley — Computer Engineering, University of Waterloo  
AWS Certified Cloud Practitioner (CLF-C02)
