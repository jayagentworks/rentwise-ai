import pytest

from app.models import Destination, RentalPreferences
from app.providers.mock import MockMapProvider, MockShanghaiListingProvider
from app.service import RentalDecisionService, true_cost


@pytest.mark.asyncio
async def test_search_ranks_and_explains_results():
    prefs = RentalPreferences(monthly_rent_max=6000, monthly_total_max=6500, move_in_date="2026-08-01", destinations=[Destination(label="公司", address="陆家嘴", weight=1, max_minutes=60)], soft_preferences=["采光好"])
    response = await RentalDecisionService(MockShanghaiListingProvider(), MockMapProvider()).search(prefs)
    assert response.total_candidates == 6
    assert response.recommendations[0].reasons
    assert response.recommendations[0].commutes[0].minutes > 0


def test_true_cost_amortizes_agent_fee():
    listing = pytest.importorskip("app.providers.mock").LISTINGS[2]
    from app.models import Listing
    model = Listing(**listing, utilities_estimate=300, deposit_months=1, image_url="https://example.com/a.jpg", source_name="test", source_url="https://example.com")
    monthly, _ = true_cost(model, 12)
    assert monthly == 6800 + 260 + 300 + round(6800 / 12)

