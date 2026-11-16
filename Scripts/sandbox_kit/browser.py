"""The Chromium the vault's pages are opened in, for a test or a check."""
import os
import subprocess


def chromium():
    """$CHROMIUM, or nixpkgs' chromium built on demand"""
    if os.environ.get("CHROMIUM"):
        return os.environ["CHROMIUM"]
    out = subprocess.run(["nix", "build", "--no-link", "--print-out-paths", "nixpkgs#chromium"],
                         check=True, capture_output=True, text=True).stdout.strip()
    return out + "/bin/chromium"
