---
title: Roadmap
---

# Roadmap

The order matters: get the shape of the format right on a single
implementation before worrying about federation across many providers
nobody has built yet.

## Phase 0 — Philosophy (this directory)

Write down the vision, architecture, and principles while they're fresh.
No JSON Schema yet, no code yet. Done when the docs in this directory
stop changing shape on every re-read.

## Phase 1 — OpenDiag as the reference implementation

- Wrap OpenDiag's existing local facts (snapshots, DTC logs,
  coding/adaptation changes) in the OVPF event envelope, locally, with
  no cloud requirement.
- Define the first real (versioned) JSON Schema for the event envelope
  and a first handful of event types, driven by what OpenDiag actually
  produces today rather than speculative types nobody emits yet.
- Local-only signing: events are signed with a locally-held key even
  before any provider or sync exists, so "immutable and signed" is true
  from day one, not bolted on later.

## Phase 2 — Export / import and a single reference provider

- Export a vehicle's full timeline to a portable file; import it
  elsewhere. Portability has to work before there are two providers to
  move *between*, or it will quietly get deprioritized once there's a
  business incentive not to finish it.
- Stand up OpenDiag Cloud as the *Reference Provider* — explicitly named
  as one implementation, not "the" official home for passports.
- Implement `.well-known/ovp` discovery (`DISCOVERY.md`) against this
  single provider, so the discovery *shape* is proven even with only one
  provider to discover.

## Phase 3 — Identity and trust primitives

- Passkey/WebAuthn-backed Identities for people.
- Domain-verified Identities for workshops and providers.
- Signed events end-to-end: producer signs, provider stores the
  signature verbatim, any consumer can verify without trusting the
  provider's word for it.
- Grants as first-class, expiring, revocable objects rather than
  implicit "you're logged in so you can see everything."

## Phase 4 — Multi-provider and delegation

- A second, independent provider implementation (even a minimal one)
  to pressure-test that the spec doesn't secretly assume OpenDiag
  internals.
- Passport migration between providers, including the signed
  `PassportMoved` event and redirect-following described in
  `DISCOVERY.md`.
- Reputation signals surfaced to consumers, per `TRUST.md`.

## Phase 5 — Ecosystem

- Third-party event producers: workshop software, tyre-booking systems,
  dyno software, OCR importers, mobile maintenance apps, other
  diagnostic tools.
- Dealer and insurer read-only consumption of timelines they don't
  host.
- A formal spec document and versioning process for OVPF, at the point
  where enough real usage exists to know what actually needs to be
  pinned down.

## What doesn't belong on this roadmap

Anything that requires OpenDiag to approve, whitelist, or onboard a
specific third party before they can participate. If a milestone reads
like "OpenDiag reviews and approves X," it belongs in `TRUST.md` as a
problem to solve cryptographically instead, not in this roadmap as a
process to run.
