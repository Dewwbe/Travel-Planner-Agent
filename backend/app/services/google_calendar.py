from datetime import datetime, timedelta, timezone
import jwt
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.calendar_credential import CalendarCredential
from app.services.token_crypto import decrypt_json, encrypt_json

SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events",
]

def _client_config():
    if not settings.google_client_id or not settings.google_client_secret:
        raise RuntimeError("Google OAuth client is not configured")
    return {"web": {
        "client_id": settings.google_client_id,
        "client_secret": settings.google_client_secret,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": [settings.google_redirect_uri],
    }}

def oauth_flow(state: str | None = None) -> Flow:
    return Flow.from_client_config(_client_config(), scopes=SCOPES,
                                   redirect_uri=settings.google_redirect_uri, state=state)

def create_oauth_state(user_id: int) -> str:
    return jwt.encode({"sub": str(user_id), "purpose": "google_oauth",
                       "exp": datetime.now(timezone.utc) + timedelta(minutes=10)},
                      settings.jwt_secret, algorithm=settings.jwt_algorithm)

def read_oauth_state(state: str) -> int:
    payload = jwt.decode(state, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    if payload.get("purpose") != "google_oauth":
        raise jwt.InvalidTokenError("Invalid OAuth state purpose")
    return int(payload["sub"])

def authorization_url(user_id: int) -> str:
    flow = oauth_flow()
    url, _ = flow.authorization_url(access_type="offline", include_granted_scopes="true",
                                    prompt="consent", state=create_oauth_state(user_id))
    return url

def save_credentials(db: Session, user_id: int, credentials: Credentials):
    data = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": list(credentials.scopes or SCOPES),
        "expiry": credentials.expiry.isoformat() if credentials.expiry else None,
    }
    row = db.scalar(select(CalendarCredential).where(CalendarCredential.user_id == user_id))
    if not row:
        row = CalendarCredential(user_id=user_id, encrypted_token=b"", scopes="")
        db.add(row)
    row.encrypted_token = encrypt_json(data)
    row.scopes = " ".join(data["scopes"])
    db.commit()

def load_credentials(db: Session, user_id: int) -> Credentials:
    row = db.scalar(select(CalendarCredential).where(CalendarCredential.user_id == user_id))
    if not row:
        raise RuntimeError("Google Calendar is not connected")
    data = decrypt_json(row.encrypted_token)
    expiry = datetime.fromisoformat(data["expiry"]) if data.get("expiry") else None
    credentials = Credentials(token=data.get("token"), refresh_token=data.get("refresh_token"),
                              token_uri=data.get("token_uri"), client_id=data.get("client_id"),
                              client_secret=data.get("client_secret"), scopes=data.get("scopes"),
                              expiry=expiry)
    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        save_credentials(db, user_id, credentials)
    return credentials

def calendar_service(db: Session, user_id: int):
    return build("calendar", "v3", credentials=load_credentials(db, user_id), cache_discovery=False)
