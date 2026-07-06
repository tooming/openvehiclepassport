---
title: Architecture
---

# Architecture

## Layering: OVP vs. OVPF

- **OVP** (Open Vehicle Passport) is the ecosystem: identities,
  discovery, trust, providers, governance. It's the set of agreements
  that make interoperability possible.
- **OVPF** (Open Vehicle Passport Format) is the technical specification
  living inside that ecosystem: JSON schemas, event formats, APIs, and
  export/import rules.

OpenDiag is the reference implementation of OVPF — one client, one
provider (OpenDiag Cloud), built to prove the spec works, not to be the
only thing that can speak it.

## Core entities

**Vehicle** — the permanent subject. Identified by a globally unique ID
independent of any provider (see `IDENTIFIERS.md`). Has no owner in the
data model; it has a history and a current set of access grants.

**Passport** — the vehicle's timeline as hosted by a specific provider.
A vehicle has exactly one *current* passport home at a time, but that
home is mutable and portable (see `DISCOVERY.md`).

**Event** — an immutable fact appended to a vehicle's timeline (see
`EVENTS.md`). The only way the timeline grows.

**Identity** — any actor capable of producing events or holding
permissions: a person, a workshop, an organization, a fleet, or a piece
of software (a diagnostic app, an AI assistant, an OCR importer). OVP
deliberately does not special-case "user" vs. "workshop" — both are
identities with different reputations and different grants.

**Provider** — a host for passports, analogous to a Matrix homeserver or
an email provider. Exposes discovery (`.well-known/ovp`), storage, and
an API surface implementations agree to speak. Competes on service
quality, not on lock-in.

**Grant** — a temporary permission linking an Identity to a Vehicle:
read access, write access (ability to append events), or administrative
control (ability to change the passport's home provider). Grants expire
or get revoked; they are not the same thing as "ownership," because the
vehicle isn't owned by an account in this model at all.

## How they compose

```
Vehicle (permanent, globally unique ID)
  └── Passport (hosted at a Provider, can move)
        └── Event Timeline (immutable, append-only)
              ├── produced by Identities (people, workshops, apps)
              └── signed, and readable per current Grants
```

A client (OpenDiag, a dealer tool, a workshop app) never talks to "the
vehicle" directly. It:

1. Resolves the vehicle ID to a provider (`DISCOVERY.md`).
2. Authenticates as some Identity holding a Grant.
3. Reads the event timeline, or appends new signed events.

Nothing about this requires the client and the provider to be built by
the same company. That's the point.

## Why this shape, and not a database with a REST API

A conventional app models "vehicle belongs to user, user belongs to
account, account belongs to a cloud." That collapses three things that
actually have different lifetimes: the vehicle (decades), the account
(years), and the software (months to a few years). Modeling identity,
provider, and event separately lets each rotate independently without
corrupting the other two — which is the entire reason Matrix-style
federation and event sourcing both landed on very similar shapes
independently.

## Storage is an implementation detail, not part of the protocol

OVPF defines the **representation and exchange** of vehicle history — the
event envelope, the hash chain, the fold to derived state (`EVENTS.md`).
It deliberately does not define how a Provider stores that history
internally. A Provider is free to back a passport with a relational
database, an object store, an event-sourcing engine, or a bare git
repository per vehicle — as long as it can answer the same three
questions any other Provider answers: what are the events, are they
intact, and how do I get a copy.

This is a deliberate boundary, not an oversight. The moment the spec
prefers one storage engine, "any provider can host a passport" quietly
becomes "any provider that also runs Postgres/DynamoDB/git can host a
passport" — which is exactly the kind of accidental lock-in OVP exists
to avoid. Providers competing on service quality (`TRUST.md`) only
works if storage stays out of scope entirely.

Git in particular is worth naming explicitly, because it's an obvious
and genuinely tempting fit: immutable history, hash-chained commits,
signing, cloning, and offline-first are most of what OVPF needs, for
free. It's also a plausible storage engine for a specific reference
Provider to prototype (see `ROADMAP.md`) — but that's a choice made at
the Provider layer, evaluated like any other storage engine, not a
protocol requirement. Git's unit of history is a file; OVPF's unit of
history is an event. Where those two models rub against each other
(mutable derived state vs. immutable facts, binary attachments at
scale, querying "all brake replacements") is exactly the kind of
friction a protocol shouldn't force every Provider to inherit.

## Relationship to OpenDiag today

OpenDiag's existing local-first diagnostics data (snapshots, traces,
DTC logs, coding/adaptation changes) is a natural first source of OVP
events. Nothing about this architecture requires ripping that out —
it requires wrapping produced facts in the OVPF event envelope so they
*could* be exported, signed, and handed to any provider, OpenDiag's own
or someone else's.
