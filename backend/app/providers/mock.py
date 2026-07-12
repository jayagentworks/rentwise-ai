import hashlib
import math

from app.models import CommuteMode, CommuteResult, Destination, Listing, RentalPreferences
from app.providers.base import ListingProvider, MapProvider


LISTINGS = [
    dict(id="SH-PD-001", title="张江地铁旁明亮一居", district="浦东新区", neighborhood="张江汤臣豪园", address="浦东新区晨晖路88弄", monthly_rent=5200, service_fee_monthly=0, property_fee_monthly=180, agent_fee_once=0, bedrooms=1, area_sqm=42, floor=8, has_elevator=True, allows_pets=True, rental_type="entire", latitude=31.204, longitude=121.590, tags=["近地铁", "采光好", "民水民电"]),
    dict(id="SH-YP-002", title="五角场生活圈整租一室", district="杨浦区", neighborhood="文化花园", address="杨浦区国权东路99弄", monthly_rent=4700, service_fee_monthly=470, property_fee_monthly=120, agent_fee_once=0, bedrooms=1, area_sqm=38, floor=5, has_elevator=False, allows_pets=False, rental_type="entire", latitude=31.301, longitude=121.510, tags=["商业便利", "安静", "老小区"]),
    dict(id="SH-MH-003", title="虹桥通勤友好两居", district="闵行区", neighborhood="金汇花园", address="闵行区红松路175弄", monthly_rent=6800, service_fee_monthly=0, property_fee_monthly=260, agent_fee_once=6800, bedrooms=2, area_sqm=71, floor=11, has_elevator=True, allows_pets=True, rental_type="entire", latitude=31.188, longitude=121.382, tags=["两居", "电梯", "适合家庭"]),
    dict(id="SH-JA-004", title="静安内环精装一居", district="静安区", neighborhood="大宁瑞仕花园", address="静安区广延路1188弄", monthly_rent=6200, service_fee_monthly=0, property_fee_monthly=300, agent_fee_once=3100, bedrooms=1, area_sqm=45, floor=15, has_elevator=True, allows_pets=False, rental_type="entire", latitude=31.283, longitude=121.455, tags=["精装修", "地铁", "物业好"]),
    dict(id="SH-BS-005", title="宝山大场阳光两居", district="宝山区", neighborhood="乾溪新村", address="宝山区环镇北路699弄", monthly_rent=4300, service_fee_monthly=0, property_fee_monthly=100, agent_fee_once=0, bedrooms=2, area_sqm=66, floor=4, has_elevator=False, allows_pets=True, rental_type="entire", latitude=31.315, longitude=121.414, tags=["性价比", "南北通透", "适合家庭"]),
    dict(id="SH-XH-006", title="漕河泾品质合租主卧", district="徐汇区", neighborhood="田林十二村", address="徐汇区田林东路99弄", monthly_rent=3600, service_fee_monthly=360, property_fee_monthly=0, agent_fee_once=0, bedrooms=1, area_sqm=24, floor=6, has_elevator=False, allows_pets=False, rental_type="shared", latitude=31.174, longitude=121.431, tags=["合租", "近公司", "独立阳台"]),
]


class MockShanghaiListingProvider(ListingProvider):
    name = "mock-shanghai"

    async def search(self, preferences: RentalPreferences) -> list[Listing]:
        return [
            Listing(
                **item,
                utilities_estimate=300,
                deposit_months=1,
                image_url=f"https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=900&auto=format&fit=crop&q=80&sig={index}",
                source_name="演示房源",
                source_url=f"https://example.com/listings/{item['id']}",
            )
            for index, item in enumerate(LISTINGS)
        ]


class MockMapProvider(MapProvider):
    name = "mock-map"

    async def commute(self, listing: Listing, destination: Destination, mode: CommuteMode) -> CommuteResult:
        digest = hashlib.sha256(f"{listing.id}:{destination.address}:{mode}".encode()).digest()
        baseline = 18 + digest[0] % 52
        multiplier = {"transit": 1.0, "driving": 0.78, "walking": 2.4, "bicycling": 1.35}[mode.value]
        minutes = round(baseline * multiplier)
        distance = round(max(1.2, minutes * (0.38 if mode == CommuteMode.TRANSIT else 0.55)), 1)
        return CommuteResult(destination=destination.label, minutes=minutes, distance_km=distance, within_limit=minutes <= destination.max_minutes)

