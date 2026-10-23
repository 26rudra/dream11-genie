"""Baked-in SAMPLE data for Dream11 Genie.

This is illustrative sample data for ONE fixture so the project runs offline and
deterministically — no third-party sports API or extra key needed. The tool
functions in tools.py read from here. To go live, swap these dicts for real API
calls (the tool signatures stay the same).

Stats are representative samples, not live/official numbers.
"""

VENUE = "MA Chidambaram Stadium, Chepauk"

# --- Pitch & conditions for the venue -------------------------------------
PITCH = {
    "MA Chidambaram Stadium, Chepauk": {
        "venue": "MA Chidambaram Stadium, Chepauk",
        "surface": "Dry, spin-friendly; grips and turns as the game wears on",
        "avg_first_innings": 165,
        "pace_vs_spin": "Spinners dominate; wrist-spin especially effective",
        "dew": "Light dew after 8:30 PM — a small edge to the chasing side",
        "recommendation": "Load up on quality spinners and in-form top-order batters; "
                          "medium-pace/cutters do better than express seam.",
    }
}

# --- Team form / news blurbs ----------------------------------------------
FORM = {
    "CSK": "CSK are in good rhythm. Ruturaj Gaikwad is in sublime touch at the top. "
           "Ravindra Jadeja is contributing with both bat and ball. Matheesha Pathirana "
           "is back from a minor niggle and bowling at full tilt. Moeen Ali and Theekshana "
           "give strong spin options that suit Chepauk.",
    "MI": "MI are batting-heavy and dangerous. Suryakumar Yadav is in red-hot form. "
          "Jasprit Bumrah has been near-unplayable at the death. Rohit Sharma has looked "
          "scratchy and inconsistent. Their spin depth is thinner than CSK's, a concern on a turner.",
}

# --- Squads (name -> stats) -----------------------------------------------
# role: WK / BAT / AR / BOWL ; credits: Dream11-style 7.0-11.0
# 'recent' = last 5 outings (runs for batters, wickets for bowlers)
SQUADS = {
    "CSK vs MI": {
        "venue": VENUE,
        "teams": {"CSK": [], "MI": []},  # filled below from PLAYERS
    }
}

