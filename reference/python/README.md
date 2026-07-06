# ovpf (reference Python implementation)

The one canonical implementation of the OVPF wire format: canonicalization,
event hashing, monotonic UUIDv7 ids, envelope construction, lock-guarded
local append, and the fold (seal / verify / merge / reduce).

- `ovpf_core.py` — the implementation.
- `ovpf.py` — thin CLI over `ovpf_core` (`ovpf` console script once installed).
- `qr.py` — generates the QR "physical anchor" for a passport (optional
  `segno` dependency, install with `pip install .[qr]`).

```
pip install -e .
ovpf PASSPORT.ovpf.ndjson
```

This package versions independently of the OVPF spec itself (see
`../schema/v0.1` and `../context/v0.1`). It documents which `specVersion`
values it supports in its own changelog, not the other way around.
