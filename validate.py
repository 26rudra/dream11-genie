"""Deterministic Dream11 rule validator.

LLMs reason well but slip on hard numeric/count constraints (credits, per-team
caps). We never trust the model to police those — we check them in code, and
feed any violations back for a single correction pass (see agent.pick_team).
"""
from __future__ import annotations

from collections import Counter

from data import PLAYERS
from schema import Pick, Team

RULES = {
    "size": 11,
    "composition": {"WK": (1, 4), "BAT": (3, 6), "AR": (1, 4), "BOWL": (3, 6)},
    "max_credits": 100.0,
    "max_per_team": 7,
}


def validate_team(team) -> tuple[list[str], dict]:
    """Return (list of rule violations, summary stats). Empty list == valid."""
    issues: list[str] = []
    names = [p.player for p in team.players]
    known = [n for n in names if n in PLAYERS]

    unknown = [n for n in names if n not in PLAYERS]
    if unknown:
        issues.append(f"players not in the squad data: {unknown}")
    if len(names) != RULES["size"]:
        issues.append(f"must be {RULES['size']} players, got {len(names)}")
    if len(set(names)) != len(names):
        issues.append("duplicate players in the XI")

    roles = Counter(PLAYERS[n]["role"] for n in known)
    for role, (lo, hi) in RULES["composition"].items():
        c = roles.get(role, 0)
        if not (lo <= c <= hi):
            issues.append(f"{role} count is {c}, must be {lo}-{hi}")

    credits = round(sum(PLAYERS[n]["credits"] for n in known), 1)
    if credits > RULES["max_credits"]:
        issues.append(f"total credits {credits} exceed the {RULES['max_credits']} cap")

    teams = Counter(PLAYERS[n]["team"] for n in known)
    for t, c in teams.items():
        if c > RULES["max_per_team"]:
            issues.append(f"{c} players from {t} — max {RULES['max_per_team']} from one team")

    if team.captain not in names:
        issues.append("captain is not in the XI")
    if team.vice_captain not in names:
        issues.append("vice-captain is not in the XI")
    if team.captain == team.vice_captain:
        issues.append("captain and vice-captain are the same player")

    return issues, {"credits": credits, "roles": dict(roles), "teams": dict(teams)}


def repair_credits(team: Team) -> Team:
    """Deterministically bring an over-budget XI under the credit cap.

    Greedily swaps the priciest NON-captain players for the cheapest unused
    same-role player, never breaking the per-team cap. This is the 'hard numeric
    constraint belongs in code, not the LLM' pattern — guaranteed correct.
    Composition and per-team validity are preserved (same-role swaps only).
    """
    names = [p.player for p in team.players]
    reasons = {p.player: p.reason for p in team.players}
    original = {p.player: p for p in team.players}  # fall back to these for names not in squad data
    protected = {team.captain, team.vice_captain}

    def total(ns):
        return round(sum(PLAYERS[n]["credits"] for n in ns if n in PLAYERS), 1)

    def team_counts(ns):
        return Counter(PLAYERS[n]["team"] for n in ns if n in PLAYERS)

    guard = 0
    while total(names) > RULES["max_credits"] and guard < 30:
        guard += 1
        best = None  # (key, index, replacement_name) — key sorts by least quality lost
        for i, n in enumerate(names):
            if n in protected or n not in PLAYERS:
                continue
            role, cost = PLAYERS[n]["role"], PLAYERS[n]["credits"]
            for cand, cp in PLAYERS.items():
                if cand in names or cp["role"] != role:
                    continue
                trial = names.copy(); trial[i] = cand
                if any(v > RULES["max_per_team"] for v in team_counts(trial).values()):
                    continue
                saving = cost - cp["credits"]
                if saving <= 0:
                    continue
                # prefer the swap that loses the FEWEST fantasy points; break ties
                # toward the bigger credit saving (fewer total swaps needed).
                pts_loss = PLAYERS[n]["avg_fantasy_points"] - cp["avg_fantasy_points"]
                key = (pts_loss, -saving)
                if best is None or key < best[0]:
                    best = (key, i, cand)
        if not best:
            break
        _, i, cand = best
        old = names[i]
        names[i] = cand
        reasons[cand] = f"Budget swap in for {old} — {PLAYERS[cand]['note']}"

    # Rebuild from squad data for known players; for any name the model invented
    # that isn't in the squad data, keep its original Pick (repair never swaps
    # those, and looking them up in PLAYERS would KeyError). validate_team still
    # flags them afterward — we just don't crash on the way out.
    picks = []
    for n in names:
        if n in PLAYERS:
            picks.append(Pick(player=n, team=PLAYERS[n]["team"], role=PLAYERS[n]["role"],
                              reason=reasons.get(n, PLAYERS[n]["note"])))
        else:
            picks.append(original[n])
    return Team(match=team.match, captain=team.captain, vice_captain=team.vice_captain,
                players=picks, strategy=team.strategy)


def player_pool_text(match: str | None = None) -> str:
    """A compact 'name — TEAM, ROLE, credits' pool for the correction prompt."""
    lines = [
        f"{n} — {p['team']}, {p['role']}, {p['credits']} cr"
        for n, p in PLAYERS.items()
    ]
    return "\n".join(lines)
