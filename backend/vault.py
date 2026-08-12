"""
Owner unlock verification.

A private generation path (see /vault/* in main.py) lets the campaign owner
generate freely — any scene, any day, ignoring the daily cap, the per-user
limit and the closed-day lock — for testing and demos. It is gated by a single
secret key that only the owner knows.

Security notes:
  * The plaintext key is NEVER stored in this repository. Only the SHA-256
    digest below is stored, computed over a static pepper + the key, so reading
    the source does not reveal the key and the digest is not a bare dictionary
    hash of a common phrase.
  * verify() uses hmac.compare_digest so the comparison is constant-time.
  * The vault routes are registered with include_in_schema=False, so they do
    not appear in /openapi.json or /docs — the surface is not discoverable from
    the running API either.
  * Override the digest per-deploy with the VAULT_KEY_HASH env var (set it to
    the sha256 hex of _PEPPER + your key). Leave it unset to use the default.
"""

import os
import hmac
import hashlib

# Static pepper mixed into the key before hashing. Not a secret on its own —
# it just means the stored digest is not a plain hash of the key phrase, so it
# cannot be reversed with a generic rainbow table.
_PEPPER = "snl-vault::"

# SHA-256 of _PEPPER + the owner key. The key itself is intentionally absent.
_DEFAULT_KEY_HASH = "8999524f615e0a4e1c019cc424f35da8a598ccb5ef0761597d96433cc1b632ca"


def _expected_hash() -> str:
    return (os.getenv("VAULT_KEY_HASH", "").strip() or _DEFAULT_KEY_HASH).lower()


def verify(key: str | None) -> bool:
    """True iff `key` matches the owner unlock key. Constant-time."""
    if not key:
        return False
    digest = hashlib.sha256((_PEPPER + key).encode()).hexdigest()
    return hmac.compare_digest(digest, _expected_hash())
