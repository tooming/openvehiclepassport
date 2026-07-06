#!/usr/bin/env python3
"""OVPF reference CLI — replay / verify / seal / merge a passport.

Thin CLI over `ovpf_core` (the one canonical implementation). Replaying a
passport into current state *is* the definition of "current state".

Usage:
  python3 ovpf.py PASSPORT.ovpf.ndjson          # replay -> state + chain check
  python3 ovpf.py --json PASSPORT.ovpf.ndjson   # derived state as JSON
  python3 ovpf.py --seal PASSPORT.ovpf.ndjson   # (re)compute the hash-chain in place
  python3 ovpf.py --merge A.ndjson B.ndjson     # reconcile two copies -> merged, sealed
  python3 ovpf.py --sync PASSPORT.ovpf.ndjson --provider https://api.example.com
                                                 # push/pull against a cloud provider
"""
import json
import sys

import ovpf_core
import sync as _sync

# re-export for tests / callers that import from ovpf
canonicalize = ovpf_core.canonicalize
event_hash = ovpf_core.event_hash
load = ovpf_core.load
seal = ovpf_core.seal
verify_chain = ovpf_core.verify_chain
merge = ovpf_core.merge
reduce = ovpf_core.reduce


def _unit(code):
    return {"KMT": "km", "SMI": "mi"}.get(code, code)


def _format(s):
    v, out = s["vehicle"], []
    desc = " ".join(str(v[k]) for k in ("modelYear", "make", "model") if v.get(k))
    if v.get("engine"):
        desc = (desc + f" · {v['engine']}").strip(" ·")
    out.append(f"Passport : {s['passport']}")
    out.append(f"Vehicle  : {desc or '(unknown)'}"
               + (f"   VIN {v['vin']}" if v.get("vin") else "  (no VIN yet)"))
    out.append(f"Owner    : {s['owner'] or '(anonymous / not set)'}")
    m = s["mileage"]
    out.append(f"Mileage  : {str(m['value']) + ' ' + _unit(m['unit']) if m else '(unknown)'}")
    of = s["open_faults"]
    out.append(f"Open faults ({len(of)}):{' none' if not of else ''}")
    for f in of:
        out.append(f"   - {f['module']} {f['code']} — {f['text']} (since {(f['since'] or '')[:10]})")
    out.append(f"Service history ({len(s['service_history'])}):")
    for h in s["service_history"]:
        out.append(f"   - {h['date']} {h['type']}: {h['total']} {h['currency'] or ''} @ {h['odometer']} km")
    if s["coding_changes"]:
        out.append(f"Coding changes ({len(s['coding_changes'])}):")
        for c in s["coding_changes"]:
            out.append(f"   - {c['date']} {c['module']} {c['preset'] or ''} ({c['before']} -> {c['after']})")
    if s["ai_insights"]:
        out.append(f"AI insights ({len(s['ai_insights'])}):")
        for a in s["ai_insights"]:
            out.append(f"   - (conf {a['confidence']}) {a['insight']}")
    out.append(f"Events   : {s['event_count']} total, "
               f"{s['corrections_applied']} correction(s) applied")
    return "\n".join(out)


def _extract_options(argv, names):
    """Pull `--name value` pairs out of argv; return (values, remaining)."""
    values, remaining, i = {}, [], 0
    while i < len(argv):
        if argv[i] in names and i + 1 < len(argv):
            values[argv[i][2:]] = argv[i + 1]
            i += 2
        else:
            remaining.append(argv[i])
            i += 1
    return values, remaining


def main(argv):
    options, argv = _extract_options(argv, {"--provider", "--id", "--token"})
    flags = {a for a in argv if a.startswith("--")}
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        raise SystemExit(__doc__)

    if "--sync" in flags:
        if "provider" not in options:
            raise SystemExit("--sync requires --provider <url>")
        result = _sync.sync(args[0], options["provider"].rstrip("/"),
                             passport_id=options.get("id"), token=options.get("token"))
        print(f"passport {result['passport_id']}")
        print(f"pushed {result['pushed']}, pulled {result['pulled']}, "
              f"total {result['total_events']} event(s)")
        for err in result["errors"]:
            print(f"  ! {err}", file=sys.stderr)
        return

    if "--merge" in flags:
        merged, conflicts = merge(*[load(p) for p in args])
        seal(merged)
        for ev in merged:
            print(json.dumps(ev, ensure_ascii=False))
        if conflicts:
            print(f"# WARNING: {len(conflicts)} id conflict(s): {conflicts}",
                  file=sys.stderr)
        return

    path = args[0]
    events = load(path)

    if "--seal" in flags:
        seal(events)
        with open(path, "w", encoding="utf-8") as f:
            for ev in events:
                f.write(json.dumps(ev, ensure_ascii=False) + "\n")
        print(f"sealed {len(events)} events -> {path}")
        return

    state = reduce(events)
    if "--json" in flags:
        print(json.dumps(state, indent=2, ensure_ascii=False))
        return

    print("=== derived state (replayed) ===")
    print(_format(state))
    print("\n=== hash-chain ===")
    problems = verify_chain(events)
    print("OK — chain intact, no tampering detected" if not problems
          else "\n".join("  x " + p for p in problems))


def main_cli():
    """Console-script entry point (`ovpf` command) — reads sys.argv."""
    main(sys.argv[1:])


if __name__ == "__main__":
    main_cli()
