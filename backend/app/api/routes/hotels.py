from fastapi import APIRouter, Depends
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.hotel import HotelSearchRequest, HotelSearchResponse
from app.services.hotel_mcp import search_hotels_via_mcp

router = APIRouter(prefix="/hotels", tags=["Hotel MCP"])

@router.post("/search", response_model=HotelSearchResponse)
async def search_hotels(data: HotelSearchRequest, _: User = Depends(get_current_user)):
    return HotelSearchResponse(hotels=await search_hotels_via_mcp(data))
