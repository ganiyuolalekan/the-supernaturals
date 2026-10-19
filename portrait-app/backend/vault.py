"""
Owner unlock verification.

A private generation path (see /vault/* in main.py) lets the event owner
generate freely — any scene, any day, ignoring the daily cap, the per-user
limit and the closed-day lock — for testing and demos. It is gated by a single
secret key that only the owner knows.

Security notes:
  * The plaintext key is NEVER stored in this repository, and there is NO default:
    the vault stays closed until you set VAULT_KEY_HASH. Generate it with
        python -c "import hashlib; print(hashlib.sha256(('vault::' + 'YOUR-KEY').encode()).hexdigest())"
    The digest is computed over a static pepper + the key, so it is not a bare
    dictionary hash of a common phrase.
  * verify() uses hmac.compare_digest so the comparison is constant-time.
  * The vault routes are registered with include_in_schema=False, so they do
    not appear in /openapi.json or /docs — the surface is not discoverable from
    the running API either.
  * Leave VAULT_KEY_HASH unset to disable the vault entirely.
"""

import os
import hmac
import hashlib

# Static pepper mixed into the key before hashing. Not a secret on its own —
# it just means the stored digest is not a plain hash of the key phrase, so it
# cannot be reversed with a generic rainbow table.
_PEPPER = "vault::"

def _expected_hash() -> str:
    return os.getenv("VAULT_KEY_HASH", "").strip().lower()


def verify(key: str | None) -> bool:
    """True iff `key` matches the owner unlock key. Constant-time."""
    expected = _expected_hash()
    if not key or not expected:
        return False
    digest = hashlib.sha256((_PEPPER + key).encode()).hexdigest()
    return hmac.compare_digest(digest, expected)
