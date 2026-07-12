import pytest
from app.skills.listing_image import ListingImageAnalysisSkill

class FakeVision:
    async def analyze_images_json(self, images, prompt):
        return {"observations": [{"category":"潮湿疑点","observation":"墙角存在颜色差异，无法仅凭照片确认霉斑","confidence":"低","needs_offline_check":True}], "warnings":["照片视角有限"]}, 80

@pytest.mark.asyncio
async def test_listing_image_analysis_is_evidence_limited():
    report = await ListingImageAnalysisSkill(FakeVision()).analyze([(b"image", "image/jpeg")])
    assert report.observations[0].needs_offline_check is True
    assert report.llm_tokens == 80
