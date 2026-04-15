#!/usr/bin/env python3
"""
Regenerate all derived JSON for each event-type preset.

Requires data/complete.json. Run from anywhere:
  python3 scripts/rebuild_presets.py

Use --skip-geocode or NYPHIL_SKIP_GEOCODE=1 to avoid Nominatim (offline / CI).
"""
import argparse
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from build_aggregates import run_build_aggregates
from build_concerts_data import write_concerts_single_soloist, write_concerts_soloists
from build_conductors_index import write_conductors_index
from build_date_indices import write_date_indices
from build_debuts import write_debuts
from build_geography import write_locations
from filter_presets import PRESET_ORDER, filter_programs
from geocode_locations import collect_location_names, ensure_geocodes_for_names

DATA_DIR = os.path.join(SCRIPT_DIR, "..", "data")
COMPLETE_PATH = os.path.join(DATA_DIR, "complete.json")


def main():
    parser = argparse.ArgumentParser(description="Rebuild preset JSON under data/presets/")
    parser.add_argument(
        "--skip-geocode",
        action="store_true",
        help="Do not call Nominatim; use data/geocode_cache.json as-is",
    )
    args = parser.parse_args()

    if not os.path.isfile(COMPLETE_PATH):
        print("Missing", COMPLETE_PATH, file=sys.stderr)
        sys.exit(1)
    with open(COMPLETE_PATH, encoding="utf-8") as f:
        programs = json.load(f)["programs"]

    all_names = set()
    for preset in PRESET_ORDER:
        all_names |= collect_location_names(filter_programs(programs, preset))
    ensure_geocodes_for_names(all_names, skip_network=args.skip_geocode)

    for preset in PRESET_ORDER:
        filtered = filter_programs(programs, preset)
        out_dir = os.path.join(DATA_DIR, "presets", preset)
        os.makedirs(out_dir, exist_ok=True)
        date_dir = os.path.join(out_dir, "date-indices")
        print("=== preset", preset, "programs", len(filtered), "===")
        run_build_aggregates(filtered, out_dir)
        write_date_indices(filtered, date_dir)
        write_concerts_soloists(filtered, os.path.join(out_dir, "concerts-soloists.json"))
        write_concerts_single_soloist(
            filtered, os.path.join(out_dir, "concerts-single-soloist.json")
        )
        write_debuts(filtered, os.path.join(out_dir, "debuts.json"))
        write_conductors_index(filtered, os.path.join(out_dir, "conductors_index.json"))
        write_locations(filtered, os.path.join(out_dir, "locations.json"))


if __name__ == "__main__":
    main()
