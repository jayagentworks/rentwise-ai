import math
import asyncio
import time
import hashlib
import json

import httpx
from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.models import CommuteMode, CommuteResult, Destination, Listing
from app.providers.base import MapProvider


class AMapError(RuntimeError):
    pass


class AMapProvider(MapProvider):
    name = "amap"
    base_url = "https://restapi.amap.com"

    def __init__(self, api_key: str, city: str = "上海", base_url: str | None = None, qps: float = 3, redis_url: str | None = None):
        if not api_key:
            raise ValueError("AMAP_API_KEY is required")
        self.api_key = api_key
        self.city = city
        self._geocode_cache: dict[str, tuple[float, float]] = {}
        self._rate_lock = asyncio.Lock()
        self._next_request_at = 0.0
        self._request_interval = 1.05 / max(qps, 0.1)
        self._qps = max(1, int(qps))
        self.redis = Redis.from_url(redis_url, decode_responses=True) if redis_url else None
        if base_url:
            self.base_url = base_url.rstrip("/")

    async def _wait_for_rate_limit(self) -> None:
        if self.redis:
            script = """
            local key, now, limit = KEYS[1], tonumber(ARGV[1]), tonumber(ARGV[2])
            redis.call('ZREMRANGEBYSCORE', key, 0, now - 1000)
            local count = redis.call('ZCARD', key)
            if count < limit then
              redis.call('ZADD', key, now, ARGV[3])
              redis.call('PEXPIRE', key, 1500)
              return 0
            end
            local oldest = redis.call('ZRANGE', key, 0, 0, 'WITHSCORES')
            return math.max(1, 1000 - (now - tonumber(oldest[2])))
            """
            while True:
                now_ms = int(time.time() * 1000)
                try:
                    delay_ms = await self.redis.eval(script, 1, "amap:rate:global", now_ms, self._qps, f"{now_ms}:{time.monotonic_ns()}")
                    if not delay_ms:
                        return
                    await asyncio.sleep(delay_ms / 1000)
                except RedisError:
                    break
        async with self._rate_lock:
            now = time.monotonic()
            delay = self._next_request_at - now
            if delay > 0:
                await asyncio.sleep(delay)
            self._next_request_at = time.monotonic() + self._request_interval

    async def _get(self, path: str, params: dict[str, str]) -> dict:
        cache_payload = json.dumps({"path": path, "params": sorted(params.items())}, ensure_ascii=False, separators=(",", ":"))
        cache_key = f"amap:response:{hashlib.sha256(cache_payload.encode()).hexdigest()}"
        if self.redis:
            try:
                cached = await self.redis.get(cache_key)
                if cached:
                    return json.loads(cached)
            except RedisError:
                pass
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                await self._wait_for_rate_limit()
                async with httpx.AsyncClient(base_url=self.base_url, timeout=25) as client:
                    response = await client.get(path, params={"key": self.api_key, "output": "JSON", **params})
                    response.raise_for_status()
                    data = response.json()
                break
            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                last_error = exc
                if attempt < 2:
                    await asyncio.sleep(0.5 * (attempt + 1))
        else:
            raise AMapError(f"AMap network request failed after retries: {last_error}") from last_error
        if str(data.get("status")) != "1":
            raise AMapError(f"AMap API error: {data.get('info', 'unknown error')} ({data.get('infocode', '-')})")
        if self.redis:
            try:
                ttl = 30 * 24 * 60 * 60 if path == "/v3/geocode/geo" else 15 * 60
                await self.redis.set(cache_key, json.dumps(data, ensure_ascii=False), ex=ttl)
            except RedisError:
                pass
        return data

    async def geocode(self, address: str) -> tuple[float, float]:
        if address in self._geocode_cache:
            return self._geocode_cache[address]
        data = await self._get("/v3/geocode/geo", {"address": address, "city": self.city})
        if not data.get("geocodes"):
            raise AMapError(f"No geocoding result for: {address}")
        longitude, latitude = data["geocodes"][0]["location"].split(",")
        coordinates = float(longitude), float(latitude)
        self._geocode_cache[address] = coordinates
        return coordinates

    async def commute(self, listing: Listing, destination: Destination, mode: CommuteMode) -> CommuteResult:
        destination_lon, destination_lat = await self.geocode(destination.address)
        origin = f"{listing.longitude:.6f},{listing.latitude:.6f}"
        target = f"{destination_lon:.6f},{destination_lat:.6f}"
        common = {"origin": origin, "destination": target}

        if mode == CommuteMode.TRANSIT:
            data = await self._get("/v3/direction/transit/integrated", {**common, "city": self.city, "cityd": self.city})
            transits = data.get("route", {}).get("transits", [])
            if not transits:
                raise AMapError("No transit route returned")
            route = min(transits, key=lambda item: int(item["duration"]))
        else:
            paths = {
                CommuteMode.DRIVING: "/v3/direction/driving",
                CommuteMode.WALKING: "/v3/direction/walking",
                CommuteMode.BICYCLING: "/v4/direction/bicycling",
            }
            data = await self._get(paths[mode], common)
            route_paths = data.get("route", {}).get("paths", data.get("data", {}).get("paths", []))
            if not route_paths:
                raise AMapError(f"No {mode.value} route returned")
            route = min(route_paths, key=lambda item: int(item["duration"]))

        minutes = math.ceil(int(route["duration"]) / 60)
        distance_km = round(int(route["distance"]) / 1000, 1)
        return CommuteResult(
            destination=destination.label,
            minutes=minutes,
            distance_km=distance_km,
            within_limit=minutes <= destination.max_minutes,
        )
