"""Local <-> cloud sync for an .ovpf.ndjson passport.

The cloud copy is just another peer to reconcile with, not a special
protocol (see docs/ARCHITECTURE.md's storage-is-out-of-scope note): we
fetch its events, union by id with the local file (same primitive as
`ovpf --merge`), push whatever it's missing, and reseal locally.

recordedAt is producer-set and immutable (same as occurredAt) -- the
provider must never rewrite it, or a synced-back copy of an event would
look like a content conflict on the next sync. See ovp-provider-aws's
app.py for the matching provider-side half of this contract.

Stdlib only (urllib), matching ovpf_core's "no dependencies" stance.
"""
import json
import os
import re
import urllib.error
import urllib.request

import ovpf_core

_UUID_RE = re.compile(r"urn:ovpf:([0-9a-fA-F-]{36})")


def _token_path(passport_path):
    return passport_path + ".writetoken"


def _load_token(passport_path):
    p = _token_path(passport_path)
    if os.path.exists(p):
        return open(p, encoding="utf-8").read().strip()
    return None


def _save_token(passport_path, token):
    with open(_token_path(passport_path), "w", encoding="utf-8") as f:
        f.write(token)
    os.chmod(_token_path(passport_path), 0o600)


def _infer_passport_id(events):
    for ev in events:
        m = _UUID_RE.search(ev.get("vehicle", ""))
        if m:
            return m.group(1)
    return None


def _request(method, url, token=None, body=None):
    headers = {"content-type": "application/json"}
    if token:
        headers["authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")


def _content(ev):
    return {k: v for k, v in ev.items() if k not in ("hash", "prevHash")}


def sync(passport_path, provider, passport_id=None, token=None):
    """Reconcile the local file with `provider` (a base URL, e.g.
    https://api.example.com). Returns a summary dict; raises RuntimeError
    on unrecoverable HTTP errors."""
    local_events = ovpf_core.load(passport_path)
    passport_id = passport_id or _infer_passport_id(local_events)
    if not passport_id:
        raise RuntimeError("no passport id given, and none found in "
                            "any event's `vehicle` urn:ovpf:<uuid>")

    token = token or _load_token(passport_path)

    status, body = _request("GET", f"{provider}/v1/passports/{passport_id}/export", token)
    if status == 404:
        status, reg_body = _request("POST", f"{provider}/v1/passports", token,
                                     body={"id": passport_id})
        if status not in (201, 409):
            raise RuntimeError(f"could not register passport: {status} {reg_body}")
        if status == 201:
            token = json.loads(reg_body)["writeToken"]
            _save_token(passport_path, token)
        remote_events = []
    elif status == 200:
        remote_events = [json.loads(l) for l in body.splitlines() if l.strip()]
    else:
        raise RuntimeError(f"export failed: {status} {body}")

    local_ids = {e["id"] for e in local_events}
    remote_ids = {e["id"] for e in remote_events}
    to_push = [e for e in local_events if e["id"] not in remote_ids]
    to_pull = [e for e in remote_events if e["id"] not in local_ids]

    pushed, push_errors = [], []
    if to_push and not token:
        push_errors.append("no write token available -- pulled read-only, "
                            f"{len(to_push)} local event(s) NOT pushed")
    elif to_push:
        for ev in to_push:
            status, resp_body = _request(
                "POST", f"{provider}/v1/passports/{passport_id}/events",
                token, body=_content(ev))
            if status != 201:
                push_errors.append(f"{ev['id']}: {status} {resp_body}")
                continue
            pushed.append(json.loads(resp_body))  # server's canonical copy

    pushed_by_id = {e["id"]: e for e in pushed}
    merged = [pushed_by_id.get(e["id"], e) for e in local_events] + to_pull
    merged.sort(key=lambda e: (e.get("occurredAt", ""), e.get("id", "")))
    ovpf_core.seal(merged)

    with open(passport_path, "w", encoding="utf-8") as f:
        for ev in merged:
            f.write(json.dumps(ev, ensure_ascii=False) + "\n")

    return {
        "passport_id": passport_id,
        "pushed": len(pushed),
        "pulled": len(to_pull),
        "errors": push_errors,
        "total_events": len(merged),
    }
