# Open Vehicle Passport Format (OVPF) — draft sketch v0.1

> **Status: exploratory sketch.** Nothing here is frozen. The goal is to nail
> the *shape* — an append-only, immutable, local-first event log that any tool
> can produce and any tool can replay into "current state" — and to reuse
> existing standards (Schema.org, ISO 8601, VIN, JSON-LD, RFC 8785) rather
> than invent basics.

## 1. Core idea

A vehicle's passport **is** its history: an ordered, append-only log of
**immutable events**. There is no canonical "current state" record — state
(current owner, mileage, open faults, service history) is **derived by
replaying events**. Corrections never mutate or delete; they **append** a new
event that supersedes an earlier one.

```
events  ──fold──▶  derived state (a view, always rebuildable, never authoritative)
```

Producers of events are peers: a **diagnostic** tool (e.g. `kline-diag`),
**maintenance** logging, **manual** entry, **AI** analysis, **imports** from
other apps — and, later, a workshop app, tyre-booking system, mobile app, OCR
importer, dyno software, other-manufacturer diagnostics. None of them owns the
passport; **the vehicle owns its timeline** and they all just append.

**Positioning.** OVPF is meant to be an **open specification** in the spirit
of OpenTelemetry / OpenAPI / OCI / GPX: *applications compete, the data format
is shared*. `kline-diag`/OpenDiag is the **reference implementation**, not the
product. We're not building a database — we're building an immutable timeline
of everything that ever happened to a vehicle, of which "current state" is
just one projection.

## 2. Design principles

1. **Append-only & immutable.** Events are never edited or deleted.
2. **Derived state, not stored state.** Any "current value" is a reduction.
3. **Local-first, portable.** The whole passport is a plain file (an NDJSON
   event stream) the user owns and can export/move. Cloud is optional sync.
4. **Standards over invention.** Schema.org `Vehicle` for the vehicle
   description; ISO 8601 for time; VIN as optional data; JSON-LD for
   linked-data semantics; SI as the canonical unit system (lesson from
   studying MyGarage: version the format, evolve additively, one unit system).
5. **Forward-compatible.** A reader that doesn't recognise an event `type`
   MUST preserve it in the log and MAY ignore it during reduction — never
   drop unknown events. Vendor extensions live under their own namespace
   (e.g. `x-bmw:CodingChanged`).
6. **Anonymous-first (the "Just Open" principle).** A passport is created and
   used with **no account and no identity**: generate UUID → generate QR →
   done. Owner/operator identity is *optional* and *late-bound* — it only
   appears when the user opts into a cloud feature (sync/AI/backup/sharing).
   The format must be fully usable offline and account-free.
7. **Two trust tiers.** *Local default:* anonymous events, optionally
   **hash-chained** (needs no identity, still tamper-evident). *Cloud opt-in:*
   per-producer **signatures** for cross-owner trust — added only once a user
   has chosen to have an identity. Signatures are never required to read,
   write, or replay a passport.

## 2a. Identity & access (the vehicle owns the timeline)

**The vehicle is the only permanent entity.** People, workshops, and the
cloud do not own the history — the vehicle does. Everything else is temporal.

- **Passport identity is a UUID** — the vehicle's, not a VIN and not an
  account: `urn:ovpf:<uuidv7>`. This is what the **QR sticker encodes** (NFC
  later) and the only thing needed to create a passport: mint a UUID, render
  the QR, emit `PassportOpened` — no forms, no VIN, no login. **The QR
  identifies the vehicle, not the owner**, and doubles as a
  log-your-maintenance reminder.
- **VIN is optional data** (a `VehicleIdentified` event / `PassportOpened.
  vehicle`), usable as an alias. A car you don't own yet, or a pre-VIN car,
  still gets a valid passport; VIN (quasi-PII) stays on-device by default.
- **Unified Identity model.** There is no "user" vs "workshop" split — every
  actor is an **Identity** (Person, Workshop, Organization, Fleet, or a
  Diagnostic app), represented cryptographically (a key / passkey), not as a
  server account.
- **Access, not ownership.** Vehicles never belong to accounts. An Identity
  holds **temporal access** to a vehicle (roles: owner/custodian, workshop,
  operator, viewer), granted/revoked over time via events (`AccessGranted` /
  `AccessRevoked`). "Current owner" is just the projection = the Identity
  currently holding the owner role. History is permanent and independent of
  who has access now.
