---
title: Discovery
---

# Discovery

## The problem

Given a vehicle ID (from a QR scan, a manual entry, or another event's
reference), a client needs to find out: which provider currently hosts
this passport, and what can that provider's API do? This has to work
without a central registry that every provider must register with,
because a central registry is exactly the kind of chokepoint OVP exists
to avoid.

## The precedent

This is a solved problem, solved more than once, and each solution rhymes:

- **WebFinger** — `.well-known/webfinger` lets any domain answer "who is
  this account and what can I do with them?"
- **Matrix** — `.well-known/matrix/server` and `/client` let a
  human-readable domain (`matrix.org`) delegate to the actual server
  doing the work, which can live somewhere else entirely.
- **OpenID Connect** — `.well-known/openid-configuration` lets a client
  discover an identity provider's capabilities without hardcoding them.
- **ACME / Let's Encrypt** — domain-based proof of control, no manual
  registration step, no human in the loop.

OVP's discovery should be boring by the same standard: a well-known
path, a small JSON document, no manual approval step from anyone.

## `.well-known/ovp`

Every provider exposes discovery metadata at a well-known path, e.g.:

```
GET https://passport.opendiag.io/.well-known/ovp
```

returning (shape illustrative, not final):

```json
{
  "provider": "passport.opendiag.io",
  "ovpf_version": "0.1",
  "api_base": "https://passport.opendiag.io/ovpf/v1",
  "capabilities": ["events.read", "events.append", "attachments", "export"]
}
```

A client that wants to resolve `ovp:01K0Y5...@passport.opendiag.io`
fetches this document once, learns the API base and what the provider
supports, and proceeds — the same shape as fetching a Matrix
`.well-known` file before ever talking to the homeserver.

## Delegation and redirection

Because the *label after the `@`* can change (see `IDENTIFIERS.md`),
resolution has to check for a current redirect before trusting the
label at face value:

1. Client asks the last-known provider: "where does `ovp:01K0Y5...`
   currently live?"
2. If the passport has moved, the provider returns a *signed* redirect
   pointing at the new home (signed by whichever Identity held the
   administrative Grant at the time of the move — see `TRUST.md`).
3. Client follows the redirect, verifies the signature, and repeats
   discovery against the new provider.

This is deliberately closer to Matrix server delegation than to a DNS
CNAME: the redirect is a signed, auditable *event* in its own right
(technically, an event on the vehicle's own timeline: "passport moved
from A to B, authorized by Identity X"), not an unauditable
infrastructure-layer redirect. Anyone inspecting the vehicle's history
later can see exactly when and why it moved.

## What discovery is not

Discovery answers "where do I ask," not "am I allowed to ask." Whether a
given Identity can actually read or write the timeline once it finds the
right provider is a question for `TRUST.md` and the Grant model in
`ARCHITECTURE.md`. Keeping these separate is what makes it possible for
discovery to be fully public and unauthenticated: knowing where a
passport lives should never itself leak the passport's contents.
