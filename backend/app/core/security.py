import hashlib
import hmac
import secrets


HASH_NAME = 'sha256'
ITERATIONS = 260_000
SALT_BYTES = 16


def hash_password(password: str) -> str:
    salt = secrets.token_hex(SALT_BYTES)
    digest = hashlib.pbkdf2_hmac(HASH_NAME, password.encode('utf-8'), salt.encode('utf-8'), ITERATIONS)
    return f'pbkdf2_{HASH_NAME}${ITERATIONS}${salt}${digest.hex()}'


def verify_password(password: str, stored_hash: str) -> bool:
    if not stored_hash:
        return False
    parts = stored_hash.split('$')
    if len(parts) != 4:
        return hmac.compare_digest(password, stored_hash)
    algorithm, iterations, salt, expected = parts
    if algorithm != f'pbkdf2_{HASH_NAME}':
        return False
    digest = hashlib.pbkdf2_hmac(HASH_NAME, password.encode('utf-8'), salt.encode('utf-8'), int(iterations))
    return hmac.compare_digest(digest.hex(), expected)