- **Anonymous by default; identity on the producer.** The *vehicle* stays
  account-free and works fully offline. It's the *producers* that carry
  identity: a workshop signs **its** events (§4a), never the vehicle. So a
  passport can be entirely anonymous/local, and signatures attach per-event
  by whoever wants their contribution trusted — never required to read,
  write, or replay.
- **The QR is the entry point.** Scanning opens the passport immediately
  (offline, from the UUID). With cloud enabled the same code resolves via a
  URL (`…/p/<uuid>`); without, the bare UUID still works — Git vs GitHub.

## 3. The event envelope

Every event is a JSON-LD object sharing this envelope. Payload lives in `data`.

| Field | Req | Type | Meaning |
|---|---|---|---|
| `@context` | ✓ | IRI | The OVPF context (§5). Pins vocabulary + versions. |
| `id` | ✓ | `urn:uuid:` | **UUIDv7** — globally unique and time-ordered (gives natural sort + dedup on merge). |
| `type` | ✓ | term | Event type from the OVPF vocabulary (§4) or a namespaced extension. |
| `specVersion` | ✓ | string | OVPF format version, e.g. `"0.1"`. Additive evolution. |
| `vehicle` | ✓ | IRI | Subject passport — always `urn:ovpf:<uuid>` (the QR-encoded id). VIN is optional data, never the identity (§2a). |
| `occurredAt` | ✓ | ISO 8601 | When the real-world event happened (with timezone/offset). |
| `recordedAt` | ✓ | ISO 8601 | When it was appended to the log. (Event time ≠ record time.) |
| `producer` | ✓ | object | What emitted it: `{ type, name, version, device?, operator?, domain?, verified?, verifiedAt? }`. `type ∈ {Diagnostic, Maintenance, Manual, AI, Import, Workshop}`. `domain` is a producer's self-declared identity claim (e.g. `"skoor.ee"`); `verified`/`verifiedAt` are set *only* by the provider that received the event, from its own workshop registry (§4a) — never trust a client-supplied `verified`. |
| `data` | ✓ | object | Event-type-specific payload (§4). |
| `corrects` | – | `urn:uuid:` | The event this supersedes. Pair with `correctionReason`. |
| `attachments` | – | array | Content-addressed blobs: `{ name, mediaType, hash: "sha256:…", uri? }`. Binary stays out of the log, referenced immutably. |
| `prevHash` | – | string | `sha256:` of the previous event's canonical form (RFC 8785 JCS), for chaining. |
| `hash` | – | string | `sha256:` of this event's canonical form (excludes `hash`). |
| `signature` | – | object | Optional producer signature (§4a): `{ identity, alg, sig }` over the canonical event. Proves *who* — never required. |

**Why event-time vs record-time:** a service done last month but logged today
must sort by when it *happened* for mileage/history, while `recordedAt` +
UUIDv7 give a deterministic append order for merging two offline logs.

## 4. Core event types (initial vocabulary)

Namespace `ovpf:`. Payload fields below are the essentials, not exhaustive.

