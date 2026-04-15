"""
Rebuild composer-years.json, works-by-composer.json, and
soloist-instruments-by-season-count.json from data/complete.json.

Run from repo root: python3 scripts/build_aggregates.py
Or from scripts/: python3 build_aggregates.py (paths below assume cwd is scripts/).
"""
import json
import os
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "data")
COMPLETE_PATH = os.path.join(DATA_DIR, "complete.json")

SOLOIST_EXCLUDE = {"", " ", "  ", "Audience", "No Soloist"}


def norm_space(s):
    if s is None:
        return ""
    if not isinstance(s, str):
        return ""
    return " ".join(s.split())


def build_composer_years(programs):
    # composer -> calendar year -> count of work performances (one per concert x work row)
    counts = defaultdict(lambda: defaultdict(int))
    for program in programs:
        for concert in program["concerts"]:
            year = int(concert["Date"].split("T")[0].split("-")[0])
            for work in program["works"]:
                if work.get("interval"):
                    continue
                composer = norm_space(work.get("composerName"))
                if not composer:
                    continue
                counts[composer][year] += 1
    # stringify years for JSON keys (matches existing site data)
    return {c: {str(y): counts[c][y] for y in sorted(counts[c])} for c in sorted(counts)}


def build_works_by_composer(programs):
    # preserve first-seen title order per composer (program list order)
    order = defaultdict(list)
    seen = defaultdict(set)
    for program in programs:
        for work in program["works"]:
            if work.get("interval"):
                continue
            composer = norm_space(work.get("composerName"))
            title = norm_space(work.get("workTitle"))
            if not composer or not title:
                continue
            if title not in seen[composer]:
                seen[composer].add(title)
                order[composer].append(title)
    return {c: order[c] for c in sorted(order)}


def build_soloist_instruments(programs):
    # lowercase instrument key -> calendar year -> soloist listing count
    counts = defaultdict(lambda: defaultdict(int))
    for program in programs:
        for concert in program["concerts"]:
            year = int(concert["Date"].split("T")[0].split("-")[0])
            for work in program["works"]:
                for soloist in work.get("soloists") or []:
                    try:
                        name = soloist.get("soloistName")
                        if name in SOLOIST_EXCLUDE:
                            continue
                        inst = norm_space(soloist.get("soloistInstrument"))
                        if not inst:
                            inst = "not specified"
                        counts[inst.lower()][year] += 1
                    except (TypeError, AttributeError):
                        continue
    return {
        inst: {str(y): counts[inst][y] for y in sorted(counts[inst])}
        for inst in sorted(counts)
    }


def run_build_aggregates(programs, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    composer_years = build_composer_years(programs)
    works_by_composer = build_works_by_composer(programs)
    soloist_instruments = build_soloist_instruments(programs)

    out = [
        ("composer-years.json", composer_years),
        ("works-by-composer.json", works_by_composer),
        ("soloist-instruments-by-season-count.json", soloist_instruments),
    ]
    for name, obj in out:
        path = os.path.join(output_dir, name)
        with open(path, "w", encoding="utf-8") as w:
            json.dump(obj, w, indent=4, ensure_ascii=False)
        print("wrote", path)


def main():
    import subprocess
    import sys

    sp = os.path.join(SCRIPT_DIR, "rebuild_presets.py")
    r = subprocess.run([sys.executable, sp], check=False)
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
