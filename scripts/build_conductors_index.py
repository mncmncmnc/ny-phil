"""Conductor -> chronological appearances with work metadata."""
import json
import os
import re
from collections import defaultdict

from build_aggregates import norm_space


def norm_conductor_name(s):
    """
    Canonical key for conductorName. Collapses stray leading/trailing semicolons
    and whitespace (source data sometimes has '; Last, First' duplicates).
    """
    s = norm_space(s)
    if not s:
        return ""
    s = re.sub(r"^[\s;]+", "", s)
    s = re.sub(r"[\s;]+$", "", s)
    return norm_space(s)


def conductor_tokens(conductor_name):
    """
    Split semicolon-separated shared credits into normalized person keys.
    Preserves input order and drops duplicates/empties.
    """
    raw = norm_space(conductor_name)
    if not raw:
        return []
    seen = set()
    out = []
    for part in raw.split(";"):
        name = norm_conductor_name(part)
        if not name or name in seen:
            continue
        seen.add(name)
        out.append(name)
    return out


def build_conductors_index(programs):
    by_conductor = defaultdict(list)
    for program in programs:
        pid = program["id"]
        for concert in sorted(program.get("concerts") or [], key=lambda c: c["Date"]):
            date = concert["Date"][:10]
            for work in program.get("works") or []:
                if work.get("interval"):
                    continue
                credits = conductor_tokens(work.get("conductorName"))
                if not credits:
                    continue
                comp = norm_space(work.get("composerName"))
                title = norm_space(work.get("workTitle"))
                shared = len(credits) > 1
                for cond in credits:
                    by_conductor[cond].append(
                        {
                            "date": date,
                            "composerName": comp,
                            "workTitle": title,
                            "programId": pid,
                            "sharedCredit": shared,
                        }
                    )
    # sort each list by date
    out = {
        c: sorted(rows, key=lambda r: (r["date"], r["programId"]))
        for c, rows in sorted(by_conductor.items())
    }
    return out


def write_conductors_index(programs, path):
    data = build_conductors_index(programs)
    with open(path, "w", encoding="utf-8") as w:
        json.dump(data, w, indent=2, ensure_ascii=False)
    print("wrote", path)