| Type | Producer | Key `data` fields | Standards reused |
|---|---|---|---|
| `PassportOpened` | Manual/Import | genesis. **Requires only the passport UUID** — everything else optional. MAY embed a partial Schema.org `Vehicle`. | schema:Vehicle |
| `VehicleIdentified` | Manual/Diagnostic | adds/refines vehicle facts later (VIN read from the car, make/model/trim…). Lets a passport start blank and learn what it is. | schema:Vehicle |
| `VehicleImported` | Import | a passport created from another system/export; carries `source` + provenance. | — |
| `AccessGranted` / `AccessRevoked` | any Identity w/ authority | `identity` (key/DID), `role` (owner/workshop/operator/viewer), `by?`, `from?`/`until?`. Replaces "ownership transfer" — access is temporal, history isn't. | — |
| `OdometerReading` | Diagnostic/Manual | `value`, `unit` (`km`), `source` (`obd`/`dash`/`manual`) | schema:mileageFromOdometer |
| `DiagnosticTroubleCodeRead` | **Diagnostic** (kline-diag) | `module` (ECU addr+name), `codes[]` (`code`, `status`, `text`, `rawHex`, `envHex?`) | SAE J2012 / OEM hex |
| `DiagnosticTroubleCodeCleared` | **Diagnostic** | `module`, `codesCleared[]`, `snapshotRef?` | — |
| `LiveDataRecorded` | **Diagnostic** | `session`, `channels[]`, `sampleRate`, `attachmentRef` (CSV/NDJSON of samples) | — |
| `EcuCodingChanged` | **Diagnostic** (kline-diag transaction layer) | `module`, `before`, `after`, `preset?`, `backupRef` | — |
| `ServicePerformed` | Maintenance | `serviceType`, `lineItems[]` (`part`, `qty`, `laborHours`, `cost`), `vendor?`, `odometer`, `total`. Concrete kinds are just `serviceType` values (OilChanged, TyresInstalled…). | schema:MonetaryAmount |
| `PartReplaced` | Maintenance | `part` (name, number, `gtin?`), `position?`, `odometer` | schema:Product |
| `DynoRun` | Dyno software | `power`, `torque`, `curveRef` (attachment), `conditions` | schema:QuantitativeValue |
| `EcuTuned` | Tuning/Diagnostic | `map`, `before?`/`after?`, `tool`, `checksumRef` | — |
| `ReminderCreated` | any | `about` (service/inspection due), `dueAt?`, `dueOdometer?` | — |
| `FuelAdded` | Manual | `volume`+`unit` (`L`), `fuelType`, `cost`, `odometer`, `full?` | schema:fuelType |
| `InspectionRecorded` | Manual/Import | `kind` (MOT/TÜV/emissions), `result`, `validUntil`, `authority` | — |
| `RecallNoticed` / `RecallRemedied` | Import | `campaign`, `authority` (NHTSA…), `remedy?` | NHTSA campaign no. |
| `PhotoAdded` / `DocumentAdded` | Manual | `category` (title/receipt/insurance…), `attachmentRef` | schema:MediaObject |
| `AiInsightGenerated` | **AI** | `insight`, `confidence`, `model`, `basis[]` (event ids analysed) | — |
| `NoteAdded` | Manual | `text` | — |

## 4a. Trust — emergent, never manually approved

Trust must require **zero manual verification and zero platform operations**.
It emerges, layered on the integrity floor:

1. **Integrity (local, free):** the hash-chain (§ envelope) proves the log
   wasn't rewritten. No identity needed.
2. **Authenticity (opt-in):** an event MAY carry a `signature` from the
   producing **Identity** (§2a) — a **passkey / WebAuthn** or key signature
   over the canonical event. This is how **workshops sign their work**: every
   service event becomes attributable to *workshop + operator + signing key +
   timestamp*, like a signed Git commit. A buyer verifies signatures offline.
3. **Reputation of the Identity (higher tiers):** an Identity's key can be
   *automatically* bound to a real entity via **business-registry lookups**,
   **domain/email** verification, or accumulated **reputation** — all
   programmatic. **Never a manual approval queue.**

The vehicle never needs any of this; it stays anonymous. Signatures are a
property of *producers*, added only by those who want their contributions
trusted.

**Domain verification, implemented (both reference providers):** a workshop
proves control of a domain the same way ACME/Let's Encrypt does — a DNS TXT
record, checked by the provider itself, no human in the loop:

```
POST /v1/workshops              { domain, name }        -> mints a token
                                 returns a dnsRecord: { type: TXT,
                                 name: "_ovp-verify.<domain>",
                                 value: "ovp-verify=<token>" }
POST /v1/workshops/{domain}/verify                       -> checks DNS now
                                 (idempotent -- call again as DNS propagates)
GET  /v1/workshops/{domain}                              -> current status
```

The check itself is a DNS-over-HTTPS lookup (no DNS library dependency on
either provider). Once verified, `append_event`/`appendEvent` stamps
`producer.verified: true` on any event whose `producer.domain` matches —
looked up server-side at write time, baked into the hash immediately, and
never re-derived later (a workshop losing verified status doesn't
retroactively change what it attested when it signed). Each provider keeps
its own workshop registry; verifying with one provider doesn't verify with
another, by design — there's no shared trust authority to bootstrap.

Notes:
- The **Diagnostic** rows are exactly what `kline-diag` already produces —
  it becomes the first real event producer.
