from flask import Flask, render_template, request
import anthropic
import os
import json

app = Flask(__name__)
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# ── Complete Drill Library ──────────────────────────────────────────────────
DRILL_LIBRARY = {
    # ── BALL HANDLING ──────────────────────────────────────────────────────
    # Beginner
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
    # Intermediate
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
    "Right and Left Hand Pounds with In and Out": {"video_id": "UqJtZ1EYbBI", "start": 15, "category": "Ball Handling", "level": "Intermediate"},
    "Continuous Cross with Pound": {"video_id": "UqJtZ1EYbBI", "start": 41, "category": "Ball Handling", "level": "Intermediate"},
    "Between the Legs and Behind the Back Stationary": {"video_id": "UqJtZ1EYbBI", "start": 51, "category": "Ball Handling", "level": "Intermediate"},
    "Three Move Combination with Pound": {"video_id": "UqJtZ1EYbBI", "start": 76, "category": "Ball Handling", "level": "Intermediate"},
    "Continuous Crosses on the Move": {"video_id": "UqJtZ1EYbBI", "start": 83, "category": "Ball Handling", "level": "Intermediate"},
    "Between Cross on the Move": {"video_id": "UqJtZ1EYbBI", "start": 98, "category": "Ball Handling", "level": "Intermediate"},
    "In and Out Between on the Move": {"video_id": "UqJtZ1EYbBI", "start": 111, "category": "Ball Handling", "level": "Intermediate"},
    "Behind the Back on the Move": {"video_id": "UqJtZ1EYbBI", "start": 121, "category": "Ball Handling", "level": "Intermediate"},
    "Cone Cross Drill": {"video_id": "UqJtZ1EYbBI", "start": 125, "category": "Ball Handling", "level": "Intermediate"},
    "Cone Between the Legs Drill": {"video_id": "UqJtZ1EYbBI", "start": 139, "category": "Ball Handling", "level": "Intermediate"},
    "Cone Behind the Back Drill": {"video_id": "UqJtZ1EYbBI", "start": 150, "category": "Ball Handling", "level": "Intermediate"},
    "Three Move Cone Combination": {"video_id": "UqJtZ1EYbBI", "start": 158, "category": "Ball Handling", "level": "Intermediate"},
    "Game Simulation Cone Drill": {"video_id": "UqJtZ1EYbBI", "start": 174, "category": "Ball Handling", "level": "Intermediate"},
    "Transition Between the Legs": {"video_id": "UqJtZ1EYbBI", "start": 216, "category": "Ball Handling", "level": "Intermediate"},
    "Cross Jab Transition": {"video_id": "UqJtZ1EYbBI", "start": 234, "category": "Ball Handling", "level": "Intermediate"},
    "Dribble Lunges": {"video_id": "HLHhVyiOExA", "start": 67, "category": "Ball Handling", "level": "Intermediate"},
    "Lateral Dribbling": {"video_id": "HLHhVyiOExA", "start": 96, "category": "Ball Handling", "level": "Intermediate"},
    "Box Dribbling": {"video_id": "HLHhVyiOExA", "start": 116, "category": "Ball Handling", "level": "Intermediate"},
    "Crossover Into Jumper": {"video_id": "HLHhVyiOExA", "start": 840, "category": "Ball Handling", "level": "Intermediate"},
    "Between Legs Into Jumper": {"video_id": "HLHhVyiOExA", "start": 924, "category": "Ball Handling", "level": "Intermediate"},
    "Behind Back Into Jumper": {"video_id": "HLHhVyiOExA", "start": 948, "category": "Ball Handling", "level": "Intermediate"},
    "In and Out Into Jumper": {"video_id": "HLHhVyiOExA", "start": 1421, "category": "Ball Handling", "level": "Intermediate"},
    "In and Out Crossover Into Jumper": {"video_id": "HLHhVyiOExA", "start": 1525, "category": "Ball Handling", "level": "Intermediate"},
    "In and Out Crossover Through Legs": {"video_id": "HLHhVyiOExA", "start": 1569, "category": "Ball Handling", "level": "Intermediate"},
    # Advanced
    "Pound Dribble with Weight Shift": {"video_id": "oADaM2L1YLc", "start": 16, "category": "Ball Handling", "level": "Advanced"},
    "Crossover Side to Side": {"video_id": "oADaM2L1YLc", "start": 55, "category": "Ball Handling", "level": "Advanced"},
    "Pound and Joke Cross": {"video_id": "oADaM2L1YLc", "start": 86, "category": "Ball Handling", "level": "Advanced"},
    "Joke Cross No Pounds": {"video_id": "oADaM2L1YLc", "start": 127, "category": "Ball Handling", "level": "Advanced"},
    "Pound Between and Behind": {"video_id": "oADaM2L1YLc", "start": 160, "category": "Ball Handling", "level": "Advanced"},
    "Splits Between the Legs": {"video_id": "oADaM2L1YLc", "start": 221, "category": "Ball Handling", "level": "Advanced"},
    "Pound Crossovers Moving": {"video_id": "oADaM2L1YLc", "start": 286, "category": "Ball Handling", "level": "Advanced"},
    "Between the Legs Moving": {"video_id": "oADaM2L1YLc", "start": 336, "category": "Ball Handling", "level": "Advanced"},
    "Crossover and Between Blend": {"video_id": "oADaM2L1YLc", "start": 387, "category": "Ball Handling", "level": "Advanced"},
    "Double Crossover": {"video_id": "ktoebYTz1-k", "start": 38, "category": "Ball Handling", "level": "Advanced"},
    "Double Cross Between and Cross Combo": {"video_id": "ktoebYTz1-k", "start": 92, "category": "Ball Handling", "level": "Advanced"},
    "Front Back Rhythm Dribble": {"video_id": "ktoebYTz1-k", "start": 150, "category": "Ball Handling", "level": "Advanced"},
    "Between and Behind Combo": {"video_id": "ktoebYTz1-k", "start": 190, "category": "Ball Handling", "level": "Advanced"},
    # Elite
    "Hot Freestyle Hop Dribble": {"video_id": "yEbzA3-Q-sY", "start": 111, "category": "Ball Handling", "level": "Elite"},
    "Forward Back Footwork Dribble": {"video_id": "yEbzA3-Q-sY", "start": 151, "category": "Ball Handling", "level": "Elite"},
    "Rotational Pull Back Dribble": {"video_id": "yEbzA3-Q-sY", "start": 197, "category": "Ball Handling", "level": "Elite"},
    "Low High Dribble": {"video_id": "yEbzA3-Q-sY", "start": 258, "category": "Ball Handling", "level": "Elite"},
    "Single Hand Freestyle": {"video_id": "yEbzA3-Q-sY", "start": 295, "category": "Ball Handling", "level": "Elite"},
    "Even Stance Explosion": {"video_id": "yEbzA3-Q-sY", "start": 329, "category": "Ball Handling", "level": "Elite"},
    "Cross Step Between the Legs Elite": {"video_id": "yEbzA3-Q-sY", "start": 467, "category": "Ball Handling", "level": "Elite"},
    "Short Lunge Explosion": {"video_id": "yEbzA3-Q-sY", "start": 603, "category": "Ball Handling", "level": "Elite"},
    "Feet Behind Retreat Explosion": {"video_id": "yEbzA3-Q-sY", "start": 687, "category": "Ball Handling", "level": "Elite"},
    "Double In Stride Move": {"video_id": "yEbzA3-Q-sY", "start": 863, "category": "Ball Handling", "level": "Elite"},
    "Off Balance Recovery Dribble": {"video_id": "yEbzA3-Q-sY", "start": 904, "category": "Ball Handling", "level": "Elite"},
    "Pound Pocket Right Hand": {"video_id": "mpn994jqzdA", "start": 8, "category": "Ball Handling", "level": "Elite"},
    "Pound Pocket Left Hand": {"video_id": "mpn994jqzdA", "start": 36, "category": "Ball Handling", "level": "Elite"},
    "Pound Pocket Cross Between": {"video_id": "mpn994jqzdA", "start": 127, "category": "Ball Handling", "level": "Elite"},
    "Pound Pocket Behind": {"video_id": "mpn994jqzdA", "start": 156, "category": "Ball Handling", "level": "Elite"},
    "Quick Between the Legs Speed Drill": {"video_id": "mpn994jqzdA", "start": 214, "category": "Ball Handling", "level": "Elite"},
    "Double Pat to Pocket": {"video_id": "mpn994jqzdA", "start": 335, "category": "Ball Handling", "level": "Elite"},
    "Double Pat Freestyle": {"video_id": "mpn994jqzdA", "start": 367, "category": "Ball Handling", "level": "Elite"},
    "Ball Manipulation Freestyle": {"video_id": "mpn994jqzdA", "start": 429, "category": "Ball Handling", "level": "Elite"},
    "Behind Right Foot Between Combo": {"video_id": "mpn994jqzdA", "start": 456, "category": "Ball Handling", "level": "Elite"},
    "Full Combination Drill": {"video_id": "mpn994jqzdA", "start": 508, "category": "Ball Handling", "level": "Elite"},
    "Continuous Between the Legs Fast": {"video_id": "zKacrZQvprA", "start": 6, "category": "Ball Handling", "level": "Elite"},
    "Continuous Between the Legs Slow": {"video_id": "zKacrZQvprA", "start": 36, "category": "Ball Handling", "level": "Elite"},
    "Continuous Behind the Back": {"video_id": "zKacrZQvprA", "start": 93, "category": "Ball Handling", "level": "Elite"},
    "Behind the Back Rhythm Change": {"video_id": "zKacrZQvprA", "start": 125, "category": "Ball Handling", "level": "Elite"},
    "Pound Between Tight Spaces": {"video_id": "zKacrZQvprA", "start": 186, "category": "Ball Handling", "level": "Elite"},
    "Pound Crossover Pat": {"video_id": "zKacrZQvprA", "start": 216, "category": "Ball Handling", "level": "Elite"},
    "Pound Behind Speed": {"video_id": "zKacrZQvprA", "start": 246, "category": "Ball Handling", "level": "Elite"},
    "Negative Space Behind Dribble": {"video_id": "zKacrZQvprA", "start": 273, "category": "Ball Handling", "level": "Elite"},
    "Rocking Between the Legs": {"video_id": "zKacrZQvprA", "start": 335, "category": "Ball Handling", "level": "Elite"},
    "Rocking Behind the Back": {"video_id": "zKacrZQvprA", "start": 392, "category": "Ball Handling", "level": "Elite"},
    "Rock Crossover with Feet": {"video_id": "zKacrZQvprA", "start": 422, "category": "Ball Handling", "level": "Elite"},
    "Pace Change Between Two Fast Three Slow": {"video_id": "zKacrZQvprA", "start": 484, "category": "Ball Handling", "level": "Elite"},
    "Full Freestyle Combination": {"video_id": "zKacrZQvprA", "start": 547, "category": "Ball Handling", "level": "Elite"},

    # ── SHOOTING ───────────────────────────────────────────────────────────
    # Beginner
    "Loop Around Block Shooting": {"video_id": "0feXGPKiAYs", "start": 44, "category": "Shooting", "level": "Beginner"},
    "Baseline Shooting": {"video_id": "0feXGPKiAYs", "start": 124, "category": "Shooting", "level": "Beginner"},
    "Wall Shooting": {"video_id": "0feXGPKiAYs", "start": 213, "category": "Shooting", "level": "Beginner"},
    "Hot Lava Shooting": {"video_id": "0feXGPKiAYs", "start": 302, "category": "Shooting", "level": "Beginner"},
    "Block Form Shooting": {"video_id": "vQsycsq1ib8", "start": 34, "category": "Shooting", "level": "Beginner"},
    "Glass Form Shooting": {"video_id": "vQsycsq1ib8", "start": 88, "category": "Shooting", "level": "Beginner"},
    "Mid Range Form Shooting": {"video_id": "vQsycsq1ib8", "start": 114, "category": "Shooting", "level": "Beginner"},
    "Opposite Block Glass Shooting": {"video_id": "vQsycsq1ib8", "start": 134, "category": "Shooting", "level": "Beginner"},
    "Quick Feet Form Shooting": {"video_id": "vQsycsq1ib8", "start": 177, "category": "Shooting", "level": "Beginner"},
    "One Dribble Form Shooting": {"video_id": "vQsycsq1ib8", "start": 220, "category": "Shooting", "level": "Beginner"},
    "Long Shot vs Short Shot Technique": {"video_id": "iTwkhWAa_P4", "start": 0, "category": "Shooting", "level": "Beginner"},
    "Hold at Point of Leverage Drill": {"video_id": "iTwkhWAa_P4", "start": 190, "category": "Shooting", "level": "Beginner"},
    "Elbow to the Rim Extension Drill": {"video_id": "iTwkhWAa_P4", "start": 235, "category": "Shooting", "level": "Beginner"},
    "One Hand Shooting to Yourself": {"video_id": "MAvdDUUTLB4", "start": 9, "category": "Shooting", "level": "Beginner"},
    "Guide Hand Line Shooting": {"video_id": "MAvdDUUTLB4", "start": 88, "category": "Shooting", "level": "Beginner"},
    "Close Range Form Shots": {"video_id": "MAvdDUUTLB4", "start": 200, "category": "Shooting", "level": "Beginner"},
    "Mid Range Shooting with Footwork": {"video_id": "MAvdDUUTLB4", "start": 246, "category": "Shooting", "level": "Beginner"},
    "Catch and Shoot from the Wings": {"video_id": "MAvdDUUTLB4", "start": 324, "category": "Shooting", "level": "Beginner"},
    "Corner to Corner Game Like Shots": {"video_id": "MAvdDUUTLB4", "start": 384, "category": "Shooting", "level": "Beginner"},
    # Intermediate
    "Ball Pick Ups": {"video_id": "akSJjN8UIj0", "start": 25, "category": "Shooting", "level": "Intermediate"},
    "Dribble Pull Ups": {"video_id": "akSJjN8UIj0", "start": 135, "category": "Shooting", "level": "Intermediate"},
    "3-2-1 Shooting Drill": {"video_id": "akSJjN8UIj0", "start": 279, "category": "Shooting", "level": "Intermediate"},
    "4 by 7 Shooting Drill": {"video_id": "akSJjN8UIj0", "start": 412, "category": "Shooting", "level": "Intermediate"},
    "Shooting off the Pivot": {"video_id": "akSJjN8UIj0", "start": 530, "category": "Shooting", "level": "Intermediate"},
    "Free Throw Conditioning": {"video_id": "akSJjN8UIj0", "start": 648, "category": "Shooting", "level": "Intermediate"},
    "Flare Shooting": {"video_id": "gX07sPg7tWo", "start": 40, "category": "Shooting", "level": "Intermediate"},
    "Trail Shooting": {"video_id": "gX07sPg7tWo", "start": 95, "category": "Shooting", "level": "Intermediate"},
    "One Dribble Middle Attack Jumper": {"video_id": "gX07sPg7tWo", "start": 152, "category": "Shooting", "level": "Intermediate"},
    "One Dribble Pullup 60 Second Drill": {"video_id": "gX07sPg7tWo", "start": 210, "category": "Shooting", "level": "Intermediate"},
    "Three Point Combo Drill": {"video_id": "gX07sPg7tWo", "start": 295, "category": "Shooting", "level": "Intermediate"},
    "Find Your Range Shooting": {"video_id": "HLHhVyiOExA", "start": 139, "category": "Shooting", "level": "Intermediate"},
    "Lane Slide Jumper": {"video_id": "HLHhVyiOExA", "start": 308, "category": "Shooting", "level": "Intermediate"},
    "One Two Footwork Alternating": {"video_id": "HLHhVyiOExA", "start": 595, "category": "Shooting", "level": "Intermediate"},
    "One Two Footwork Lateral": {"video_id": "HLHhVyiOExA", "start": 658, "category": "Shooting", "level": "Intermediate"},
    "Hop Footwork Lateral": {"video_id": "HLHhVyiOExA", "start": 755, "category": "Shooting", "level": "Intermediate"},
    "Coming Off Curl Screen Simulation": {"video_id": "HLHhVyiOExA", "start": 758, "category": "Shooting", "level": "Intermediate"},
    "Spin Out Shooting": {"video_id": "HLHhVyiOExA", "start": 983, "category": "Shooting", "level": "Intermediate"},
    "Jab Into Off Dribble Shot": {"video_id": "HLHhVyiOExA", "start": 1114, "category": "Shooting", "level": "Intermediate"},
    "Back Pivot Shot Fake Sweep": {"video_id": "HLHhVyiOExA", "start": 1199, "category": "Shooting", "level": "Intermediate"},
    "Spot Up Pull Up Layup Series": {"video_id": "HLHhVyiOExA", "start": 1259, "category": "Shooting", "level": "Intermediate"},
    # Advanced
    "Cold Three Point Shooting": {"video_id": "jR0iJmStMPs", "start": 79, "category": "Shooting", "level": "Advanced"},
    "Single Leg RDL Reach Shooting": {"video_id": "jR0iJmStMPs", "start": 108, "category": "Shooting", "level": "Advanced"},
    "Reverse Lunge Overhead Shooting": {"video_id": "jR0iJmStMPs", "start": 117, "category": "Shooting", "level": "Advanced"},
    "Side to Side Pop Shooting": {"video_id": "jR0iJmStMPs", "start": 134, "category": "Shooting", "level": "Advanced"},
    "Find the Seams Warm Up Shooting": {"video_id": "jR0iJmStMPs", "start": 145, "category": "Shooting", "level": "Advanced"},
    "Pivot Dribble Pickup Shooting": {"video_id": "jR0iJmStMPs", "start": 170, "category": "Shooting", "level": "Advanced"},
    "Double Behind Inverted Snatch Shooting": {"video_id": "jR0iJmStMPs", "start": 186, "category": "Shooting", "level": "Advanced"},
    "Change of Speed Push Out Shooting": {"video_id": "jR0iJmStMPs", "start": 208, "category": "Shooting", "level": "Advanced"},
    "Quick Form Shooting Streak": {"video_id": "jR0iJmStMPs", "start": 230, "category": "Shooting", "level": "Advanced"},
    "Ball Pickup Ground Shots": {"video_id": "jR0iJmStMPs", "start": 246, "category": "Shooting", "level": "Advanced"},
    "Double Pump Shots": {"video_id": "jR0iJmStMPs", "start": 260, "category": "Shooting", "level": "Advanced"},
    "Corner to Wing Three Point Shooting": {"video_id": "jR0iJmStMPs", "start": 279, "category": "Shooting", "level": "Advanced"},
    "High Speed Skip Into Three": {"video_id": "jR0iJmStMPs", "start": 309, "category": "Shooting", "level": "Advanced"},
    "One Knee Push Out Transition Shot": {"video_id": "jR0iJmStMPs", "start": 318, "category": "Shooting", "level": "Advanced"},
    "High Speed Acceleration Shooting": {"video_id": "jR0iJmStMPs", "start": 326, "category": "Shooting", "level": "Advanced"},
    "Cross Court Toss and Shoot": {"video_id": "jR0iJmStMPs", "start": 334, "category": "Shooting", "level": "Advanced"},
    "Corner to Corner Varied Footwork Shooting": {"video_id": "jR0iJmStMPs", "start": 345, "category": "Shooting", "level": "Advanced"},
    "One Dribble Uphill Hop Shot": {"video_id": "pq4DdAqX3yg", "start": 9, "category": "Shooting", "level": "Advanced"},
    "One Dribble Sideline Hop Shot": {"video_id": "pq4DdAqX3yg", "start": 34, "category": "Shooting", "level": "Advanced"},
    "Inside Outside Crossover Fadeaway": {"video_id": "pq4DdAqX3yg", "start": 52, "category": "Shooting", "level": "Advanced"},
    "Behind the Back Wrap Hop Shot": {"video_id": "pq4DdAqX3yg", "start": 87, "category": "Shooting", "level": "Advanced"},
    "Two Dribble Pullup and Fadeaway Alternating": {"video_id": "pq4DdAqX3yg", "start": 127, "category": "Shooting", "level": "Advanced"},
    "Floater Mid Range Catch and Shoot Series": {"video_id": "pq4DdAqX3yg", "start": 156, "category": "Shooting", "level": "Advanced"},
    "Step Back Mid Range and Three Point Catch and Shoot": {"video_id": "pq4DdAqX3yg", "start": 204, "category": "Shooting", "level": "Advanced"},
    "Slide Corner Three Wing Curl Sprint Three Series": {"video_id": "pq4DdAqX3yg", "start": 237, "category": "Shooting", "level": "Advanced"},
    "Top to Corner Sprint Dribble Shooting": {"video_id": "pq4DdAqX3yg", "start": 283, "category": "Shooting", "level": "Advanced"},
    "Five Minute Around the World Shooting": {"video_id": "pq4DdAqX3yg", "start": 328, "category": "Shooting", "level": "Advanced"},
    # Elite
    "One Dribble Variable Form Shooting": {"video_id": "GYMWi86DHhE", "start": 94, "category": "Shooting", "level": "Elite"},
    "Slight Drift Shooting": {"video_id": "GYMWi86DHhE", "start": 136, "category": "Shooting", "level": "Elite"},
    "Square Away Mid Air Shooting": {"video_id": "GYMWi86DHhE", "start": 172, "category": "Shooting", "level": "Elite"},
    "High Speed Chase and Shoot": {"video_id": "GYMWi86DHhE", "start": 304, "category": "Shooting", "level": "Elite"},
    "Contested Closeout Shooting": {"video_id": "GYMWi86DHhE", "start": 434, "category": "Shooting", "level": "Elite"},
    "Rotational Balance Hop Shooting": {"video_id": "GYMWi86DHhE", "start": 468, "category": "Shooting", "level": "Elite"},
    "Full 360 Turn Rim Find Shooting": {"video_id": "GYMWi86DHhE", "start": 573, "category": "Shooting", "level": "Elite"},
    "Hop Timing Catch and Shoot": {"video_id": "GYMWi86DHhE", "start": 727, "category": "Shooting", "level": "Elite"},
    "Energy Transfer Pull Down Shooting": {"video_id": "GYMWi86DHhE", "start": 801, "category": "Shooting", "level": "Elite"},
    "Defense Touch Toss and Shoot": {"video_id": "GYMWi86DHhE", "start": 963, "category": "Shooting", "level": "Elite"},
    "Three Dribble Three Pass Find the Shot": {"video_id": "GYMWi86DHhE", "start": 1072, "category": "Shooting", "level": "Elite"},
    "Closeout Backpedal Catch and Shoot": {"video_id": "GYMWi86DHhE", "start": 1204, "category": "Shooting", "level": "Elite"},
    "Miss Three Rotate Pressure Shooting": {"video_id": "GYMWi86DHhE", "start": 1228, "category": "Shooting", "level": "Elite"},
    "Dribble into Drop Step Shooting": {"video_id": "8uhumn1FVYY", "start": 0, "category": "Shooting", "level": "Elite"},
    "Corner Slide and Drop": {"video_id": "8uhumn1FVYY", "start": 149, "category": "Shooting", "level": "Elite"},
    "Drop Step with One Two Footwork": {"video_id": "8uhumn1FVYY", "start": 277, "category": "Shooting", "level": "Elite"},
    "Free Throw Line Verticality": {"video_id": "8uhumn1FVYY", "start": 546, "category": "Shooting", "level": "Elite"},
    "Drive and Drop Step Turn": {"video_id": "8uhumn1FVYY", "start": 872, "category": "Shooting", "level": "Elite"},
    "Ball Fake into Shot": {"video_id": "8uhumn1FVYY", "start": 1011, "category": "Shooting", "level": "Elite"},

    # ── DEFENSE ────────────────────────────────────────────────────────────
    "Lateral Line Jumps Warmup": {"video_id": "xoMov-_xDB4", "start": 92, "category": "Defense", "level": "Beginner"},
    "Four Way Single Leg Hops": {"video_id": "xoMov-_xDB4", "start": 126, "category": "Defense", "level": "Beginner"},
    "High Skips": {"video_id": "xoMov-_xDB4", "start": 139, "category": "Defense", "level": "Beginner"},
    "High Knees": {"video_id": "xoMov-_xDB4", "start": 149, "category": "Defense", "level": "Beginner"},
    "Lunge Twist with Explosive Jump": {"video_id": "xoMov-_xDB4", "start": 155, "category": "Defense", "level": "Beginner"},
    "Leg Pulls Hip Loosener": {"video_id": "xoMov-_xDB4", "start": 165, "category": "Defense", "level": "Beginner"},
    "Side Lunges": {"video_id": "xoMov-_xDB4", "start": 172, "category": "Defense", "level": "Beginner"},
    "Speed Skater Jumps": {"video_id": "xoMov-_xDB4", "start": 187, "category": "Defense", "level": "Beginner"},
    "Sprint Backpedal Sprint Warmup": {"video_id": "xoMov-_xDB4", "start": 196, "category": "Defense", "level": "Beginner"},
    "Four Cone Defensive Change of Direction": {"video_id": "xoMov-_xDB4", "start": 202, "category": "Defense", "level": "Beginner"},
    "Shuttle Slide and Sprint Drill": {"video_id": "xoMov-_xDB4", "start": 242, "category": "Defense", "level": "Beginner"},
    "Hip Flip Into Sprint": {"video_id": "xoMov-_xDB4", "start": 269, "category": "Defense", "level": "Beginner"},
    "Kobe Bryant Cutoff Drill": {"video_id": "xoMov-_xDB4", "start": 293, "category": "Defense", "level": "Beginner"},
    "Defensive Slides No Hip Turn Drill": {"video_id": "yxXEC_5xxYE", "start": 0, "category": "Defense", "level": "Intermediate"},
    "Attack Top Foot Cutoff Drill": {"video_id": "yxXEC_5xxYE", "start": 40, "category": "Defense", "level": "Intermediate"},
    "Attack Middle Cutoff Drill": {"video_id": "yxXEC_5xxYE", "start": 110, "category": "Defense", "level": "Intermediate"},
    "Four Cone Hip Cutoff Partner Drill": {"video_id": "yxXEC_5xxYE", "start": 154, "category": "Defense", "level": "Intermediate"},
    "Pin Inside Arm Steal Drill": {"video_id": "yxXEC_5xxYE", "start": 178, "category": "Defense", "level": "Intermediate"},
    "Ice Skaters": {"video_id": "m01zzaw80Jo", "start": 72, "category": "Defense", "level": "Intermediate"},
    "Ice Skater Pogos": {"video_id": "m01zzaw80Jo", "start": 96, "category": "Defense", "level": "Intermediate"},
    "Lateral Lunge 45 Degree Push": {"video_id": "m01zzaw80Jo", "start": 187, "category": "Defense", "level": "Intermediate"},
    "Single Leg Bounce Lateral Explosion": {"video_id": "m01zzaw80Jo", "start": 287, "category": "Defense", "level": "Intermediate"},
    "Crossover Step Footwork Drill": {"video_id": "m01zzaw80Jo", "start": 426, "category": "Defense", "level": "Intermediate"},
    "Lateral Shuffle with Punch Out": {"video_id": "m01zzaw80Jo", "start": 535, "category": "Defense", "level": "Intermediate"},
    "Diamond Closeout Cushion Slide Finisher": {"video_id": "m01zzaw80Jo", "start": 612, "category": "Defense", "level": "Intermediate"},
    "Defensive Slides with Jumper": {"video_id": "HLHhVyiOExA", "start": 308, "category": "Defense", "level": "Intermediate"},
    "Closeout Touch and Defend Drill": {"video_id": "mTkNmMqfTWs", "start": 78, "category": "Defense", "level": "Advanced"},
    "Full Court One on One Defensive Drill": {"video_id": "mTkNmMqfTWs", "start": 298, "category": "Defense", "level": "Advanced"},
    "Three on Three Full Court to Half Court": {"video_id": "mTkNmMqfTWs", "start": 443, "category": "Defense", "level": "Advanced"},
    "Shell Drill Baseline Drive Defense": {"video_id": "mTkNmMqfTWs", "start": 544, "category": "Defense", "level": "Advanced"},
    "Shell Drill Down Screen Defense": {"video_id": "mTkNmMqfTWs", "start": 759, "category": "Defense", "level": "Advanced"},
    "Three on Four Overload Scramble Drill": {"video_id": "mTkNmMqfTWs", "start": 851, "category": "Defense", "level": "Advanced"},
    "No Paint Drill": {"video_id": "mTkNmMqfTWs", "start": 1083, "category": "Defense", "level": "Advanced"},
    "Whistle Scramble Matchup Drill": {"video_id": "mTkNmMqfTWs", "start": 1299, "category": "Defense", "level": "Advanced"},
    "One on One Defensive Slides No Hip Opening": {"video_id": "o1Eid7669zY", "start": 0, "category": "Defense", "level": "Elite"},
    "Teacup Quick Turn Technique": {"video_id": "o1Eid7669zY", "start": 211, "category": "Defense", "level": "Elite"},
    "Pinky Drag Low Stance Drill": {"video_id": "o1Eid7669zY", "start": 310, "category": "Defense", "level": "Elite"},
    "Farmers Full Court Defensive Slides": {"video_id": "o1Eid7669zY", "start": 398, "category": "Defense", "level": "Elite"},
    "Steal and Deflection Timing Practice": {"video_id": "o1Eid7669zY", "start": 495, "category": "Defense", "level": "Elite"},
    "Physicality Body Contact Positioning": {"video_id": "o1Eid7669zY", "start": 678, "category": "Defense", "level": "Elite"},

    # ── POST MOVES ─────────────────────────────────────────────────────────
    "Face Up Rip Through": {"video_id": "1BkPSQL1ZzM", "start": 14, "category": "Post Moves", "level": "Beginner"},
    "Jab Cross": {"video_id": "1BkPSQL1ZzM", "start": 129, "category": "Post Moves", "level": "Beginner"},
    "Face Up Fadeaway": {"video_id": "1BkPSQL1ZzM", "start": 203, "category": "Post Moves", "level": "Beginner"},
    "Low Post Position Stability Drill": {"video_id": "FkoOzqGmJ3c", "start": 27, "category": "Post Moves", "level": "Beginner"},
    "Entry Pass Catch Drill": {"video_id": "FkoOzqGmJ3c", "start": 155, "category": "Post Moves", "level": "Beginner"},
    "Post Position with Ball Possession Drill": {"video_id": "FkoOzqGmJ3c", "start": 281, "category": "Post Moves", "level": "Beginner"},
    "Proper Post Catch and Position": {"video_id": "JANMMKsws5E", "start": 9, "category": "Post Moves", "level": "Intermediate"},
    "Bump and Jump Hook": {"video_id": "JANMMKsws5E", "start": 117, "category": "Post Moves", "level": "Intermediate"},
    "Up and Under": {"video_id": "JANMMKsws5E", "start": 124, "category": "Post Moves", "level": "Intermediate"},
    "Dribble Drop Step Baseline": {"video_id": "JANMMKsws5E", "start": 153, "category": "Post Moves", "level": "Intermediate"},
    "Drop Step Counter Pump Fake Step Through": {"video_id": "JANMMKsws5E", "start": 194, "category": "Post Moves", "level": "Intermediate"},
    "Catch Turn Pump Fake Counter": {"video_id": "JANMMKsws5E", "start": 257, "category": "Post Moves", "level": "Intermediate"},
    "Mid Post Face Up Jab and Drive": {"video_id": "JANMMKsws5E", "start": 326, "category": "Post Moves", "level": "Intermediate"},
    "Back Down Spin Crab Dribble Drill": {"video_id": "scTEsQJ5GRI", "start": 24, "category": "Post Moves", "level": "Intermediate"},
    "Glass Toss High Finish": {"video_id": "scTEsQJ5GRI", "start": 92, "category": "Post Moves", "level": "Intermediate"},
    "Glass Toss Crab Dribble Finish": {"video_id": "scTEsQJ5GRI", "start": 136, "category": "Post Moves", "level": "Intermediate"},
    "Glass Toss Hook Shot": {"video_id": "scTEsQJ5GRI", "start": 176, "category": "Post Moves", "level": "Intermediate"},
    "Cross Step Spin Finish": {"video_id": "scTEsQJ5GRI", "start": 240, "category": "Post Moves", "level": "Intermediate"},
    "Cross Step Through Finish": {"video_id": "scTEsQJ5GRI", "start": 279, "category": "Post Moves", "level": "Intermediate"},
    "Post Shooting Step to Ball": {"video_id": "scTEsQJ5GRI", "start": 332, "category": "Post Moves", "level": "Intermediate"},
    "Mid Post Rip Spin": {"video_id": "aRm82j__ogo", "start": 26, "category": "Post Moves", "level": "Intermediate"},
    "Face Up Jab Shot Fake and Drive": {"video_id": "MEJOcdykhYs", "start": 42, "category": "Post Moves", "level": "Intermediate"},
    "Drop Step Post Spin": {"video_id": "MEJOcdykhYs", "start": 163, "category": "Post Moves", "level": "Intermediate"},
    "Double Shot Fake Step Through": {"video_id": "MEJOcdykhYs", "start": 285, "category": "Post Moves", "level": "Intermediate"},
    "Jump Stop Both Feet Post Positioning": {"video_id": "rfRENRC5lIk", "start": 15, "category": "Post Moves", "level": "Advanced"},
    "Turnaround Jump Shot": {"video_id": "rfRENRC5lIk", "start": 129, "category": "Post Moves", "level": "Advanced"},
    "Pivot Shot Fake Right Side Attack": {"video_id": "rfRENRC5lIk", "start": 154, "category": "Post Moves", "level": "Advanced"},
    "Jump Stop Baby Hook": {"video_id": "rfRENRC5lIk", "start": 212, "category": "Post Moves", "level": "Advanced"},
    "Shot Fake One Dribble Middle Turnaround": {"video_id": "rfRENRC5lIk", "start": 233, "category": "Post Moves", "level": "Advanced"},
    "Pivot Left Side One Dribble Jump Stop Shot": {"video_id": "rfRENRC5lIk", "start": 301, "category": "Post Moves", "level": "Advanced"},
    "Shot Fake Floater Left Side": {"video_id": "rfRENRC5lIk", "start": 322, "category": "Post Moves", "level": "Advanced"},
    "Shot Fake Dribble Back Attack": {"video_id": "rfRENRC5lIk", "start": 336, "category": "Post Moves", "level": "Advanced"},
    "Shot Fake Pivot Practice Drill": {"video_id": "rfRENRC5lIk", "start": 422, "category": "Post Moves", "level": "Advanced"},

    # ── FINISHING ──────────────────────────────────────────────────────────
    "Attack Retreat and Finish": {"video_id": "HLHhVyiOExA", "start": 456, "category": "Finishing", "level": "Intermediate"},
    "Modified Mikan Inside Hand Drill": {"video_id": "Ajzf6XgUYO8", "start": 39, "category": "Finishing", "level": "Intermediate"},
    "Wide Hook Touch Drill": {"video_id": "Ajzf6XgUYO8", "start": 57, "category": "Finishing", "level": "Intermediate"},
    "Side to Side Cradle Finish": {"video_id": "Ajzf6XgUYO8", "start": 65, "category": "Finishing", "level": "Intermediate"},
    "Two Foot Change of Direction Baseline Finish": {"video_id": "Ajzf6XgUYO8", "start": 93, "category": "Finishing", "level": "Intermediate"},
    "Two Foot Change of Direction Middle Finish": {"video_id": "Ajzf6XgUYO8", "start": 127, "category": "Finishing", "level": "Intermediate"},
    "Two Foot Floater Finish": {"video_id": "Ajzf6XgUYO8", "start": 137, "category": "Finishing", "level": "Intermediate"},
    "Cradle Change of Direction Series": {"video_id": "Ajzf6XgUYO8", "start": 144, "category": "Finishing", "level": "Intermediate"},
    "One Hand Overhead Gather Drill": {"video_id": "Ajzf6XgUYO8", "start": 174, "category": "Finishing", "level": "Intermediate"},
    "Show Ball Cradle Finish": {"video_id": "Ajzf6XgUYO8", "start": 185, "category": "Finishing", "level": "Intermediate"},
    "Show Ball Gyro Counter Finish": {"video_id": "Ajzf6XgUYO8", "start": 205, "category": "Finishing", "level": "Intermediate"},
    "Show Ball Inside Hand Finish": {"video_id": "Ajzf6XgUYO8", "start": 215, "category": "Finishing", "level": "Intermediate"},
    "Off Foot Same Hand Layup": {"video_id": "Ajzf6XgUYO8", "start": 225, "category": "Finishing", "level": "Intermediate"},
    "Off Foot Underhand Floater": {"video_id": "Ajzf6XgUYO8", "start": 247, "category": "Finishing", "level": "Intermediate"},
    "Off Foot Reverse Layup": {"video_id": "Ajzf6XgUYO8", "start": 255, "category": "Finishing", "level": "Intermediate"},
    "Layups From Anywhere": {"video_id": "Ajzf6XgUYO8", "start": 270, "category": "Finishing", "level": "Intermediate"},
    "Offhand Floater Baseline One Foot": {"video_id": "Ajzf6XgUYO8", "start": 293, "category": "Finishing", "level": "Intermediate"},
    "Offhand Floater Middle One Foot": {"video_id": "Ajzf6XgUYO8", "start": 310, "category": "Finishing", "level": "Intermediate"},
    "Offhand Two Foot Floater Series": {"video_id": "Ajzf6XgUYO8", "start": 315, "category": "Finishing", "level": "Intermediate"},
    "Same Foot Same Hand Finish": {"video_id": "n67j58oHcdA", "start": 17, "category": "Finishing", "level": "Intermediate"},
    "Mixed Finishes Five Cone Series": {"video_id": "n67j58oHcdA", "start": 197, "category": "Finishing", "level": "Intermediate"},
    "Unpredictability Quicksand Finish": {"video_id": "D3pimUFPaIU", "start": 48, "category": "Finishing", "level": "Advanced"},
    "Contact Initiation Ground Positioning": {"video_id": "D3pimUFPaIU", "start": 83, "category": "Finishing", "level": "Advanced"},
    "Two Foot Contact Finish": {"video_id": "D3pimUFPaIU", "start": 119, "category": "Finishing", "level": "Advanced"},
    "Finishing on the Way Down": {"video_id": "D3pimUFPaIU", "start": 174, "category": "Finishing", "level": "Advanced"},
    "Ball Protection and Baiting": {"video_id": "D3pimUFPaIU", "start": 207, "category": "Finishing", "level": "Advanced"},
    "Cuff Euro Step Finish": {"video_id": "zh2JLinO-ws", "start": 56, "category": "Finishing", "level": "Elite"},
    "Weak Hand Extension Footwork Finish": {"video_id": "zh2JLinO-ws", "start": 95, "category": "Finishing", "level": "Elite"},
    "One Step Inside Hand Fade Finish": {"video_id": "zh2JLinO-ws", "start": 126, "category": "Finishing", "level": "Elite"},
    "High Backboard Underhand Flick": {"video_id": "zh2JLinO-ws", "start": 168, "category": "Finishing", "level": "Elite"},
    "Midair Knee Touch Cradle Finish": {"video_id": "zh2JLinO-ws", "start": 197, "category": "Finishing", "level": "Elite"},
    "Spin Step Inside Hand Finish": {"video_id": "zh2JLinO-ws", "start": 237, "category": "Finishing", "level": "Elite"},
    "No Jump High Speed Touch Finish": {"video_id": "zh2JLinO-ws", "start": 268, "category": "Finishing", "level": "Elite"},
    "Variable Mikan Different Finishes": {"video_id": "zh2JLinO-ws", "start": 294, "category": "Finishing", "level": "Elite"},
    "Eyes Closed Late Open Finishing": {"video_id": "zh2JLinO-ws", "start": 332, "category": "Finishing", "level": "Elite"},
}

