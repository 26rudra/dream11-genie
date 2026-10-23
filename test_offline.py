"""Offline tests — no API key or network needed.

Validates the tools and schema (the deterministic plumbing) so we know the data
layer is sound BEFORE spending Groq calls on the full agent. Run: python test_offline.py
"""
from data import PLAYERS, SQUADS
from schema import Pick, Team
from tools import get_match_squads, get_player_stats, search_form, get_pitch_report
from validate import validate_team, repair_credits


def check(name, cond):
    print(f"  {'✅' if cond else '❌'} {name}")
    assert cond, f"FAILED: {name}"


def main():
    print("Offline tests — tools & schema")

    squads = get_match_squads("CSK vs MI")
    check("get_match_squads returns venue", "Chepauk" in squads["venue"])
    check("both squads present", set(squads["teams"]) == {"CSK", "MI"})
    check("squads are non-empty", len(squads["teams"]["CSK"]) >= 11 and len(squads["teams"]["MI"]) >= 11)

    # loose match code
    check("loose fixture match ('MI vs CSK')", "error" not in get_match_squads("MI vs CSK"))

    stats = get_player_stats("Gaikwad")            # last-name lookup
    check("partial-name player lookup", stats.get("name") == "Ruturaj Gaikwad")
    check("player stats have role & points", "role" in stats and "avg_fantasy_points" in stats)
    check("unknown player returns error", "error" in get_player_stats("Nobody McNobody"))

    check("pitch report by keyword ('Chepauk')", "recommendation" in get_pitch_report("Chepauk"))
    check("team form note ('CSK')", "Gaikwad" in search_form("CSK"))
    check("unknown team handled", "No form notes" in search_form("XYZ"))

    # schema round-trips
    team = Team(
        match="CSK vs MI", captain="Ruturaj Gaikwad", vice_captain="Suryakumar Yadav",
        players=[Pick(player="Ruturaj Gaikwad", team="CSK", role="BAT", reason="in form")],
        strategy="spin-heavy",
    )
    check("Team schema validates", team.captain == "Ruturaj Gaikwad")

    # every squad player has stats
    all_named = set(SQUADS["CSK vs MI"]["teams"]["CSK"]) | set(SQUADS["CSK vs MI"]["teams"]["MI"])
    check("every squad player has a stats entry", all_named == set(PLAYERS))

    # --- validator + deterministic repair ---
    def pick(n):
        return Pick(player=n, team=PLAYERS[n]["team"], role=PLAYERS[n]["role"], reason="x")

    # a composition/team-valid but OVER-BUDGET (103 cr) XI
    over = Team(
        match="CSK vs MI", captain="Suryakumar Yadav", vice_captain="Ruturaj Gaikwad",
        players=[pick(n) for n in [
            "Ishan Kishan", "Ruturaj Gaikwad", "Suryakumar Yadav", "Rohit Sharma",
            "Ravindra Jadeja", "Hardik Pandya", "Jasprit Bumrah", "Deepak Chahar",
            "Maheesh Theekshana", "Matheesha Pathirana", "Gerald Coetzee"]],
        strategy="s",
    )
    issues, meta = validate_team(over)
    check("validator flags an over-budget XI", any("credit" in i for i in issues))
    check("over-budget XI is indeed >100", meta["credits"] > 100)

    fixed = repair_credits(over)
    fissues, fmeta = validate_team(fixed)
    check("repair brings credits within cap", fmeta["credits"] <= 100)
    check("repaired XI passes ALL rules", fissues == [])
    check("captain preserved through repair", fixed.captain == "Suryakumar Yadav")
    check("repaired XI still has 11 players", len(fixed.players) == 11)

    print("\n✅ All offline tests passed.")


if __name__ == "__main__":
    main()
