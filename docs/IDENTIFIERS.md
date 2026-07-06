# Identifiers

## Vehicle IDs are globally unique

A vehicle receives a globally unique identifier the moment it enters
OVP, independent of OpenDiag or any other provider:

```
ovp:01K0Y5F8G3QZJH2R7T9XN4B6C1
```

The exact encoding (ULID, UUID, or something else) isn't fixed yet — what
matters is the property: this ID never changes, is never reused, and
carries no information about who currently hosts the passport or who
currently owns the vehicle. It is not the VIN. The VIN is a fact
*about* the vehicle, recorded as (or alongside) an event; the OVP ID is
the handle used to look the vehicle up at all, and needs properties the
VIN doesn't have (VINs are reused, get typo'd, and aren't guaranteed
unique across all vehicle types and eras).

## Every passport has a home

An address combines the vehicle ID with its current provider, the same
way an email address combines a mailbox with a domain:

```
ovp:01K0Y5...@passport.opendiag.io
ovp:01K0Y5...@garage.racetune.ee
ovp:01K0Y5...@mygarage.example
```

Today, that's `passport.opendiag.io`. Tomorrow it could be a competing
cloud, or a workshop's self-hosted instance, or a NAS in someone's
garage. The vehicle doesn't move — the label after the `@` does, and
only that label changes.

## The vehicle chooses the provider, not the software

Exactly like choosing an email provider: the client (OpenDiag, a dealer
tool, a workshop app) is not the thing that decides where the passport
lives. The vehicle's current administrative Grant holders do. Migrating
providers should look like: export the timeline, sign a redirect,
publish it, done — not "beg the incumbent vendor for a data dump."

## Delegation, borrowed from Matrix

The permanent ID should be able to resolve to a *different* current home
without changing the identifier itself:

```
ovp:01K0Y5...   -->  passport.opendiag.io   (today)
ovp:01K0Y5...   -->  garage.racetune.ee     (later)
```

This is the same trick Matrix uses to let a user ID (`@alice:matrix.org`)
outlive which homeserver actually hosts Alice's account, and the same
trick email delegation (MX records) uses to let `alice@example.com`
outlive which mail server actually holds Alice's mailbox. See
`DISCOVERY.md` for how resolution actually works.

## QR (and eventually NFC) philosophy

The physical anchor — a QR sticker under the bonnet — encodes the
*vehicle ID only*, never a provider, never an owner, never an OpenDiag
URL. That's the entire reason it can survive twenty years and multiple
provider migrations without being replaced: the sticker is a constant,
and everything mutable is one discovery lookup away, not baked into the
printed code.

A secondary, and almost accidental, benefit: the QR code doubles as a
physical prompt. Seeing it under the bonnet is a reminder to log
whatever maintenance just happened, the same way a service sticker on a
windshield reminds you it's time for an oil change — except this one
never goes stale, because it isn't tied to a date.

NFC is a natural future extension — same identifier, tap instead of
scan, and potentially able to carry a short-lived proof of physical
presence for workshop write events (see `TRUST.md`).
