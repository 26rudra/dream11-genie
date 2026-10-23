"""Dream11 Genie — the agent itself.

A ReAct agent powered by Groq (free tier), built with LangChain's create_agent
(which runs on LangGraph underneath). It reasons about a fixture,
calls the tools to gather live-style data, then returns a structured XI with a
captain, vice-captain and a reason for every pick.

Needs a free Groq API key in the environment as GROQ_API_KEY (see .env.example).
"""
from __future__ import annotations

import os

from dotenv import load_dotenv, find_dotenv
from langchain_groq import ChatGroq
from langchain.agents import create_agent

from schema import Team
from tools import TOOLS
from validate import validate_team, player_pool_text, repair_credits

# Find a .env by walking up from the current directory (so it works whether the
# key sits in this project folder or a parent course folder).
load_dotenv(find_dotenv(usecwd=True))

# Groq (free tier) with LangGraph. openai/gpt-oss-120b is Groq's flagship
# tool-use model. Override via GROQ_MODEL (e.g. "openai/gpt-oss-20b" for speed).
# Needs GROQ_API_KEY in the environment — get a free key at https://console.groq.com/keys
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

# NOTE: describe the tools in plain prose, NOT as `name(args)` — showing
# function-call syntax makes some models imitate it as text and break tool-calling.
SYSTEM = """You are Dream11 Genie, an expert fantasy-cricket advisor.
Given a match, build the single best Dream11 XI and explain it.

Work like a real analyst — use your tools to gather facts, and never guess a player's form:
- First, look up the match squads and the venue.
- Check the pitch and weather report for that venue.
- Read the recent-form scouting note for both teams.
- Look up the recent stats for every player you seriously consider (at least a dozen).
Then reason about form, role balance, the pitch bias and match-ups before deciding.

TEAM RULES:
- Exactly 11 players.
- Valid composition: 1-4 wicket-keepers (WK), 3-6 batters (BAT),
  1-4 all-rounders (AR), 3-6 bowlers (BOWL).
- Total credits must not exceed 100.
- At most 7 players from any one team.
- Name a CAPTAIN (scores 2x) and a VICE-CAPTAIN (scores 1.5x) — your highest-ceiling,
  in-form picks suited to the conditions.

Finish with the final XI: each player with a one-line reason, plus a short overall
strategy. Back the picks the data supports, not big names who are out of form.
"""


# max_retries: the free Groq tier allows 8000 tokens per MINUTE, and this agent's
# context grows with every tool call — by the later steps a single request is ~4k,
# so two of them inside one minute trips the limit on a single run, with nobody
# else on your key. langchain-groq defaults to 2 retries, which is not enough for
# a long run; the Groq SDK honours the retry-after header, so raising this simply
# waits out the window instead of failing the whole run.
def _llm(temperature: float = 0.2, **kwargs) -> ChatGroq:
    kwargs.setdefault("max_retries", 8)
    return ChatGroq(model=MODEL, temperature=temperature, **kwargs)


def build_agent():
    """Return the compiled ReAct agent (LLM + tools + loop)."""
    return create_agent(_llm(), TOOLS, system_prompt=SYSTEM)