- `AiInsightGenerated.basis[]` cites the event ids it reasoned over →
  provenance stays in the log (AI is a producer, not an oracle).

## 5. Schema.org `@context`

`PassportOpened.data.vehicle` is a Schema.org `Vehicle`, so the passport is
interoperable linked data, not a bespoke table. The mapping lives in
[`context/ovpf-v0.1.context.jsonld`](context/ovpf-v0.1.context.jsonld) — e.g.
`vin → schema:vehicleIdentificationNumber`, `make → schema:brand`,
`modelYear → schema:vehicleModelDate`, `odometer → schema:mileageFromOdometer`.
Only domain concepts Schema.org lacks (DTCs, ECU coding, live-data channels)
get `ovpf:` terms.

## 6. Deriving current state (reduction)

Rebuild any view by folding the (event-time-ordered) log:

| View | Reducer |
|---|---|
| Access / current custodian | fold `AccessGranted`/`AccessRevoked` into a live set of (Identity, role); "owner" = the Identity currently holding the owner role |
| Mileage | max `OdometerReading.value` (+ readings embedded in service/fuel) |
| Open faults | (all `DiagnosticTroubleCodeRead.codes`) − (subsequent `…Cleared`) |
| Service history | ordered list of `ServicePerformed` / `PartReplaced` |
| Vehicle spec | `PassportOpened.vehicle` + later spec-correcting events |

A **correction** is applied by skipping the event whose `id` appears in some
later event's `corrects`, and using the correcting event instead.

## 7. Serialization

- **Passport = NDJSON** (`.ovpf.ndjson`): one envelope per line, append-only.
  Trivial to stream, tail, and merge; git-friendly.
- Canonical hashing (for `hash`/`prevHash`) uses **RFC 8785 JCS** over the
  envelope with `hash` removed: object keys sorted, compact separators,
  UTF-8 (no `\uXXXX` escaping of non-ASCII). **Numbers use ECMAScript's
  `Number::toString`** — a whole-number float has no `.0` (`45.0` canon-
  icalizes as `45`, matching `(45.0).toString()` in JS). This bit
  everyone: a naive Python `json.dumps` keeps the `.0` and hashes
  differently from a JS implementation for the exact same logical event.
  Any implementation MUST match this, not its own language's default
  number formatting, or cross-provider verification silently breaks. See
  `conformance/fixtures` for shared test vectors covering this.
- Merging two offline copies: union by `id`, order by (`occurredAt`, UUIDv7).

## 8. Open questions (to resolve before v0.1 freeze)

- **Owner identity & privacy.** Owners as DIDs / rotating keys? A VIN itself is
  quasi-PII — do we support a VIN-less `urn:ovpf:<uuid>` passport with VIN
  stored as an encrypted/optional event?
- **Signatures.** Is hash-chaining enough, or do we want per-producer digital
  signatures (so a buyer trusts the diagnostic events came from a real tool)?
- **Attachment storage.** Content-addressed (CID/sha256) sidecar directory vs.
  embedded base64 vs. external store.
- **Multi-device merge conflicts.** UUIDv7 + hash chain, or a CRDT layer?
- **Extension governance.** How vendor `x-*:` event types get promoted into the
  core vocabulary.
- **VIN edge cases.** Pre-1981 / non-standard / rebuilt VINs, and vehicles with
  no VIN at all.

## 9. Files in this sketch

- [`OVPF.md`](OVPF.md) — this document.
- [`context/ovpf-v0.1.context.jsonld`](context/ovpf-v0.1.context.jsonld) — the JSON-LD context (Schema.org mapping + `ovpf:` vocab).
- [`schema/envelope.schema.json`](schema/envelope.schema.json) — JSON Schema for the envelope.
- [`examples/e39-passport.ovpf.ndjson`](examples/e39-passport.ovpf.ndjson) — a worked append-only stream for a 1998 523i, incl. a real `kline-diag`-style diagnostic event, sealed with a valid hash-chain.
- [`ovpf.py`](ovpf.py) — **reference reducer + hash-chain verifier** (stdlib). Replays a passport into current state (owner, mileage, open faults, service history); `--seal` (re)computes the chain, `--json` emits state. This fold *is* the definition of "current state".
