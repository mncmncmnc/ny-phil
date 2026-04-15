"""
Fill data/geocode_cache.json for every Location string not already geocoded.

Uses OpenStreetMap Nominatim (https://nominatim.org/): one request per second,
identifying User-Agent required.

data/location_coordinates.json is optional manual overrides (takes precedence
over the cache in build_geography).

NYPHIL_SKIP_GEOCODE=1 or skip_network=True skips HTTP (uses existing cache only).
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "data")
CURATED_PATH = os.path.join(DATA_DIR, "location_coordinates.json")
CACHE_PATH = os.path.join(DATA_DIR, "geocode_cache.json")

USER_AGENT = (
    "ny-phil-site/1.0 (NY Philharmonic performance history visualization; "
    "open dataset project)"
)
REQUEST_INTERVAL_SEC = 1.1


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


def load_json(path, default):
    if not os.path.isfile(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_cache(cache):
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    tmp = CACHE_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)
    os.replace(tmp, CACHE_PATH)


def nominatim_geocode(query):
    params = urllib.parse.urlencode(
        {"q": query, "format": "json", "limit": "1"}
    )
    url = f"https://nominatim.openstreetmap.org/search?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = json.loads(resp.read().decode())
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError):
        return None
    if not data:
        return None
    try:
        return float(data[0]["lat"]), float(data[0]["lon"])
    except (KeyError, IndexError, TypeError, ValueError):
        return None


def collect_location_names(programs):
    names = set()
    for program in programs:
        for concert in program.get("concerts") or []:
            loc = (concert.get("Location") or "").strip() or "(unknown)"
            names.add(loc)
    return names


def ensure_geocodes_for_names(location_names, skip_network=False):
    curated = load_json(CURATED_PATH, {})
    cache = load_json(CACHE_PATH, {})

    skip_names = {"", "(unknown)"}

    need = []
    for name in sorted(location_names):
        if name in skip_names:
            continue
        if name in curated and _valid_coord_entry(curated[name]):
            continue
        if _valid_coord_entry(cache.get(name)):
            continue
        need.append(name)

    if not need:
        print("geocode: all locations covered by curated file + geocode_cache.json")
        return

    env_skip = os.environ.get("NYPHIL_SKIP_GEOCODE", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )
    if skip_network or env_skip:
        print(
            f"geocode: skipping {len(need)} Nominatim lookups "
            f"(use existing cache or run without --skip-geocode / NYPHIL_SKIP_GEOCODE)",
            file=sys.stderr,
        )
        return

    print(
        f"geocode: Nominatim lookup for {len(need)} locations "
        f"(~{int(len(need) * REQUEST_INTERVAL_SEC)} s)"
    )
    for i, name in enumerate(need):
        print(f"  [{i + 1}/{len(need)}] {name[:76]!r}")
        coords = nominatim_geocode(name)
        time.sleep(REQUEST_INTERVAL_SEC)
        if coords:
            cache[name] = {"lat": coords[0], "lng": coords[1]}
        else:
            cache[name] = {"failed": True}
        save_cache(cache)

    print("geocode: updated", CACHE_PATH)


def main():
    complete = os.path.join(DATA_DIR, "complete.json")
    if not os.path.isfile(complete):
        print("Missing", complete, file=sys.stderr)
        sys.exit(1)
    with open(complete, encoding="utf-8") as f:
        programs = json.load(f)["programs"]
    ensure_geocodes_for_names(collect_location_names(programs), skip_network=False)


if __name__ == "__main__":
    main()
