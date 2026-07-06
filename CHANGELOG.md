# Changelog

Two independent version axes: the **spec** (`spec/schema`, `spec/context`,
`spec/OVPF.md`) and the **reference Python implementation**
(`reference/python`, package `ovpf`). They version separately — see
`docs/ARCHITECTURE.md` and each package's own README for why.

## spec

### spec-v0.1.0 — 2026-07-07
Initial published draft: envelope schema, JSON-LD context, format sketch.

## ovpf (reference Python implementation)

### ovpf-python-v0.2.0 — 2026-07-07
- Add `sync.py`: local <-> cloud reconciliation against an OVPF provider
  (`ovpf --sync PASSPORT.ovpf.ndjson --provider <url>`), built on the
  existing merge/seal primitives. Supports ovp-provider-aws.

### ovpf-python-v0.1.0 — 2026-07-07
Initial extraction from the OpenDiag prototype: canonicalization,
hashing, UUIDv7, seal/verify/merge/reduce, CLI, QR generation.
