# SPDX-License-Identifier: Apache-2.0
"""ADR-0139: the hour of the day from the game time the probe already reads (nothing new is read).

The unit was checked against the game's own clock (ADR-0139, point 1, lab 2026-11-22): the probe's
game time counts engine ticks, 15 per game second, so one hour is 4500 and one day 108000 (game time
497541 = 14:33, the clock said 14). Night (D1) is dusk and night, from 21:00 to 05:59.
"""
from __future__ import annotations

UNITS_PER_HOUR = 4500
HOURS_PER_DAY = 24
NIGHT_FROM, NIGHT_UNTIL = 21, 6          # [21:00, 06:00)


def hour_of(game_time: int | None) -> int | None:
    if isinstance(game_time, bool) or not isinstance(game_time, int) or game_time < 0:
        return None
    return (game_time // UNITS_PER_HOUR) % HOURS_PER_DAY


def is_night(game_time: int | None) -> bool:
    """False when the time is unknown: what needs the night never happens without it."""
    hour = hour_of(game_time)
    return hour is not None and (hour >= NIGHT_FROM or hour < NIGHT_UNTIL)
