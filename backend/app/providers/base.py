from abc import ABC, abstractmethod

from app.models import CommuteMode, CommuteResult, Destination, Listing, RentalPreferences


class ListingProvider(ABC):
    name: str

    @abstractmethod
    async def search(self, preferences: RentalPreferences) -> list[Listing]: ...


class MapProvider(ABC):
    name: str

    @abstractmethod
    async def commute(
        self, listing: Listing, destination: Destination, mode: CommuteMode
    ) -> CommuteResult: ...

