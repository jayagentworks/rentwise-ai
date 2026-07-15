from app.models import Destination, RentalPreferences
from app.validation import geography_consistency_error


def preferences(city: str, address: str) -> RentalPreferences:
    return RentalPreferences(city=city, monthly_rent_max=3000, monthly_total_max=3500, move_in_date="2026-08-01", destinations=[Destination(label="Office", address=address, weight=1, max_minutes=60)])


def test_rejects_chinese_destination_for_us_city():
    error = geography_consistency_error(preferences("Austin, TX", "上海市浦东新区陆家嘴"))
    assert error == "目标城市为 Austin, TX，但通勤地点“上海市浦东新区陆家嘴”位于其他国家或地区。请修改通勤地址后再计算"


def test_allows_destination_in_same_country():
    assert geography_consistency_error(preferences("Austin, TX", "Downtown Austin, TX 78701")) is None


def test_rejects_us_destination_for_chinese_city():
    assert geography_consistency_error(preferences("上海", "1 Main Street, Austin, TX 78701")) is not None
