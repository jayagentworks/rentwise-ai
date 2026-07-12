import hashlib
from pydantic import BaseModel, Field
from app.llm import LLMError, OpenAICompatibleLLM

class VisualObservation(BaseModel):
    category: str
    observation: str
    confidence: str = Field(pattern="^(低|中|高)$")
    needs_offline_check: bool = True

class ListingImageReport(BaseModel):
    image_hash: str
    observations: list[VisualObservation]
    warnings: list[str]
    llm_tokens: int
    disclaimer: str = "图片只能反映拍摄角度和当时状态，不能证明房源面积、采光时长、结构安全或当前真实状况，请线下核验。"

class ListingImageAnalysisSkill:
    name = "listing_image_analysis"
    def __init__(self, llm: OpenAICompatibleLLM): self.llm = llm

    async def analyze(self, files: list[tuple[bytes, str]]) -> ListingImageReport:
        if not 1 <= len(files) <= 10: raise ValueError("请上传 1 至 10 张房源图片")
        if sum(len(data) for data, _ in files) > 25 * 1024 * 1024: raise ValueError("房源图片总大小不能超过 25MB")
        if any(mime not in {"image/jpeg", "image/png", "image/webp"} for _, mime in files): raise ValueError("仅支持 JPG、PNG 和 WebP")
        prompt = "分析这些租房照片。只报告图片中直接可见的现象，不推断地址、面积、朝向、房东信誉或安全结论。检查可见采光、维护痕迹、潮湿霉斑疑点、装修磨损、收纳和照片视角局限。输出JSON：observations数组(category,observation,confidence为低/中/高,needs_offline_check)，warnings数组。无法判断就明确无法判断。"
        try: result, tokens = await self.llm.analyze_images_json(files, prompt)
        except LLMError as exc: raise ValueError("视觉模型暂时无法分析房源图片") from exc
        observations = [VisualObservation.model_validate(item) for item in result.get("observations", [])[:12]]
        digest = hashlib.sha256(); [digest.update(data) for data, _ in files]
        return ListingImageReport(image_hash=digest.hexdigest(), observations=observations, warnings=[str(x)[:300] for x in result.get("warnings", [])[:6]], llm_tokens=tokens)
