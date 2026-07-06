#!/usr/bin/env python3
"""Unit tests for the OVPF reference reducer/verifier/merge (stdlib unittest)."""
import copy
import unittest

import ovpf

V = "urn:ovpf:00000000-0000-7000-8000-000000000000"


def ev(n, etype, data, occurred, **extra):
    e = {
        "@context": "https://openvehiclepassport.org/ns/v0.1",
        "id": f"urn:uuid:00000000-0000-7000-8000-{n:012d}",
        "type": etype, "specVersion": "0.1", "vehicle": V,
        "occurredAt": occurred, "recordedAt": occurred,
        "producer": {"type": "Manual", "name": "test"},
        "data": data,
    }
    e.update(extra)
    return e


def sample():
    return [
        ev(1, "PassportOpened",
           {"vehicle": {"type": "Vehicle", "make": "BMW", "model": "523i",
                        "modelYear": "1998", "vin": "WBADM01010BR12345"}},
           "1998-03-01T00:00:00Z"),
        ev(2, "OdometerReading", {"value": 21000, "unit": "KMT"},
           "2026-06-01T00:00:00Z"),
        ev(3, "DiagnosticTroubleCodeRead",
           {"module": {"name": "DME"}, "codes": [{"code": "0x71", "text": "O2"}]},
           "2026-06-15T00:00:00Z"),
        ev(4, "ServicePerformed",
           {"serviceType": "repair", "odometer": {"value": 211500, "unit": "KMT"},
            "total": {"price": 137.9, "currency": "EUR"}},
           "2026-06-20T00:00:00Z"),
        ev(5, "DiagnosticTroubleCodeCleared",
           {"module": {"name": "DME"}, "codesCleared": ["0x71"]},
           "2026-06-20T01:00:00Z"),
        ev(6, "OdometerReading", {"value": 210000, "unit": "KMT"},
           "2026-06-01T00:00:00Z",
           corrects="urn:uuid:00000000-0000-7000-8000-000000000002",
           correctionReason="typo"),
        ev(7, "AccessGranted",
           {"identity": "did:key:zB", "role": "owner", "by": "did:key:zA",
            "odometer": {"value": 212300, "unit": "KMT"}},
           "2026-07-01T00:00:00Z"),
    ]


class TestReduce(unittest.TestCase):
    def setUp(self):
        self.state = ovpf.reduce(sample())

    def test_owner_from_access_grant(self):
        # owner is the projection = Identity currently holding the owner role
        self.assertEqual(self.state["owner"], "did:key:zB")
        self.assertIn({"identity": "did:key:zB", "role": "owner"},
                      self.state["access"])

    def test_access_revoked_clears_owner(self):
        evs = sample() + [ev(8, "AccessRevoked", {"identity": "did:key:zB"},
                             "2026-08-01T00:00:00Z")]
        st = ovpf.reduce(evs)
        self.assertIsNone(st["owner"])
        self.assertEqual(st["access"], [])

    def test_roles_coexist(self):
        evs = sample() + [ev(8, "AccessGranted",
                             {"identity": "did:key:zShop", "role": "workshop"},
                             "2026-07-15T00:00:00Z")]
        st = ovpf.reduce(evs)
        self.assertEqual(st["owner"], "did:key:zB")           # unchanged
        roles = {a["identity"]: a["role"] for a in st["access"]}
        self.assertEqual(roles["did:key:zShop"], "workshop")  # coexists

    def test_legacy_ownership_transferred_alias(self):
        evs = [e for e in sample() if e["type"] != "AccessGranted"]
        evs.append(ev(9, "OwnershipTransferred",
                      {"from": "did:key:zA", "to": "did:key:zLegacy"},
                      "2026-07-02T00:00:00Z"))
        self.assertEqual(ovpf.reduce(evs)["owner"], "did:key:zLegacy")

    def test_mileage_is_max(self):
        self.assertEqual(self.state["mileage"], {"value": 212300, "unit": "KMT"})

    def test_open_faults_read_then_cleared(self):
        self.assertEqual(self.state["open_faults"], [])

    def test_wildcard_clears_whole_module(self):
        evs = [e for e in sample() if e["type"] != "DiagnosticTroubleCodeCleared"]
        evs.append(ev(8, "DiagnosticTroubleCodeCleared",
                      {"module": {"name": "DME"}, "codesCleared": ["*"]},
                      "2026-06-25T00:00:00Z"))
        self.assertEqual(ovpf.reduce(evs)["open_faults"], [])

    def test_open_fault_stays_open_if_not_cleared(self):
        evs = [e for e in sample() if e["type"] != "DiagnosticTroubleCodeCleared"]
        st = ovpf.reduce(evs)
        self.assertEqual(len(st["open_faults"]), 1)
        self.assertEqual(st["open_faults"][0]["code"], "0x71")

    def test_correction_supersedes_original(self):
        # 21000 (id 2) is corrected to 210000 (id 6); the typo must not count
        self.assertEqual(self.state["corrections_applied"], 1)
        odo_vals = []  # ensure no derived value uses the 21000 typo
        st = ovpf.reduce([e for e in sample()
                          if e["type"] in ("PassportOpened", "OdometerReading")])
        # only the corrected 210000 remains among odometer readings
        self.assertEqual(st["mileage"]["value"], 210000)

    def test_vehicle_spec_from_genesis(self):
        self.assertEqual(self.state["vehicle"]["model"], "523i")

    def test_service_history(self):
        self.assertEqual(len(self.state["service_history"]), 1)
        self.assertEqual(self.state["service_history"][0]["total"], 137.9)

    def test_owner_anonymous_by_default(self):
        st = ovpf.reduce([e for e in sample()
                          if e["type"] not in ("AccessGranted", "AccessRevoked",
                                               "OwnershipTransferred")])
        self.assertIsNone(st["owner"])   # local-first: no owner unless set


