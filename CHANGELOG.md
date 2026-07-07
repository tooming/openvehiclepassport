# Changelog

Two independent version axes: the **spec** (`spec/schema`, `spec/context`,
`spec/OVPF.md`) and the **reference Python implementation**
(`reference/python`, package `ovpf`). They version separately — see
`docs/ARCHITECTURE.md` and each package's own README for why.

## spec

### spec-v0.1.1 — 2026-07-07
- Document the canonical number-formatting rule explicitly
  (`spec/OVPF.md` §7): numbers use ECMAScript `Number::toString`, so a
  whole-number float has no `.0`. Found while porting to a second
  language (JS/Cloudflare) -- Python's default JSON float formatting
  disagreed with JS's, which would have silently broken cross-provider
  hash verification the first time any event had a "clean" numeric
  field (a price, a whole-number reading). Added
  `conformance/fixtures/canonicalization.json` as the shared test
  vectors for this.

### spec-v0.1.0 — 2026-07-07
Initial published draft: envelope schema, JSON-LD context, format sketch.

## ovpf (reference Python implementation)

### ovpf-python-v0.4.0 — 2026-07-07
- POC MODE: `sync.py` no longer sends or expects a write-capability
  token -- both reference providers (ovp-provider-aws,
  ovp-provider-cloudflare) dropped write access control entirely for
  easier POCing, not just stopped enforcing it. `ovpf --sync` no
  longer accepts `--token`, and no `.writetoken` sidecar file is
  written. This is a temporary simplification, not the intended
  posture -- see the provider READMEs' Auth sections.

### ovpf-python-v0.3.0 — 2026-07-07
- Fix `canonicalize()`: custom recursive serializer replacing
  `json.dumps`, matching ECMAScript number formatting (see spec
  v0.1.1). Re-sealed `examples/e39-passport.ovpf.ndjson` and the
  matching conformance fixture, which both contained whole-number
  floats hashed under the old (incorrect) formatting.

### ovpf-python-v0.2.0 — 2026-07-07
- Add `sync.py`: local <-> cloud reconciliation against an OVPF provider
  (`ovpf --sync PASSPORT.ovpf.ndjson --provider <url>`), built on the
  existing merge/seal primitives. Supports ovp-provider-aws.

### ovpf-python-v0.1.0 — 2026-07-07
Initial extraction from the OpenDiag prototype: canonicalization,
hashing, UUIDv7, seal/verify/merge/reduce, CLI, QR generation.
