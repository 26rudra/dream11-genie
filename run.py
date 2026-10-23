"""CLI runner for Dream11 Genie.

Usage:
    python run.py                 # defaults to "CSK vs MI"
    python run.py "CSK vs MI"     # pick a fixture we have sample data for
    python run.py "CSK vs MI" -q  # quiet (hide the agent trace)
"""
import sys

from agent import pick_team
from validate import validate_team


def _format(team) -> str:
    lines = [f"\n🏏  DREAM11 GENIE — {team.match}", "=" * 52]
    lines.append(f"Captain     ⭐ {team.captain}")
    lines.append(f"Vice-Capt.  🔸 {team.vice_captain}")
    lines.append("-" * 52)
    for i, p in enumerate(team.players, 1):
        tag = "⭐" if p.player == team.captain else ("🔸" if p.player == team.vice_captain else "  ")
        lines.append(f"{i:>2}. {tag} {p.player:<22} {p.role:<5} {p.team:<4} — {p.reason}")
    lines.append("-" * 52)
    lines.append(f"Strategy: {team.strategy}")
    return "\n".join(lines)


def main() -> None:
    args = [a for a in sys.argv[1:]]
    quiet = "-q" in args or "--quiet" in args
    args = [a for a in args if not a.startswith("-")]
    match = args[0] if args else "CSK vs MI"

    print(f"Building your XI for '{match}' … (the agent is calling tools and reasoning)")
    team = pick_team(match, verbose=not quiet)
    print(_format(team))

    issues, meta = validate_team(team)
    print("-" * 52)
    print(f"Credits: {meta['credits']}/100   |   By team: {meta['teams']}   |   Roles: {meta['roles']}")
    if issues:
        print("❌ RULES CHECK FAILED: " + "; ".join(issues))
    else:
        print(f"✅ Valid Dream11 XI — {len(team.players)} players, all rules satisfied.")


if __name__ == "__main__":
    main()
