---
title: Events
---

# Events

## Everything is an immutable event

A vehicle's history is a timeline of append-only events. Nothing is ever
edited or deleted in place. A mistake, a correction, or a status change
is recorded as a *new* event that supersedes or references the old one —
the same discipline as signed Git commits or a ledger, and for the same
reason: an editable history is not a trustworthy one.

"Current state" — mileage, whether the timing belt has been done,
whether there's an open recall — is never stored directly. It's always
a *projection*, computed by replaying the timeline. This keeps the
source of truth singular even as ten different applications each want a
different summary view of the same vehicle.

## Example event types

- `OilChanged`
- `TyresInstalled`
- `DiagnosticSession`
- `DynoRun`
- `ECUTuned`
- `ReminderCreated`
- `AccessGranted` / `AccessRevoked`
- `PassportMoved` (see `DISCOVERY.md`)
- `OwnershipTransferred`

This list is intentionally not exhaustive or final — the event type
namespace needs to stay extensible without a central body having to
bless every new type a workshop or integrator wants to add. (Likely
shape: a reverse-domain or namespaced `type` field, so third parties can
mint their own event types without collision, the way custom MIME types
or Matrix event types work.)

## Facts before opinions

Events fall into two categories, and the format must never blur them:

- **Facts** — things that happened, verifiable in principle, produced
  by a person, a workshop, or a piece of equipment. *"Oil changed on
  2026-07-06." "Dyno measured 307 hp." "Diagnostic session recorded
  DTC P0300."*
- **Opinions** — interpretation layered on top of facts, produced by
  software or AI, and explicitly not immutable in the same sense.
  *"AI believes VANOS solenoid is sticking." "AI predicts battery
  failure within 90 days."*

Opinions can be regenerated, superseded, or discarded as models improve.
Facts cannot. An event schema should make it structurally obvious which
one you're looking at — e.g., a top-level `kind: fact | opinion` — so no
downstream consumer can accidentally treat a prediction as history.

## The event envelope (illustrative)

Every event, regardless of type, carries a common envelope so any client
can at least verify and order events it doesn't understand the payload
of:

```json
{
  "id": "evt_01K0Y6...",
  "vehicle_id": "ovp:01K0Y5...",
  "type": "com.opendiag.oil_changed",
  "kind": "fact",
  "timestamp": "2026-07-06T09:14:00Z",
  "actor": "ovp-identity:workshop:racetune-tallinn",
  "signature": "ed25519:...",
  "payload": { "product": "5W-30", "quantity_l": 5.5 },
  "attachments": ["ovp-blob:sha256:..."]
}
```

- `id` is unique and immutable once issued.
- `actor` references an Identity (see `ARCHITECTURE.md`), not a raw
  user account.
- `signature` lets any party — not just the hosting provider — verify
  the event wasn't forged or altered after the fact (see `TRUST.md`).
- `attachments` point at content-addressed blobs (photos, PDFs, raw scan
  dumps) rather than embedding them, so large payloads don't bloat the
  timeline itself.

## Corrections append, they don't rewrite

If a workshop logs the wrong date or the wrong part, the fix is a new
event referencing the one it corrects (`supersedes: "evt_..."`), not an
edit to the original. The original stays visible, because part of the
value of an immutable timeline is being able to see *that* a correction
happened, not just the corrected value.
