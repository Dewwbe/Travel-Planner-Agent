from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.trip import Trip
from app.models.user import User
from app.schemas.trip import TripCreate, TripResponse

router = APIRouter(prefix="/trips", tags=["Trips"])

@router.get("", response_model=list[TripResponse])
def list_trips(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.scalars(select(Trip).where(Trip.user_id == user.id).order_by(Trip.created_at.desc())).all()

@router.post("", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
def create_trip(data: TripCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trip = Trip(user_id=user.id, **data.model_dump())
    trip.currency = trip.currency.upper()
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip

def owned_trip(trip_id: int, user: User, db: Session) -> Trip:
    trip = db.scalar(select(Trip).where(Trip.id == trip_id, Trip.user_id == user.id))
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip

@router.get("/{trip_id}", response_model=TripResponse)
def get_trip(trip_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return owned_trip(trip_id, user, db)

@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(trip_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.delete(owned_trip(trip_id, user, db))
    db.commit()
    return Response(status_code=204)

