#!/usr/bin/env python3
"""
Build data/printed_program_urls.json: numeric programID -> archives DAM URL.

Uses https://data.nyphil.org/api/dams/printed-program/{programID}.
Incremental: reuses existing map entries unless --force.
"""
import argparse
import concurrent.futures
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.request

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "data")
COMPLETE_PATH = os.path.join(DATA_DIR, "complete.json")
OUT_PATH = os.path.join(DATA_DIR, "printed_program_urls.json")

API = "https://data.nyphil.org/api/dams/printed-program/"
UA = "nyphil-views/1.0 (+https://github.com; printed program URL map)"

# python.org macOS installs often ship without a CA bundle; prefer system certs.
_CA_CANDIDATES = (
    os.environ.get("SSL_CERT_FILE"),
    "/etc/ssl/cert.pem",
    "/opt/homebrew/etc/openssl@3/cert.pem",
)


def _ssl_context():
    for path in _CA_CANDIDATES:
        if path and os.path.isfile(path):
            return ssl.create_default_context(cafile=path)
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


SSL_CONTEXT = _ssl_context()


def rewrite_dam_url(url):
    if not url:
        return None
    url = url.replace(
        "https://cortex.nyphil.org/asset-management/",
        "https://archives.nyphil.org/asset-management/",
    )
    if "?" in url:
        url = url.split("?", 1)[0]
    return url


def fetch_one(program_id):
    pid = str(program_id)
    req = urllib.request.Request(
        API + pid, headers={"User-Agent": UA, "Accept": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=45, context=SSL_CONTEXT) as resp:
            data = json.load(resp)
        return pid, rewrite_dam_url(data.get("parent_link"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return pid, None
        return pid, False  # retryable failure marker via False
    except Exception:
        return pid, False


def build_map(force=False, workers=12, retries=3):
    if not os.path.isfile(COMPLETE_PATH):
        print("Missing", COMPLETE_PATH, file=sys.stderr)
        return 1

    with open(COMPLETE_PATH, encoding="utf-8") as f:
        programs = json.load(f)["programs"]

    all_ids = []
    seen = set()
    for p in programs:
        pid = p.get("programID")
        if pid is None or pid == "":
            continue
        pid = str(pid)
        if pid in seen:
            continue
        seen.add(pid)
        all_ids.append(pid)

    existing = {}
    if os.path.isfile(OUT_PATH) and not force:
        with open(OUT_PATH, encoding="utf-8") as f:
            existing = json.load(f)
        if not isinstance(existing, dict):
            existing = {}

    out = {k: v for k, v in existing.items() if isinstance(v, str) and v}
    missing = [pid for pid in all_ids if pid not in out]
    print(
        "programIDs",
        len(all_ids),
        "cached",
        len(out),
        "to fetch",
        len(missing),
        flush=True,
    )

    failed = []
    t0 = time.time()
    done = 0

    def handle_batch(ids):
        nonlocal done
        batch_failed = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
            for pid, url in ex.map(fetch_one, ids):
                done += 1
                if url is False:
                    batch_failed.append(pid)
                elif url:
                    out[pid] = url
                if done % 250 == 0 or done == len(missing):
                    print(
                        f"  progress {done}/{len(missing)} "
                        f"ok={len(out)} elapsed={time.time() - t0:.0f}s",
                        flush=True,
                    )
        return batch_failed

    pending = missing
    for attempt in range(retries):
        if not pending:
            break
        if attempt:
            print(f"retry {attempt}: {len(pending)} ids", flush=True)
            time.sleep(1.5 * attempt)
            done = len(missing) - len(pending)
        pending = handle_batch(pending)
        failed = pending

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as w:
        json.dump(out, w, indent=0, sort_keys=True, ensure_ascii=False)
        w.write("\n")

    print(
        "wrote",
        OUT_PATH,
        "urls",
        len(out),
        "failed",
        len(failed),
        f"in {time.time() - t0:.1f}s",
        flush=True,
    )
    if failed:
        print("sample failures:", ", ".join(failed[:10]), file=sys.stderr)
        return 2
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build printed program URL map")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Refetch all IDs even if already cached",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=12,
        help="Concurrent HTTP workers (default 12)",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=3,
        help="Retries for transient failures (default 3)",
    )
    args = parser.parse_args(argv)
    raise SystemExit(build_map(force=args.force, workers=args.workers, retries=args.retries))


if __name__ == "__main__":
    main()
