Experimental views of the New York Philharmonic [Performance History](https://github.com/nyphilarchive/PerformanceHistory) open dataset (CC0). Metadata is not static; refresh periodically.

## Local server

From the project root:

`python3 -m http.server 5915`

Then open `http://localhost:5915/`.

## Refreshing the dataset

1. Download the current canonical JSON and save it as `data/complete.json` (same shape as `Programs/json/complete.json` in the upstream repo). Example:

   `curl -sL -o data/complete.json 'https://raw.githubusercontent.com/nyphilarchive/PerformanceHistory/main/Programs/json/complete.json'`

2. Regenerate **all** derived JSON for every **preset** (see below):

   `python3 scripts/rebuild_presets.py`

   This reads `data/complete.json` and writes under `data/presets/<preset>/`, including aggregates, date indices, soloists, debuts, conductors index, and geography counts.

`data/complete.json` is gitignored because of its size. Commit files under `data/presets/` and shared files such as `data/location_coordinates.json` as needed.

### Event-type presets

Pages use the query string `?preset=` to choose which folder under `data/presets/` to load (default: `all`).

| Preset | Meaning |
|--------|---------|
| `all` | No filtering; all concerts on each program |
| `subscription_season` | Concerts whose `eventType` is `Subscription Season` or `Saturday Matinee` |

Presets are defined in `scripts/filter_presets.py`. Add a new preset there, then rerun `rebuild_presets.py`, and add a matching `<option>` plus `ALLOWED` entry in `client/filters.js`.

### Geography coordinates

`data/location_coordinates.json` maps `Location` strings from the dataset to `lat` / `lng` for the map. Locations not listed there still appear in `locations.json` but are omitted from the map until coordinates are added.

The map uses [OpenStreetMap](https://www.openstreetmap.org/copyright) tiles.

### Other scripts

- `python3 scripts/build_aggregates.py` — runs the full `rebuild_presets.py` pipeline (same as above).
- `python3 scripts/wiki-articles.py` — reads `data/presets/all/works-by-composer.json`.

## Attribution

The Philharmonic requests [attribution and awareness of CC0](https://github.com/nyphilarchive/PerformanceHistory#usage-guidelines) when practical.
