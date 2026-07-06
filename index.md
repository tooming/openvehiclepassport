---
title: Open Vehicle Passport
---

# Open Vehicle Passport (OVP)

An open, implementation-neutral protocol for recording the lifetime
history of a vehicle.

OVP is the idea that the *events* a vehicle accumulates over its life —
oil changes, diagnostic sessions, dyno runs, ECU tunes, ownership
transfers — belong to a shared, open format that any application can
read and write. No single company or product owns the format; any
producer can write events, any provider can host a passport, any
application can read one.

## Reading order

1. [Vision](docs/VISION.html) — why this exists, what it's not, the
   business philosophy behind an open protocol.
2. [Manifesto](docs/MANIFESTO.html) — the short, quotable principles.
3. [Architecture](docs/ARCHITECTURE.html) — entities, layers, how OVP
   and OVPF relate.
4. [Identifiers](docs/IDENTIFIERS.html) — vehicle IDs, passport
   addresses, QR/NFC philosophy.
5. [Discovery](docs/DISCOVERY.html) — how a client finds a vehicle's
   provider, and how providers delegate.
6. [Events](docs/EVENTS.html) — the event-sourcing model, facts vs.
   opinions, event envelope.
7. [Trust](docs/TRUST.html) — how trust is established without a
   central gatekeeper.
8. [Roadmap](docs/ROADMAP.html) — the order in which this gets built.

## Two names, one project

- **OVP** — *Open Vehicle Passport*. The ecosystem: identities,
  discovery, trust, providers, governance.
- **OVPF** — *Open Vehicle Passport Format*. The technical
  specification: schemas, event formats, APIs, export/import.

[View the source on GitHub](https://github.com/tooming/openvehiclepassport)
