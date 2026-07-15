import re

from app.models import RentalPreferences

US_CITY = re.compile(r"^.+,\s*[A-Z]{2}$", re.IGNORECASE)
CHINESE_TEXT = re.compile(r"[\u4e00-\u9fff]")
CHINA_CITY = re.compile(r"上海|北京|天津|重庆|广州|深圳|杭州|南京|成都|武汉|西安|苏州")
US_ADDRESS = re.compile(r"\b[A-Z]{2}\s+\d{5}(?:-\d{4})?\b|\b(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd)\b", re.IGNORECASE)


def geography_consistency_error(preferences: RentalPreferences) -> str | None:
    city_is_us = bool(US_CITY.match(preferences.city.strip()))
    city_is_china = bool(CHINA_CITY.search(preferences.city))
    for destination in preferences.destinations:
        address = destination.address.strip()
        mismatch = (city_is_us and bool(CHINESE_TEXT.search(address))) or (city_is_china and bool(US_ADDRESS.search(address)))
        if mismatch:
            return f'目标城市为 {preferences.city}，但通勤地点“{address}”位于其他国家或地区。请修改通勤地址后再计算'
    return None
