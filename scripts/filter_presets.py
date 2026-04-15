"""
Named presets filter concert rows by eventType before aggregations.

Each preset is a function (concert: dict) -> bool.
Programs with no concerts left after filtering are dropped.
"""
from copy import deepcopy

PRESET_ALL = "all"
PRESET_SUBSCRIPTION_SEASON = "subscription_season"

PRESET_ORDER = (PRESET_ALL, PRESET_SUBSCRIPTION_SEASON)

# Subscription-line concerts in the dataset (excludes tours, parks, education, etc.)
_SUBSCRIPTION_EVENT_TYPES = frozenset(
    {"Subscription Season", "Saturday Matinee"}
)


def _subscription_season_only(concert):
    return concert.get("eventType") in _SUBSCRIPTION_EVENT_TYPES


PRESET_PREDICATES = {
    PRESET_SUBSCRIPTION_SEASON: _subscription_season_only,
}


def filter_programs(programs, preset_key):
    """Return a new program list with concerts filtered; drop empty programs."""
    if preset_key not in PRESET_ORDER:
        preset_key = PRESET_ALL
    if preset_key == PRESET_ALL:
        return programs
    pred = PRESET_PREDICATES[preset_key]
    out = []
    for p in programs:
        concerts = [c for c in p.get("concerts") or [] if pred(c)]
        if not concerts:
            continue
        new_p = deepcopy(p)
        new_p["concerts"] = concerts
        out.append(new_p)
    return out
