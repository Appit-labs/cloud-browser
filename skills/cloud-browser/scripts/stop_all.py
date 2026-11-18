#!/usr/bin/env python3
"""List and stop hosted cloud browsers so orphaned sessions stop billing.

    stop_all.py [--dry-run] [--yes] [--keep ID ...] [--api URL]
    stop_all.py --from-file payload.json [--dry-run]
    stop_all.py self-test

Uses the REST API directly (X-Browser-Use-API-Key, no Bearer) because a crashed
agent session has no CLI provider session left to close.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

API = os.environ.get("CLOUD_BROWSER_API", "https://api.browser-use.com")


def key() -> str:
    k = os.environ.get("BROWSER_USE_API_KEY", "").strip()
    if not k:
        raise SystemExit("BROWSER_USE_API_KEY is not set in this process (restart from a login shell)")
    return k


def request(method: str, path: str, body: dict | None = None) -> tuple[int, str]:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{API}{path}", data=data, method=method)
    req.add_header("X-Browser-Use-API-Key", key())
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "replace")
    except urllib.error.URLError as exc:
        raise SystemExit(f"cannot reach {API}: {exc.reason}")


def ids_from(payload: str) -> list[dict]:
    """Accept the list endpoint's shape without assuming it: find objects with an id."""
    try:
        data = json.loads(payload)
    except ValueError:
        return []
    for candidate in (data, data.get("browsers") if isinstance(data, dict) else None,
                      data.get("items") if isinstance(data, dict) else None,
                      data.get("data") if isinstance(data, dict) else None):
        if isinstance(candidate, list):
            return [o for o in candidate if isinstance(o, dict) and (o.get("id") or o.get("browserId"))]
    return []


def ident(obj: dict) -> str:
    return obj.get("id") or obj.get("browserId") or "?"


def started(obj: dict) -> str:
    for k in ("startedAt", "createdAt", "created_at", "started_at"):
        if obj.get(k):
            return str(obj[k])[:19]
    return "?"


def main(argv: list[str]) -> int:
    args = argv[1:]
    if "self-test" in args:
        return self_test()
    dry = "--dry-run" in args
    confirmed = "--yes" in args
    keep: set[str] = set()
    for i, a in enumerate(args):
        if a == "--keep" and i + 1 < len(args):
            keep.add(args[i + 1])
    if "--api" in args:
        global API
        API = args[args.index("--api") + 1]
    if "--from-file" in args:
        payload = open(args[args.index("--from-file") + 1], encoding="utf-8").read()
        status = 200
    else:
        status, payload = request("GET", "/api/v4/browsers")
    if status >= 400:
        print(f"list failed: HTTP {status}: {payload[:300]}", file=sys.stderr)
        return 1
    targets = [o for o in ids_from(payload) if ident(o) not in keep]
    if not targets:
        print("no cloud browsers running (or none matched the response shape)")
        return 0
    print(f"{'id':38} {'state':10} started")
    for o in targets:
        print(f"{ident(o):38} {str(o.get('status', '?')):10} {started(o)}")
    if dry:
        print(f"\n{len(targets)} would be stopped (dry run)")
        return 0
    if not confirmed:
        print(f"\n{len(targets)} running. Re-run with --yes to stop them, or --dry-run to list only.",
              file=sys.stderr)
        return 2
    failures = 0
    for o in targets:
        code, body = request("PATCH", f"/api/v4/browsers/{ident(o)}", {"action": "stop"})
        ok = code < 400
        failures += 0 if ok else 1
        print(f"{'stopped' if ok else f'FAILED HTTP {code}'} {ident(o)}"
              + ("" if ok else f": {body[:160]}"))
    return 1 if failures else 0


def self_test() -> int:
    shapes = [
        ('[{"id":"b1","status":"active","startedAt":"2026-01-01T10:00:00Z"}]', ["b1"]),
        ('{"browsers":[{"browserId":"b2","createdAt":"x"}]}', ["b2"]),
        ('{"items":[{"id":"b3"},{"nope":1}]}', ["b3"]),
        ('{"data":[{"id":"b4"}]}', ["b4"]),
    ]
    for payload, want in shapes:
        got = [ident(o) for o in ids_from(payload)]
        assert got == want, (payload, got)
    assert ids_from("not json") == []
    assert ids_from('{"count":0}') == []
    print("self-test ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
