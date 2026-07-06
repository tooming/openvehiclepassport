#!/usr/bin/env python3
"""Passport QR — create the physical anchor (offline, local-first).

The QR sticker on the car IS the passport's entry point. It encodes the
passport identity so a scan opens it with no account and (for the app) no
network:

  * default — a URL that *degrades gracefully*:
        https://openvehiclepassport.org/p/<uuid>
    A generic phone camera opens the URL (cloud resolves it, or serves a
    "get the app" page); OpenDiag recognises the `/p/<uuid>` path and opens
    the local passport offline. Git-vs-GitHub: the id works without the host.
  * `--bare` — the pure identity, `urn:ovpf:<uuid>`, no host dependency.

Uses **segno** (pure-Python, zero-deps) so generation works fully offline.

  pip install segno
  python3 qr.py new                         # mint a passport + print its QR (SVG)
  python3 qr.py urn:ovpf:<uuid> -o car.svg  # QR for an existing passport
  python3 qr.py <uuid> --png -o car.png
"""
import argparse
import os
import sys
import time
import uuid as _uuid

import segno

URL_PREFIX = "https://openvehiclepassport.org/p"


def mint_uuid():
    """A UUIDv7 (time-ordered) passport id — same scheme as the producers."""
    ms = int(time.time() * 1000)
    b = bytearray(ms.to_bytes(6, "big") + os.urandom(10))
    b[6] = (b[6] & 0x0F) | 0x70
    b[8] = (b[8] & 0x3F) | 0x80
    return str(_uuid.UUID(bytes=bytes(b)))


def _uuid_of(token):
    """Accept a bare uuid, a urn:ovpf:<uuid>, or a .../p/<uuid> URL."""
    return token.rsplit("/", 1)[-1].replace("urn:ovpf:", "")


def payload(token, bare=False):
    u = _uuid_of(token)
    return f"urn:ovpf:{u}" if bare else f"{URL_PREFIX}/{u}"


def make_qr(token, bare=False):
    # error='m' (~15% recovery) survives a scuffed under-hood sticker.
    return segno.make(payload(token, bare), error="m")


def main(argv):
    ap = argparse.ArgumentParser(description="Generate a passport QR.")
    ap.add_argument("token", help="'new', a uuid, urn:ovpf:<uuid>, or a /p/<uuid> URL")
    ap.add_argument("-o", "--out", help="output file (.svg default, or .png)")
    ap.add_argument("--png", action="store_true", help="write PNG instead of SVG")
    ap.add_argument("--bare", action="store_true", help="encode urn:ovpf:<uuid> (no URL)")
    args = ap.parse_args(argv)

    token = mint_uuid() if args.token == "new" else args.token
    u = _uuid_of(token)
    qr = make_qr(token, bare=args.bare)
    encoded = payload(token, bare=args.bare)

    if args.out or args.png:
        out = args.out or f"passport-{u}.{'png' if args.png else 'svg'}"
        if out.endswith(".png") or args.png:
            qr.save(out, scale=8, border=2)
        else:
            qr.save(out, scale=8, border=2)
        print(f"passport urn:ovpf:{u}")
        print(f"encoded : {encoded}")
        print(f"written : {out}")
    else:
        print(f"passport urn:ovpf:{u}")
        print(f"encoded : {encoded}\n")
        print(qr.terminal(compact=True))    # scannable right in the terminal


if __name__ == "__main__":
    main(sys.argv[1:])
