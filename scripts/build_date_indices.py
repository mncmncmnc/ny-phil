"""Write date-indices/MM-DD.json for on-this-day."""
import json
import os


def write_date_indices(programs, date_indices_dir):
    os.makedirs(date_indices_dir, exist_ok=True)
    index = {}
    for p in programs:
        for c in p["concerts"]:
            date = c["Date"].split("T")[0]
            split = date.split("-")
            key = split[1] + "-" + split[2]
            if key not in index:
                index[key] = []
            index[key].append({"program": p, "year": split[0]})

    for date_key in index:
        d = date_key.split("-")
        path = os.path.join(date_indices_dir, f"{d[0]}-{d[1]}.json")
        with open(path, "w", encoding="utf-8") as w:
            json.dump(index[date_key], w, indent=4, ensure_ascii=False)
        print("wrote", path)
