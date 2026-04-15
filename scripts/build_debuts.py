"""First appearance in dataset for composer, work, soloist."""
import json
import os

from build_aggregates import SOLOIST_EXCLUDE, norm_space


def build_debuts(programs):
    events = []
    for program in programs:
        for concert in sorted(program.get("concerts") or [], key=lambda c: c["Date"]):
            date = concert["Date"][:10]
            pid = program["id"]
            for work in program.get("works") or []:
                if work.get("interval"):
                    continue
                events.append((concert["Date"], date, pid, work))
    events.sort(key=lambda x: x[0])

    seen_composer = set()
    seen_work = set()
    seen_soloist = set()
    debuts_composers = []
    debuts_works = []
    debuts_soloists = []

    for _sort_date, date, pid, work in events:
        comp = norm_space(work.get("composerName"))
        title = norm_space(work.get("workTitle"))
        if comp and comp not in seen_composer:
            seen_composer.add(comp)
            debuts_composers.append(
                {"name": comp, "firstDate": date, "programId": pid}
            )
        if comp and title:
            wkey = comp + "\t" + title
            if wkey not in seen_work:
                seen_work.add(wkey)
                debuts_works.append(
                    {
                        "composer": comp,
                        "workTitle": title,
                        "firstDate": date,
                        "programId": pid,
                    }
                )
        for soloist in work.get("soloists") or []:
            try:
                name = soloist.get("soloistName")
                if name in SOLOIST_EXCLUDE or not name:
                    continue
                if name not in seen_soloist:
                    seen_soloist.add(name)
                    debuts_soloists.append(
                        {"name": name, "firstDate": date, "programId": pid}
                    )
            except (TypeError, AttributeError):
                continue

    return {
        "composers": debuts_composers,
        "works": debuts_works,
        "soloists": debuts_soloists,
    }


def write_debuts(programs, path):
    data = build_debuts(programs)
    with open(path, "w", encoding="utf-8") as w:
        json.dump(data, w, indent=2, ensure_ascii=False)
    print("wrote", path)