def get_drill_names_for_prompt():
    """Return organized drill names by category and level for the Claude prompt."""
    organized = {}
    for name, info in DRILL_LIBRARY.items():
        cat = info["category"]
        lvl = info["level"]
        key = f"{cat} - {lvl}"
        if key not in organized:
            organized[key] = []
        organized[key].append(name)
    return organized

@app.route("/", methods=["GET", "POST"])
def index():
    plan = None
    if request.method == "POST":
        position = request.form["position"]
        weaknesses = request.form["weaknesses"]
        time_available = request.form["time"]
        skill_level = request.form.get("skill_level", "Intermediate")
        equipment = request.form.get("equipment", "Full gym")

        drill_names = get_drill_names_for_prompt()
        drill_list_str = ""
        for category, names in drill_names.items():
            drill_list_str += f"\n{category}:\n"
            for n in names:
                drill_list_str += f"  - {n}\n"

        message = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=2048,
            messages=[
                {"role": "user", "content": f"""Create a basketball practice plan for a {skill_level} {position} who wants to improve {weaknesses} and has {time_available} minutes available. They have access to: {equipment}.

IMPORTANT: You MUST only use drills from this exact list. Do not invent or rename drills. Use the exact drill names as written:

{drill_list_str}

Choose drills appropriate for {skill_level} level. Focus on drills relevant to improving {weaknesses}.

Format your response EXACTLY like this — use these exact section headers and structure:

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

Use only drill names from the list above. Include 2-4 drills per section. Adjust sections to fill exactly {time_available} minutes."""}
            ]
        )
        plan = message.content[0].text

    return render_template("index.html", plan=plan, drill_library=json.dumps(DRILL_LIBRARY))

if __name__ == "__main__":
    app.run(debug=True)
