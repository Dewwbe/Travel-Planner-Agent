import json
from cryptography.fernet import Fernet, InvalidToken
from app.core.config import settings

def _fernet() -> Fernet:
    if not settings.token_encryption_key:
        raise RuntimeError("TOKEN_ENCRYPTION_KEY is not configured")
    try:
        return Fernet(settings.token_encryption_key.encode())
    except ValueError as exc:
        raise RuntimeError("TOKEN_ENCRYPTION_KEY must be a valid Fernet key") from exc

def encrypt_json(value: dict) -> bytes:
    return _fernet().encrypt(json.dumps(value).encode())

def decrypt_json(value: bytes) -> dict:
    try:
        return json.loads(_fernet().decrypt(value).decode())
    except (InvalidToken, ValueError) as exc:
        raise RuntimeError("Stored Google credential cannot be decrypted") from exc
