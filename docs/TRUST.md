---
title: Trust
---

# Trust

## The constraint that shapes everything else

The platform owner should have essentially zero operational work. No
manual verification queue, no support ticket saying "please approve my
workshop account," no human standing between a new participant and the
network. If a trust mechanism requires a person at OpenDiag to click
"approve," it doesn't scale past a few hundred participants and it
recreates exactly the kind of gatekeeper OVP is meant to avoid.

Trust has to emerge from verifiable structure instead:

- **Cryptographic signatures** — every event is signed by the Identity
  that produced it (see `EVENTS.md`). Verification is math, not a human
  judgment call.
- **Passkeys / WebAuthn** — individual people authenticate with
  hardware-backed credentials rather than passwords, raising the cost
  of impersonation without anyone at OpenDiag reviewing anything.
- **Domain verification** — a workshop or provider proves control of a
  domain (DNS TXT record, `.well-known` file — the same primitives ACME
  uses for Let's Encrypt) to bind their Identity to a real-world,
  checkable namespace.
- **Business registry verification** — where it matters (e.g., a
  workshop wanting its signature to carry warranty weight), Identity can
  be cross-checked against a public business registry automatically,
  not manually reviewed.
- **Reputation** — accumulated from the (immutable, so unforgeable)
  history of an Identity's own signed events over time. A workshop that
  has signed a thousand consistent events is trusted more than one that
  signed its first event five minutes ago, without anyone declaring that
  by fiat.
- **Immutable history itself** — because nothing can be quietly edited,
  bad-faith behavior (backdating events, forging signatures after the
  fact) leaves permanent, checkable evidence rather than being
  quietly cleaned up.

None of these require a manual approval step. All of them are checks a
machine can run automatically at the moment an event or a Grant is
created.

## Workshops sign work, like signed commits

A service event should eventually be able to carry:

- the workshop's Identity and signing key,
- the specific operator who performed the work,
- a timestamp,
- optionally, an NFC tap confirming physical presence at the vehicle.

This is deliberately modeled on signed Git commits: the point isn't
bureaucratic ceremony, it's that "this workshop attests this happened"
becomes a checkable cryptographic claim instead of an unverifiable line
of text in a database row someone else administers.

## Trust is layered, not binary

A client consuming a vehicle's timeline should be able to see, per
event, *how much* trust backs it — signed by a domain-verified workshop
with ten years of reputation reads differently than signed by a
brand-new, self-declared Identity with no history. OVP doesn't gatekeep
who can produce an event; it makes sure every event carries enough
provenance that consumers (a dealer, an insurer, an AI assistant) can
decide for themselves how much to weigh it. Keeping the network open
and keeping it trustworthy turn out to be the same design problem once
trust is a signal on the event rather than a permission to produce one.
