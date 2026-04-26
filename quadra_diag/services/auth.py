import hashlib
import hmac
import os
import re

from quadra_diag.core.logging import get_logger

logger = get_logger(__name__)


def _is_strong_password(password: str) -> tuple[bool, str]:
    """Check password strength. Returns (is_valid, error_message)."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\]\\/]", password):
        return False, "Password must contain at least one special character."
    return True, ""


def hash_password(password: str, iterations: int = 390000) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"{iterations}${salt.hex()}${digest.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    iterations_text, salt_hex, digest_hex = password_hash.split("$", maxsplit=2)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt_hex),
        int(iterations_text),
    )
    return hmac.compare_digest(digest.hex(), digest_hex)

