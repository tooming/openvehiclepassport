---
title: Vision
---

# Vision

## The question changed

We started by asking "how do I build a cloud app for my diagnostics
tool?" We've arrived at a different question: "how do I define an
Internet protocol for vehicle history?"

Those are different ambitions, and the second one is worth pursuing
deliberately rather than backing into by accident.

## Mission

Build an open protocol that lets any software contribute trustworthy,
signed events to a vehicle's lifetime history — and make that protocol
durable enough to outlive any single application, company, or cloud.

Applications compete. The data format is shared.

Think of the ecosystems around OpenAPI, OpenTelemetry, OCI, and Matrix —
not their implementations, but the fact that a shared, open format let
many implementations interoperate and compete on merit instead of
lock-in.

## The OCI analogy

When Docker appeared, people thought Docker was the innovation. It
wasn't. The lasting innovation came later, when the image format and
runtime were extracted into the OCI specification — the part that let
Docker, Podman, containerd, and Kubernetes all interoperate.

OpenDiag can follow the same path:

- **OVP** (the protocol) is the standard.
- **OpenDiag** is one implementation and — hopefully — a great client.
- Other garage and workshop systems are other implementations.
- Workshops are publishers of signed events.
- AI providers are consumers of standardized vehicle history.

If that ecosystem emerges, OpenDiag doesn't have to be the biggest
application to have had the biggest impact. Defining the common language
could be the contribution that lasts the longest.

## What this is not

- Not a proprietary SaaS with an API bolted on afterward.
- Not "cloud sync for OpenDiag." Cloud sync is one *feature* a provider
  can offer on top of the protocol, not the protocol itself.
- Not a walled garden that requires OpenDiag's involvement to be useful.
  A BMW dealer scanning a QR code in ten years, whose passport lives on
  `garage.racetune.ee`, should be able to fetch the timeline with zero
  OpenDiag involvement, because their software "speaks OVP."

## Core philosophy

**The vehicle is the permanent entity.** People come and go. Owners
change. Workshops change. Cloud providers change. The vehicle's history
remains. Everything else — accounts, sessions, subscriptions — is
temporary and sits on top of that permanent timeline.

**Facts before opinions.** The protocol stores facts: an oil change
happened, a dyno run measured 307 hp, a diagnostic session was recorded.
Applications and AI layer *opinions* on top: "VANOS may be sticking,"
"battery likely to fail within 3 months." Facts are immutable history.
Opinions are disposable interpretation, and are never confused with the
former.

**Local first.** The application works immediately, offline, without a
cloud account. Cloud is optional and adds synchronization, backup, AI,
collaboration, and attachments — it is not a precondition for value.

**Time to first value.** No mandatory login, onboarding, or cloud
registration. A user should complete their first useful task before ever
creating an account.

## The business philosophy

Owning the protocol means we stop having to "sell the cloud" and start
having to sell the best provider. Under an open protocol, people stay
with OpenDiag Cloud because:

- the diagnostics are better,
- the AI is better,
- the workshop ecosystem is larger,
- the UI is nicer,

not because leaving is hard. That is a harder business to run, and a
much better one to be in. It is exactly how we want to compete, and it's
the same bet Matrix, Docker/OCI, and the open web have made before us.

## Immediate next step

Don't write schemas or implementation code yet. Define the architecture:
core entities, event model, trust model, discovery model, provider
model, export/import format. Treat this like designing an Internet
protocol, not another CRUD application — one that should still make
sense in thirty years.
