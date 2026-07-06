# Conformance fixtures

Language-agnostic test vectors for any OVPF implementation, not just the
Python reference. Each fixture pair:

- `fixtures/<name>.input.ndjson` — a sealed (hash-chained) event log.
- `fixtures/<name>.expected-state.json` — the derived state that
  `reduce(events)` must produce (see `docs/EVENTS.md` for the fold rules).

A conformant implementation must, given the input, produce the
expected-state JSON (semantic equality, not byte equality) and must
report the hash chain as intact. Generated from the Python reference via:

```
python3 reference/python/ovpf.py --json fixtures/<name>.input.ndjson \
  > fixtures/<name>.expected-state.json
```
