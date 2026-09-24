"""
NFL Injury Agent
----------------
Fetches the current NFL injury report from ESPN's public data feed,
compares it to the last saved snapshot, and records any status changes.

It does the same job as the "Compare & log changes" button in your
original tracker, but automatically, with no copy/paste.

Files it reads and writes (all in the data/ folder):
  snapshot.json  - every player's latest known status
  log.json       - list of status changes, newest first
  meta.json      - when the agent last ran and what it found

Uses only Python's built-in libraries, so there is nothing to install.
"""

import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ESPN_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/injuries"

DATA_DIR = Path(__file__).parent / "data"
SNAPSHOT_FILE = DATA_DIR / "snapshot.json"
LOG_FILE = DATA_DIR / "log.json"
META_FILE = DATA_DIR / "meta.json"

MAX_LOG_ENTRIES = 500

# If ESPN suddenly returns far fewer players than we had before, something
# is probably wrong with the feed. We stop rather than mark everyone "Cleared".
MIN_PLAYERS_SAFETY = 20


# ---------- helpers ----------

def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def normalize_status(raw):
    """Map ESPN's wording onto the same statuses your tracker uses."""
    s = (raw or "").strip().lower()
    if not s:
        return None
    if s in ("ir", "injured reserve") or "reserve" in s:
        return "Injured Reserve"
    if "physically unable" in s or s == "pup":
        return "PUP"
    if "suspen" in s:
        return "Suspended"
    if "day-to-day" in s or "day to day" in s:
        return "Day-To-Day"
    if "doubtful" in s:
        return "Doubtful"
    if "questionable" in s:
        return "Questionable"
    if "out" in s:
        return "Out"
    return raw.strip().title()


# ---------- step 1: fetch ----------

def fetch_espn():
    req = urllib.request.Request(
        ESPN_URL,
        headers={
            "User-Agent": "Mozilla/5.0 (personal injury tracker)",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def parse_espn(data):
    """Turn ESPN's JSON into {player_name: {team, status, comment}}."""
    parsed = {}
    for team_group in data.get("injuries", []) or []:
        team = team_group.get("displayName") or "Unspecified"
        for item in team_group.get("injuries", []) or []:
            athlete = item.get("athlete") or {}
            name = (athlete.get("displayName") or "").strip()
            status = normalize_status(item.get("status"))
            if not name or not status:
                continue

            position = ((athlete.get("position") or {}).get("abbreviation") or "").strip()
            details = item.get("details") or {}
            injury = (details.get("type") or "").strip()
            comment = " ".join(part for part in (position, injury) if part)

            parsed[name] = {"team": team, "status": status, "comment": comment}
    return parsed


# ---------- step 2: compare (same rules as your original tracker) ----------

def diff_and_log(snapshot, new_parsed, now_iso):
    changes = []
    first_import = len(snapshot) == 0

    # new players and status changes
    for player, nxt in new_parsed.items():
        prev = snapshot.get(player)
        if prev is None:
            if not first_import:
                changes.append({"ts": now_iso, "player": player, "team": nxt["team"],
                                "from": "Available", "to": nxt["status"]})
        elif prev.get("status") != nxt["status"]:
            changes.append({"ts": now_iso, "player": player, "team": nxt["team"],
                            "from": prev.get("status"), "to": nxt["status"]})
        snapshot[player] = {**nxt, "updatedAt": now_iso}

    # players who dropped off the report -> Cleared
    for player, prev in list(snapshot.items()):
        if player not in new_parsed and prev.get("status") != "Cleared":
            changes.append({"ts": now_iso, "player": player, "team": prev.get("team"),
                            "from": prev.get("status"), "to": "Cleared"})
            snapshot[player] = {**prev, "status": "Cleared", "updatedAt": now_iso}

    return changes, first_import


# ---------- main ----------

def main():
    now_iso = datetime.now(timezone.utc).isoformat(timespec="seconds")
    print(f"Running injury agent at {now_iso}")

    try:
        raw = fetch_espn()
    except Exception as e:
        print(f"ERROR: could not reach ESPN: {e}")
        print("Nothing was changed. The agent will try again on its next run.")
        sys.exit(1)

    new_parsed = parse_espn(raw)
    print(f"Found {len(new_parsed)} players on ESPN's injury report.")

    snapshot = load_json(SNAPSHOT_FILE, {})
    log = load_json(LOG_FILE, [])

    active_before = sum(1 for p in snapshot.values() if p.get("status") != "Cleared")
    if len(new_parsed) < MIN_PLAYERS_SAFETY and active_before >= MIN_PLAYERS_SAFETY:
        print(f"ERROR: only {len(new_parsed)} players found, but {active_before} were listed last time.")
        print("ESPN's feed may have changed or be temporarily broken. Nothing was changed.")
        sys.exit(1)
    if len(new_parsed) == 0:
        print("ERROR: no players found in ESPN's response. Nothing was changed.")
        sys.exit(1)

    changes, first_import = diff_and_log(snapshot, new_parsed, now_iso)
    log = (changes + log)[:MAX_LOG_ENTRIES]

    save_json(SNAPSHOT_FILE, snapshot)
    save_json(LOG_FILE, log)
    save_json(META_FILE, {
        "lastChecked": now_iso,
        "playerCount": len(new_parsed),
        "lastRunChanges": len(changes),
        "firstRun": first_import,
    })

    if first_import:
        print(f"Baseline saved: {len(new_parsed)} players. Future runs will log changes.")
    else:
        print(f"{len(changes)} status change(s) logged:")
        for c in changes:
            print(f"  {c['player']} ({c['team']}): {c['from']} -> {c['to']}")


if __name__ == "__main__":
    main()