def pick_team(match: str, verbose: bool = False) -> Team:
    """Run the agent end-to-end for a fixture and return a structured Team.

    Two steps: (1) the ReAct agent gathers data and reasons to a textual answer,
    (2) a structured-output call formats that into the Team schema the UI needs.
    """
    agent = build_agent()
    # The system prompt asks the agent to look up a dozen+ players' stats plus
    # squads/pitch/form — each is a node visit, so give the loop generous headroom
    # (LangGraph counts every step; a thorough run can exceed the default 25).
    result = agent.invoke(
        {"messages": [("user", f"Pick my Dream11 XI for {match}.")]},
        config={"recursion_limit": 50},
    )
    messages = result["messages"]
    final_text = messages[-1].content

    if verbose:
        _print_trace(messages)

    # Step 2 — coerce the reasoning into the exact schema the UI expects.
    # BOTH arguments matter, and each fixes a different failure:
    #   method="json_schema" — ask Groq natively instead of via a function call.
    #     The default (function-calling) path makes the model reply in prose often
    #     enough to break a live run: the API then raises tool_use_failed.
    #   strict=True — turn on CONSTRAINED DECODING, so the model literally cannot
    #     emit off-schema text. Without it, schema adherence is only best-effort
    #     and a long nested payload like Team can come back json_validate_failed.
    # Strict mode is Groq-side and only exists on openai/gpt-oss-*; on other
    # models it is silently ignored. That is why this course pins gpt-oss-120b.
    # reasoning_effort="low" + max_tokens matter here, and for a reason worth
    # understanding. gpt-oss-120b is a REASONING model: it spends output tokens
    # thinking before it writes. Step 3 below hands it a genuine constraint puzzle
    # (11 players, <=100 credits, role quotas, <=7 per team), and on the default
    # settings it sometimes spends its whole budget reasoning and returns an EMPTY
    # completion — which then fails schema validation with json_validate_failed and
    # failed_generation: "". Constrained decoding guarantees that whatever the model
    # emits fits the schema; it cannot make the model emit anything at all.
    # Formatting is not the part that needs deep reasoning, so we cap it and give
    # the answer room. Measured on the repair prompt: 3 failures in 7 runs on the
    # defaults, 0 in 7 with these two arguments.
    structurer = _llm(temperature=0, reasoning_effort="low", max_tokens=4000) \
        .with_structured_output(Team, method="json_schema", strict=True)
    team = structurer.invoke(
        "Convert the following fantasy-cricket recommendation into the required "
        f"structured format for the match '{match}'. Keep the same 11 players, "
        "captain, vice-captain and reasons.\n\n" + str(final_text)
    )

    # Step 3 — enforce the HARD rules deterministically. LLMs slip on credit caps
    # and per-team limits, so we validate in code and feed violations back for a
    # bounded number of correction passes.
    issues, _ = validate_team(team)
    attempts = 0
    while issues and attempts < 2:
        attempts += 1
        if verbose:
            print(f"⚠️  Draft XI invalid ({'; '.join(issues)}) — correcting (pass {attempts})…")
        team = structurer.invoke(_fix_prompt(match, team, issues))
        issues, _ = validate_team(team)

    # Final backstop: if the credit cap is still breached, fix it deterministically
    # in code (LLMs can't reliably solve this knapsack-style constraint).
    if issues:
        team = repair_credits(team)
        issues, _ = validate_team(team)
        if verbose:
            print("🔧 Applied deterministic credit repair." if not issues
                  else f"⚠️  Remaining after repair: {'; '.join(issues)}")
    return team


def _fix_prompt(match: str, team: Team, issues: list) -> str:
    return (
        "This Dream11 XI is INVALID. Violations: " + "; ".join(issues) + ".\n"
        f"Rebuild the strongest LEGAL XI for '{match}' using ONLY players from this pool "
        "(name — team, role, credits):\n" + player_pool_text() + "\n\n"
        "HARD RULES (all must hold): exactly 11 players; 1-4 WK, 3-6 BAT, 1-4 AR, 3-6 BOWL; "
        "total credits <= 100; at most 7 players from one team; captain and vice-captain must "
        "both be in the XI and be different. Keep the best players you can while satisfying "
        "every rule.\n\nCurrent invalid team:\n" + str(team)
    )


def _print_trace(messages) -> None:
    """Print a readable think → tool → observe trace (what LangSmith shows visually)."""
    print("\n===== AGENT TRACE =====")
    for m in messages:
        role = m.__class__.__name__.replace("Message", "").upper()
        tool_calls = getattr(m, "tool_calls", None)
        if tool_calls:
            for tc in tool_calls:
                print(f"[{role}] → ACTION {tc['name']}({tc['args']})")
        elif role == "TOOL":
            content = str(m.content)
            print(f"[TOOL] OBSERVATION: {content[:200]}{'…' if len(content) > 200 else ''}")
        elif m.content:
            content = str(m.content)
            print(f"[{role}] {content[:300]}{'…' if len(content) > 300 else ''}")
    print("===== END TRACE =====\n")
