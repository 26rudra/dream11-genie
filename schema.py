"""Structured output schema for Dream11 Genie.

The agent gathers data with tools, reasons, and finally emits EXACTLY this
shape so the UI (and a human) gets a clean, defensible team — not a wall of prose.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class Pick(BaseModel):
    player: str = Field(description="Player's full name")
    team: str = Field(description="Team short code, e.g. CSK or MI")
    role: str = Field(description="One of: WK, BAT, AR, BOWL")
    reason: str = Field(description="One-line justification for this pick")


class Team(BaseModel):
    match: str = Field(description="The fixture, e.g. 'CSK vs MI'")
    captain: str = Field(description="Captain — scores 2x points")
    vice_captain: str = Field(description="Vice-captain — scores 1.5x points")
    players: list[Pick] = Field(description="Exactly 11 players, including the captain and vice-captain")
    strategy: str = Field(description="2-3 sentence summary of the overall strategy")
