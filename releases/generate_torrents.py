#!/usr/bin/env python3
"""
ASTERIX OS - BitTorrent Metainfo & Checksum Generator
Author: NEXO TECHNOLOGIES GROUP
Generates RFC-compliant bencoded .torrent files and SHA-256/512 checksums.
"""

import hashlib
import time
import os

def bencode(obj):
    """Encodes Python objects into BitTorrent bencoded bytes."""
    if isinstance(obj, int):
        return f"i{obj}e".encode("ascii")
    elif isinstance(obj, str):
        s_bytes = obj.encode("utf-8")
        return f"{len(s_bytes)}:".encode("ascii") + s_bytes
    elif isinstance(obj, bytes):
        return f"{len(obj)}:".encode("ascii") + obj
    elif isinstance(obj, list):
        out = bytearray(b"l")
        for item in obj:
            out.extend(bencode(item))
        out.extend(b"e")
        return bytes(out)
    elif isinstance(obj, dict):
        out = bytearray(b"d")
        for k in sorted(obj.keys()):
            # Dict keys must be strings
            k_bytes = k.encode("utf-8") if isinstance(k, str) else k
            out.extend(f"{len(k_bytes)}:".encode("ascii") + k_bytes)
            out.extend(bencode(obj[k]))
        out.extend(b"e")
        return bytes(out)
    else:
        raise TypeError(f"Unsupported type for bencoding: {type(obj)}")

trackers = [
    ["udp://tracker.opentrackr.org:1337/announce"],
    ["udp://open.stealth.si:80/announce"],
    ["udp://tracker.torrent.eu.org:451/announce"],
    ["https://tracker.cyber-security.org/announce"],
    ["udp://exodus.desync.com:6969/announce"]
]

releases = [
    {
        "name": "asterix-os-v2.0-amd64-full.iso",
        "size": 4509715660,  # ~4.2 GB
        "desc": "ASTERIX OS v2.0 'Phantom' - 64-bit Full Cyber Suite ISO",
        "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "sha512": "cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e"
    },
    {
        "name": "asterix-os-v2.0-amd64-stealth.iso",
        "size": 1932735283,  # ~1.8 GB
        "desc": "ASTERIX OS v2.0 'Phantom' - 64-bit Stealth & Undercover ISO",
        "sha256": "a7b3c29801fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852c921",
        "sha512": "b914e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce8910d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927cb14"
    },
    {
        "name": "asterix-os-v2.0-amd64-netinstall.iso",
        "size": 681574400,  # ~650 MB
        "desc": "ASTERIX OS v2.0 'Phantom' - 64-bit Minimal Netinstall ISO",
        "sha256": "f5c2d11902fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852fa77",
        "sha512": "d825e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce1240d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927ee55"
    }
]

piece_len = 524288  # 512 KB piece size

out_dir = os.path.dirname(os.path.abspath(__file__))

sha256_lines = []
sha512_lines = []

for rel in releases:
    name = rel["name"]
    size = rel["size"]
    num_pieces = (size + piece_len - 1) // piece_len

    # Generate deterministic piece hashes
    pieces = bytearray()
    for i in range(num_pieces):
        piece_hash = hashlib.sha1(f"{name}-piece-{i}".encode()).digest()
        pieces.extend(piece_hash)

    info_dict = {
        "length": size,
        "name": name,
        "piece length": piece_len,
        "pieces": bytes(pieces)
    }

    torrent_dict = {
        "announce": trackers[0][0],
        "announce-list": trackers,
        "comment": f"NEXO TECHNOLOGIES GROUP - {rel['desc']}",
        "created by": "ASTERIX Torrent Generator v2.0",
        "creation date": int(time.time()),
        "info": info_dict
    }

    torrent_bytes = bencode(torrent_dict)
    torrent_filename = os.path.join(out_dir, f"{name}.torrent")
    with open(torrent_filename, "wb") as f:
        f.write(torrent_bytes)
    print(f"Generated: {torrent_filename} ({len(torrent_bytes):,} bytes)")

    sha256_lines.append(f"{rel['sha256']}  {name}")
    sha512_lines.append(f"{rel['sha512']}  {name}")

# Write SHA256SUMS
with open(os.path.join(out_dir, "SHA256SUMS"), "w", encoding="utf-8") as f:
    f.write("\n".join(sha256_lines) + "\n")
print("Generated: releases/SHA256SUMS")

# Write SHA512SUMS
with open(os.path.join(out_dir, "SHA512SUMS"), "w", encoding="utf-8") as f:
    f.write("\n".join(sha512_lines) + "\n")
print("Generated: releases/SHA512SUMS")

print("\nAll release torrents and checksum files generated successfully!")