PLAYERS = {
    # ---------------- CSK ----------------
    "Ruturaj Gaikwad": {"team": "CSK", "role": "BAT", "credits": 10.5, "recent": [92, 46, 71, 58, 27],
                        "batting_avg": 48.2, "strike_rate": 141, "avg_fantasy_points": 78,
                        "note": "In-form opener; anchors and accelerates. Strong captaincy pick."},
    "MS Dhoni": {"team": "CSK", "role": "WK", "credits": 9.0, "recent": [20, 14, 9, 27, 4],
                 "batting_avg": 22.0, "strike_rate": 190, "avg_fantasy_points": 34,
                 "note": "Bats only a few overs now but explosive finisher + keeper points."},
    "Devon Conway": {"team": "CSK", "role": "BAT", "credits": 9.5, "recent": [8, 56, 40, 12, 63],
                     "batting_avg": 41.0, "strike_rate": 139, "avg_fantasy_points": 58,
                     "note": "Reliable left-hand opener; can also keep."},
    "Shivam Dube": {"team": "CSK", "role": "AR", "credits": 9.0, "recent": [51, 34, 66, 8, 39],
                    "batting_avg": 38.5, "strike_rate": 162, "avg_fantasy_points": 61,
                    "note": "Powerful middle-order hitter vs spin; bowls a little."},
    "Ravindra Jadeja": {"team": "CSK", "role": "AR", "credits": 9.5, "recent": [37, 24, 18, 41, 29],
                        "batting_avg": 30.0, "strike_rate": 148, "avg_fantasy_points": 72,
                        "note": "Genuine all-rounder; left-arm spin ideal for Chepauk + fielding points."},
    "Moeen Ali": {"team": "CSK", "role": "AR", "credits": 8.5, "recent": [12, 28, 3, 44, 19],
                  "batting_avg": 24.0, "strike_rate": 155, "avg_fantasy_points": 49,
                  "note": "Off-spin all-rounder; turns it on this deck."},
    "Deepak Chahar": {"team": "CSK", "role": "BOWL", "credits": 8.5, "recent": [2, 1, 3, 0, 2],
                      "bowling_econ": 8.1, "avg_fantasy_points": 47,
                      "note": "New-ball swing; wicket threat in the powerplay."},
    "Matheesha Pathirana": {"team": "CSK", "role": "BOWL", "credits": 9.0, "recent": [3, 2, 4, 1, 3],
                            "bowling_econ": 7.8, "avg_fantasy_points": 66,
                            "note": "Slingy yorkers at the death; back from a niggle, bowling well."},
    "Maheesh Theekshana": {"team": "CSK", "role": "BOWL", "credits": 8.5, "recent": [2, 3, 1, 2, 2],
                           "bowling_econ": 7.2, "avg_fantasy_points": 52,
                           "note": "Mystery spinner; excellent on turning tracks."},
    "Tushar Deshpande": {"team": "CSK", "role": "BOWL", "credits": 8.0, "recent": [1, 2, 0, 3, 1],
                         "bowling_econ": 9.4, "avg_fantasy_points": 40,
                         "note": "Enthusiastic seamer but leaks on spin decks."},
    "Ajinkya Rahane": {"team": "CSK", "role": "BAT", "credits": 8.0, "recent": [29, 45, 11, 33, 7],
                       "batting_avg": 27.0, "strike_rate": 140, "avg_fantasy_points": 42,
                       "note": "Experienced; can bat spin but strike rate dips."},
    "Daryl Mitchell": {"team": "CSK", "role": "AR", "credits": 8.5, "recent": [22, 39, 63, 17, 30],
                       "batting_avg": 35.0, "strike_rate": 138, "avg_fantasy_points": 50,
                       "note": "Solid middle-order; occasional medium pace."},

    # ---------------- MI ----------------
    "Rohit Sharma": {"team": "MI", "role": "BAT", "credits": 10.0, "recent": [11, 43, 8, 26, 5],
                     "batting_avg": 24.5, "strike_rate": 148, "avg_fantasy_points": 44,
                     "note": "Match-winner on his day but out of form recently."},
    "Ishan Kishan": {"team": "MI", "role": "WK", "credits": 9.0, "recent": [42, 69, 18, 33, 55],
                     "batting_avg": 39.0, "strike_rate": 152, "avg_fantasy_points": 62,
                     "note": "Aggressive keeper-bat opener; keeper points a bonus."},
    "Suryakumar Yadav": {"team": "MI", "role": "BAT", "credits": 10.5, "recent": [78, 43, 102, 31, 65],
                         "batting_avg": 52.0, "strike_rate": 176, "avg_fantasy_points": 88,
                         "note": "In sensational form; best-in-world vs both pace and spin. Captaincy pick."},
    "Tilak Varma": {"team": "MI", "role": "AR", "credits": 9.0, "recent": [46, 32, 57, 21, 40],
                    "batting_avg": 40.0, "strike_rate": 150, "avg_fantasy_points": 56,
                    "note": "Left-hander who plays spin superbly; bowls a bit of off-spin."},
    "Hardik Pandya": {"team": "MI", "role": "AR", "credits": 9.5, "recent": [28, 19, 44, 33, 12],
                      "batting_avg": 28.0, "strike_rate": 145, "avg_fantasy_points": 58,
                      "note": "All-round points floor from bat + a few overs of seam."},
    "Tim David": {"team": "MI", "role": "AR", "credits": 8.5, "recent": [37, 8, 46, 22, 30],
                  "batting_avg": 31.0, "strike_rate": 168, "avg_fantasy_points": 47,
                  "note": "Death-overs power hitter."},
    "Jasprit Bumrah": {"team": "MI", "role": "BOWL", "credits": 9.5, "recent": [3, 4, 2, 3, 4],
                       "bowling_econ": 6.4, "avg_fantasy_points": 82,
                       "note": "Elite wicket threat and economy; nailed-on pick."},
    "Piyush Chawla": {"team": "MI", "role": "BOWL", "credits": 8.0, "recent": [2, 1, 3, 1, 2],
                      "bowling_econ": 7.9, "avg_fantasy_points": 45,
                      "note": "Leg-spin — handy on a Chepauk turner."},
    "Gerald Coetzee": {"team": "MI", "role": "BOWL", "credits": 8.5, "recent": [2, 3, 1, 2, 1],
                       "bowling_econ": 9.1, "avg_fantasy_points": 43,
                       "note": "Express pace; wickets but can go for runs on slow decks."},
    "Nuwan Thushara": {"team": "MI", "role": "BOWL", "credits": 8.0, "recent": [3, 1, 2, 2, 0],
                       "bowling_econ": 8.6, "avg_fantasy_points": 41,
                       "note": "Sidearm angles; new-ball threat."},
    "Dewald Brevis": {"team": "MI", "role": "BAT", "credits": 8.0, "recent": [17, 46, 25, 8, 39],
                      "batting_avg": 27.0, "strike_rate": 158, "avg_fantasy_points": 44,
                      "note": "Young power hitter who attacks spin."},
    "Naman Dhir": {"team": "MI", "role": "AR", "credits": 7.5, "recent": [24, 12, 33, 9, 20],
                   "batting_avg": 22.0, "strike_rate": 149, "avg_fantasy_points": 36,
                   "note": "Fringe all-rounder; part-time off-spin."},
}

# populate squad name lists from PLAYERS
for _name, _p in PLAYERS.items():
    SQUADS["CSK vs MI"]["teams"][_p["team"]].append(_name)
