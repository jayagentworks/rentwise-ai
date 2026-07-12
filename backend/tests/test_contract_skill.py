import pytest

from app.skills.contract import RentalContractReviewSkill


@pytest.mark.asyncio
async def test_contract_skill_detects_repair_and_missing_terms():
    text = """住房租赁合同\n甲方出租人张某，乙方承租人李某。房屋地址上海市某路1号。租期一年，月租金5000元，押金5000元。任何维修费用全部由承租人承担。"""
    report = await RentalContractReviewSkill().review("contract.txt", text.encode())
    rule_ids = {finding.rule_id for finding in report.findings}
    assert "all_repairs_tenant" in rule_ids
    assert "missing_essential_terms" in rule_ids
    assert report.document_hash


@pytest.mark.asyncio
async def test_contract_skill_rejects_unsupported_file():
    with pytest.raises(ValueError, match="仅支持"):
        await RentalContractReviewSkill().review("contract.docx", b"x" * 100)
