"""Download the files listed in vendor.lock at their pinned commits.

Each file must match the sha256 recorded in the lock, or the script stops
before it writes anything.
Usage: python fetch_vendor.py
"""
import hashlib
import json
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOCK = HERE / "vendor.lock"


def main():
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    bodies = {}
    for f in lock["files"]:
        url = f"https://raw.githubusercontent.com/{f['repo']}/{f['commit']}/{f['path']}"
        body = urllib.request.urlopen(url, timeout=60).read()
        digest = hashlib.sha256(body).hexdigest()
        if digest != f["sha256"]:
            raise SystemExit(f"{f['path']}: sha256 {digest} does not match the lock {f['sha256']}")
        bodies[Path(f["path"]).name] = body
    for name, body in bodies.items():
        (HERE / name).write_bytes(body)
        print(f"{name} {hashlib.sha256(body).hexdigest()[:12]}")


if __name__ == "__main__":
    main()
