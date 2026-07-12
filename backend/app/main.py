from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models import RentalPreferences, SearchResponse
from app.providers.mock import MockMapProvider, MockShanghaiListingProvider
from app.service import RentalDecisionService

app = FastAPI(title="RentScout AI API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
service = RentalDecisionService(MockShanghaiListingProvider(), MockMapProvider())


@app.get("/api/health")
async def health():
    return {"status": "ok", "listing_provider": service.listings.name, "map_provider": service.maps.name}


@app.post("/api/search", response_model=SearchResponse)
async def search(preferences: RentalPreferences):
    return await service.search(preferences)

