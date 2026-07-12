import json
import asyncio
from typing import Any

import httpx


class LLMError(RuntimeError):
    pass


class OpenAICompatibleLLM:
    def __init__(self, base_url: str, api_key: str, model: str, temperature: float = 0):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.temperature = temperature

    @property
    def enabled(self) -> bool:
        return bool(self.base_url and self.api_key and self.model)

    async def complete_json(self, system: str, payload: dict[str, Any], max_tokens: int = 1200) -> tuple[dict[str, Any], int]:
        if not self.enabled:
            raise LLMError("LLM is not configured")
        request = {
            "model": self.model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": json.dumps(payload, ensure_ascii=False)}],
            "temperature": self.temperature,
            "max_tokens": max_tokens,
            "enable_thinking": False,
            "response_format": {"type": "json_object"},
        }
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=60) as client:
                    response = await client.post(f"{self.base_url}/chat/completions", headers={"Authorization": f"Bearer {self.api_key}"}, json=request)
                    response.raise_for_status()
                    body = response.json()
                content = body["choices"][0]["message"]["content"]
                return json.loads(content), int(body.get("usage", {}).get("total_tokens", 0))
            except (httpx.HTTPError, KeyError, TypeError, ValueError) as exc:
                last_error = exc
                if attempt < 2:
                    await asyncio.sleep(attempt + 1)
        raise LLMError(f"LLM JSON request failed after retries: {last_error}") from last_error
