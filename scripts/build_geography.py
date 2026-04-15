"""Aggregate concert counts by Location; attach lat/lng from cache + curated overrides."""
import json
import os
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "data")
CURATED_PATH = os.path.join(DATA_DIR, "location_coordinates.json")
CACHE_PATH = os.path.join(DATA_DIR, "geocode_cache.json")


def _valid_coord_entry(v):
    if not isinstance(v, dict):
        return False
    if v.get("failed"):
        return False
    try:
        float(v["lat"])
        float(v["lng"])
        return True
    except (KeyError, TypeError, ValueError):
        return False


def load_cache_raw(cache_path=CACHE_PATH):
    if not os.path.isfile(cache_path):
        return {}
    with open(cache_path, encoding="utf-8") as f:
        return json.load(f)


def merged_coordinates(curated_path=CURATED_PATH, cache_path=CACHE_PATH):
    """Cache first, then curated overwrites (manual corrections win)."""
    merged = {}
    cache = load_cache_raw(cache_path)
    for k, v in cache.items():
        if _valid_coord_entry(v):
            merged[k] = {"lat": float(v["lat"]), "lng": float(v["lng"])}
    curated = {}
    if os.path.isfile(curated_path):
        with open(curated_path, encoding="utf-8") as f:
            curated = json.load(f)
    for k, v in curated.items():
        if _valid_coord_entry(v):
            merged[k] = {"lat": float(v["lat"]), "lng": float(v["lng"])}
    return merged


def geocode_failed_names(cache_path=CACHE_PATH):
    cache = load_cache_raw(cache_path)
    return {k for k, v in cache.items() if isinstance(v, dict) and v.get("failed")}


def build_locations(programs, coords_by_location, failed_names=None):
    by_loc = defaultdict(lambda: {"count": 0, "venues": defaultdict(int)})
    for program in programs:
        for concert in program.get("concerts") or []:
            loc = (concert.get("Location") or "").strip() or "(unknown)"
            venue = (concert.get("Venue") or "").strip() or "(unknown)"
            by_loc[loc]["count"] += 1
            by_loc[loc]["venues"][venue] += 1

    out = {}
    for loc, info in sorted(by_loc.items(), key=lambda x: -x[1]["count"]):
        venues = dict(sorted(info["venues"].items(), key=lambda x: -x[1])[:15])
        entry = {"count": info["count"], "venues": venues}
        if loc in coords_by_location:
            entry["lat"] = coords_by_location[loc]["lat"]
            entry["lng"] = coords_by_location[loc]["lng"]
        elif failed_names and loc in failed_names:
            entry["geocode_failed"] = True
        out[loc] = entry
    return out


def write_locations(programs, path, curated_path=CURATED_PATH, cache_path=CACHE_PATH):
    coords = merged_coordinates(curated_path, cache_path)
    failed = geocode_failed_names(cache_path)
    data = build_locations(programs, coords, failed_names=failed)
    with open(path, "w", encoding="utf-8") as w:
        json.dump(data, w, indent=2, ensure_ascii=False)
    with_coords = sum(1 for v in data.values() if "lat" in v)
    print("wrote", path, f"({with_coords}/{len(data)} locations with coordinates)")

