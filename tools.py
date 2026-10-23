"""The Dream11 Genie tools — the agent's 'hands'.

Each function has a clear docstring + typed signature, because that IS the tool
schema the model reads. They're plain Python functions so they're trivial to
unit-test; LangGraph wraps them into tools automatically in agent.py.

Right now they read baked-in sample data (data.py). To go live, replace the
bodies with real API calls — the signatures stay identical, so nothing else changes.
"""
from __future__ import annotations

from data import PLAYERS, SQUADS, PITCH, FORM


def _find_player(name: str):
    """Case-insensitive / partial-name lookup so the model doesn't need exact spelling."""
    if not name:
        return None, None
    q = name.strip().lower()
    # exact (case-insensitive)
    for full, stats in PLAYERS.items():
        if full.lower() == q:
            return full, stats
    # substring / last-name match
    matches = [(f, s) for f, s in PLAYERS.items() if q in f.lower() or q in f.lower().split()[-1]]
    if len(matches) == 1:
        return matches[0]
    return None, None


def get_match_squads(match: str) -> dict:
    """Return the available squads and venue for a fixture.

    Call this FIRST so you know which players you may pick and where the game is.
    `match` should look like 'CSK vs MI'. Returns the venue and each team's player list.
    """
    key = match.strip()
    if key not in SQUADS:
        # try a loose match on the code pair
        for k in SQUADS:
            if set(k.lower().replace(" vs ", " ").split()) == set(key.lower().replace(" vs ", " ").split()):
                key = k
                break
    if key not in SQUADS:
        return {"error": f"No squad data for '{match}'. Available: {list(SQUADS)}"}
    return SQUADS[key]


def get_player_stats(player: str) -> dict:
    """Return recent form and fantasy stats for ONE player.

    Use this before selecting anyone — never guess a player's form. Accepts a full
    name or a last name (e.g. 'Gaikwad'). Returns role, credits, last-5 outings,
    averages and average fantasy points.
    """
    full, stats = _find_player(player)
    if not stats:
        return {"error": f"No stats found for '{player}'. Use a name from get_match_squads."}
    return {"name": full, **stats}


def search_form(team: str) -> str:
    """Return a short scouting note on a team's current form, injuries and in-form players.

    `team` is a short code like 'CSK' or 'MI'.
    """
    code = team.strip().upper()
    if code not in FORM:
        return f"No form notes for '{team}'. Known teams: {list(FORM)}"
    return FORM[code]


def get_pitch_report(venue: str) -> dict:
    """Return the pitch and weather report for a venue.

    Accepts the full venue name or a keyword like 'Chepauk'. Returns surface
    behaviour, average first-innings score, pace-vs-spin bias, dew and a recommendation.
    """
    q = venue.strip().lower()
    for name, report in PITCH.items():
        if q in name.lower():
            return report
    return {"error": f"No pitch report for '{venue}'. Known venues: {list(PITCH)}"}


# The toolset the agent is given (plain callables — LangGraph builds the schemas).
TOOLS = [get_match_squads, get_player_stats, search_form, get_pitch_report]
