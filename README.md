# Open Vehicle Passport (OVP)

OVP is an open, implementation-neutral protocol for recording the lifetime
history of a vehicle: the *events* it accumulates over its life — oil
changes, diagnostic sessions, dyno runs, ECU tunes, ownership transfers —
as a shared, append-only format that any application can read and write.

No single company owns a vehicle's history. Any producer can write events,
any provider can host them, and any consumer can read them, as long as
they speak the format. This repo is that format's spec, its reference
Python implementation, and the philosophy behind it — the protocol layer
the rest of the ecosystem builds on:

- [OpenDiag](https://github.com/tooming/opendiag) — a BMW K-line
  diagnostics application, and the reference implementation of OVPF: the
  first producer/consumer built against this protocol.
- [ovp-provider-aws](https://github.com/tooming/ovp-provider-aws) — a
  serverless provider (Lambda, DynamoDB, API Gateway, CloudFront).
- [ovp-provider-cloudflare](https://github.com/tooming/ovp-provider-cloudflare) —
  a second, independent provider (Workers, KV), in a different language,
  proving the protocol isn't tied to one stack.

## Reading order

1. [`docs/VISION.md`](docs/VISION.md) — why this exists, what it's not,
   the business philosophy behind an open protocol.
2. [`docs/MANIFESTO.md`](docs/MANIFESTO.md) — the short, quotable
   principles.
3. [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — entities, layers,
   how OVP and OVPF relate.
4. [`docs/IDENTIFIERS.md`](docs/IDENTIFIERS.md) — vehicle IDs, passport
   addresses, QR/NFC philosophy.
5. [`docs/DISCOVERY.md`](docs/DISCOVERY.md) — how a client finds a
   vehicle's provider, and how providers delegate.
6. [`docs/EVENTS.md`](docs/EVENTS.md) — the event-sourcing model, facts
   vs. opinions, event envelope.
7. [`docs/TRUST.md`](docs/TRUST.md) — how trust is established without
   a central gatekeeper.
8. [`docs/ROADMAP.md`](docs/ROADMAP.md) — the order in which this gets
   built, starting from OpenDiag as the reference implementation.
9. [`spec/OVPF.md`](spec/OVPF.md) — the normative format spec: event
   envelope, canonicalization, hash-chaining, producer verification.
10. [`reference/python`](reference/python) and
    [`conformance/fixtures`](conformance/fixtures) — a working
    implementation and the shared test vectors any other one (JS, Rust,
    whatever) has to match.

## Two names, one project

- **OVP** — *Open Vehicle Passport*. The ecosystem: identities,
  discovery, trust, providers, governance.
- **OVPF** — *Open Vehicle Passport Format*. The technical
  specification: schemas, event formats, APIs, export/import.

OpenDiag is the reference implementation of OVPF — proof the protocol
works, not the protocol itself. Anyone can build another one against the
same spec.
