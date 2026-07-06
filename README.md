# Open Vehicle Passport (OVP)

This directory is the seed of something bigger than OpenDiag: an open,
implementation-neutral protocol for recording the lifetime history of a
vehicle.

OpenDiag is a BMW K-line diagnostics application. OVP is not that. OVP is
the idea that the *events* a vehicle accumulates over its life — oil
changes, diagnostic sessions, dyno runs, ECU tunes, ownership transfers —
belong to a shared, open format that any application can read and write.
OpenDiag is planned to become one producer and consumer of that format,
and its cloud offering one *provider* among many that could exist.

There is no code here yet, intentionally. These documents capture the
philosophy and architecture while it's fresh, before any schema gets
frozen prematurely.

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

## Two names, one project

- **OVP** — *Open Vehicle Passport*. The ecosystem: identities,
  discovery, trust, providers, governance.
- **OVPF** — *Open Vehicle Passport Format*. The technical
  specification: schemas, event formats, APIs, export/import.

OpenDiag will be the reference implementation of OVPF. It is not the
protocol, and it should not need to be for the protocol to matter.
