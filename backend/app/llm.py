import json
import asyncio
import base64
from typing import Any

import httpx


class LLMError(RuntimeError):
    pass


class OpenAICompatibleLLM:
    def __init__(self, base_url: str, api_key: str, model: str, temperature: float = 0, vision_model: str = ""):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.vision_model = vision_model

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

    async def extract_images_text(self, images: list[tuple[bytes, str]], max_tokens: int = 5000) -> tuple[str, int]:
        if not self.enabled or not self.vision_model:
            raise LLMError("Vision model is not configured")
        content = []
        for data, mime_type in images:
            encoded = base64.b64encode(data).decode()
            content.append({"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{encoded}"}})
        content.append({"type": "text", "text": "这些图片按顺序组成一份中文住房租赁合同。请逐页完整转写所有可见文字，保留条款编号、金额、日期、甲乙方和标点。不要总结、解释或补写看不清的内容；看不清处标记[无法识别]。"})
        request = {"model": self.vision_model, "messages": [{"role": "user", "content": content}], "temperature": 0, "max_tokens": max_tokens}
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=120) as client:
                    response = await client.post(f"{self.base_url}/chat/completions", headers={"Authorization": f"Bearer {self.api_key}"}, json=request)
                    response.raise_for_status()
                    body = response.json()
                choice = body["choices"][0]
                text = choice["message"]["content"].strip()
                if choice.get("finish_reason") == "length":
                    text += "\n[无法识别：OCR输出达到长度限制，可能存在截断]"
                if len(text) < 30:
                    raise ValueError("OCR returned insufficient text")
                return text, int(body.get("usage", {}).get("total_tokens", 0))
            except (httpx.HTTPError, KeyError, TypeError, ValueError) as exc:
                last_error = exc
                if attempt < 2:
                    await asyncio.sleep(attempt + 1)
        raise LLMError(f"Vision OCR failed after retries: {last_error}") from last_error