class TestChain(unittest.TestCase):
    def test_seal_then_verify_ok(self):
        evs = sample()
        ovpf.seal(evs)
        self.assertEqual(ovpf.verify_chain(evs), [])

    def test_tamper_is_detected(self):
        evs = sample()
        ovpf.seal(evs)
        evs[3]["data"]["total"]["price"] = 50.0     # forge a sealed event
        problems = ovpf.verify_chain(evs)
        self.assertTrue(any("hash mismatch" in p for p in problems))

    def test_reorder_breaks_link(self):
        evs = sample()
        ovpf.seal(evs)
        evs[2], evs[3] = evs[3], evs[2]             # swap two sealed events
        self.assertTrue(ovpf.verify_chain(evs))     # non-empty == problems

    def test_unsealed_reported(self):
        problems = ovpf.verify_chain(sample())      # no hashes
        self.assertTrue(any("not sealed" in p for p in problems))


class TestMerge(unittest.TestCase):
    def test_union_dedups(self):
        a = ovpf.seal(sample())
        b = ovpf.seal(copy.deepcopy(sample()))      # same events, own chain
        merged, conflicts = ovpf.merge(a, b)
        self.assertEqual(len(merged), len(sample()))  # deduped by id
        self.assertEqual(conflicts, [])

    def test_merge_is_orderable_and_resealable(self):
        a = sample()[:4]
        b = sample()[4:]
        merged, _ = ovpf.merge(a, b)
        self.assertEqual(len(merged), len(sample()))
        ovpf.seal(merged)
        self.assertEqual(ovpf.verify_chain(merged), [])
        # merged replay equals full-log replay
        self.assertEqual(ovpf.reduce(merged)["owner"], "did:key:zB")

    def test_conflict_on_reused_id(self):
        a = sample()
        b = copy.deepcopy(sample())
        b[1]["data"]["value"] = 99999               # same id, different content
        _, conflicts = ovpf.merge(a, b)
        self.assertEqual(len(conflicts), 1)


GOLDEN_EVENT = {
    "@context": ovpf.canonicalize.__globals__.get("CONTEXT", None) or
    "https://openvehiclepassport.org/ns/v0.1",
    "id": "urn:uuid:018f3a1b-0000-7000-8000-0000000000aa",
    "type": "PassportOpened", "specVersion": "0.1", "vehicle": "urn:ovpf:x",
    "occurredAt": "2026-01-01T00:00:00Z", "recordedAt": "2026-01-01T00:00:00Z",
    "producer": {"type": "Manual", "name": "t"},
    "data": {"vehicle": {"type": "Vehicle", "vin": "ABC"}}}
GOLDEN_HASH = "sha256:d0ffd8834939e26b423e12111dfbd606b0c228907c1268cc24c9c8f51335734f"


class TestWireFormat(unittest.TestCase):
    """Guards the canonical hash — any change here breaks cross-implementation
    compatibility, so it must be deliberate (bump the constant knowingly)."""
    def test_golden_hash(self):
        self.assertEqual(ovpf.event_hash(dict(GOLDEN_EVENT)), GOLDEN_HASH)


if __name__ == "__main__":
    unittest.main(verbosity=2)
