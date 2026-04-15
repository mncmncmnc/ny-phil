"""concerts-soloists.json and concerts-single-soloist.json from program list."""
import json
import os

EXCLUDE = ["", " ", "  ", "Audience", "No Soloist"]
EXCLUDE_SINGLE = ["Audience", "No Soloist"]


def _concert_date_range(program):
    concerts = program.get("concerts") or []
    if not concerts:
        return None
    dates = sorted(c["Date"] for c in concerts)
    return [dates[0], dates[-1]]


def build_concerts_soloists(programs):
    found = {}
    for program in programs:
        rng = _concert_date_range(program)
        if not rng:
            continue
        for work in program["works"]:
            for soloist in work.get("soloists") or []:
                try:
                    if soloist.get("soloistName") not in EXCLUDE:
                        name = soloist["soloistName"]
                        instrument = soloist.get("soloistInstrument") or ""
                        if instrument.strip() == "":
                            instrument = "not specified"
                        if name not in found:
                            found[name] = {
                                "programs": {},
                                "range": {},
                                "instrument": [],
                            }
                        if instrument not in found[name]["instrument"]:
                            found[name]["instrument"].append(instrument)
                        found[name]["programs"][program["id"]] = {"range": rng}
                except (TypeError, KeyError, AttributeError):
                    continue

    for name in found:
        date_range = {"min": 9999, "max": 0}
        for pid in found[name]["programs"]:
            d1 = int(found[name]["programs"][pid]["range"][0].split("-")[0])
            d2 = int(found[name]["programs"][pid]["range"][1].split("-")[0])
            date_range["min"] = min(date_range["min"], d1)
            date_range["max"] = max(date_range["max"], d2)
        found[name]["range"] = date_range
        found[name]["instrument"].sort()
        found[name]["num_programs"] = len(found[name]["programs"])
    return found


def build_concerts_single_soloist(programs):
    found = {}
    for program in programs:
        soloists = []
        instrument = ""
        for work in program["works"]:
            for soloist in work.get("soloists") or []:
                try:
                    if soloist.get("soloistName") not in EXCLUDE_SINGLE:
                        sn = soloist["soloistName"]
                        if sn not in soloists:
                            soloists.append(sn)
                            instrument = soloist.get("soloistInstrument") or ""
                except (TypeError, AttributeError):
                    continue
        rng = _concert_date_range(program)
        if len(soloists) == 1 and rng:
            s0 = soloists[0]
            if s0 not in found:
                found[s0] = {"programs": [], "instrument": []}
            if instrument not in found[s0]["instrument"]:
                found[s0]["instrument"].append(instrument)
            found[s0]["programs"].append(
                {"id": program["id"], "range": rng}
            )
    return found


def write_concerts_soloists(programs, path):
    data = build_concerts_soloists(programs)
    with open(path, "w", encoding="utf-8") as w:
        json.dump(data, w, ensure_ascii=False)
    print("wrote", path)


def write_concerts_single_soloist(programs, path):
    data = build_concerts_single_soloist(programs)
    with open(path, "w", encoding="utf-8") as w:
        json.dump(data, w, ensure_ascii=False)
    print("wrote", path)
