from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from jwt import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models.calendar_credential import CalendarCredential
from app.models.user import User
from app.schemas.calendar import CalendarStatusResponse, OAuthStartResponse
from app.services.google_calendar import authorization_url, oauth_flow, read_oauth_state, save_credentials

router = APIRouter(prefix="/calendar", tags=["Google Calendar"])

@router.get("/oauth/start", response_model=OAuthStartResponse)
def oauth_start(user: User = Depends(get_current_user)):
    return OAuthStartResponse(authorization_url=authorization_url(user.id))

@router.get("/oauth/callback", include_in_schema=False)
def oauth_callback(code: str = Query(...), state: str = Query(...), db: Session = Depends(get_db)):
    try:
        user_id = read_oauth_state(state)
        flow = oauth_flow(state=state)
        flow.fetch_token(code=code)
        save_credentials(db, user_id, flow.credentials)
        return RedirectResponse(settings.google_oauth_success_url)
    except (InvalidTokenError, ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=f"Google OAuth failed: {exc}") from exc

@router.get("/status", response_model=CalendarStatusResponse)
def status(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    connected = db.scalar(select(CalendarCredential.id).where(CalendarCredential.user_id == user.id)) is not None
    return CalendarStatusResponse(connected=connected)
