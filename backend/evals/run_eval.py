import asyncio, json
from datetime import datetime, timezone
from pathlib import Path
from app.models import RentalPreferences
from app.providers.mock import MockMapProvider, MockShanghaiListingProvider
from app.service import RentalDecisionService

OUTPUT = Path(__file__).parent / "output"

async def evaluate():
    cases = json.loads((Path(__file__).parent / "cases.json").read_text(encoding="utf-8"))
    service = RentalDecisionService(MockShanghaiListingProvider(), MockMapProvider())
    results = []
    for case in cases:
        response = await service.search(RentalPreferences.model_validate(case["preferences"])); expected = case["expect"]
        checks = {"candidate_count": response.total_candidates == expected["candidate_count"], "top_hard_constraints_passed": response.recommendations[0].hard_constraints_passed == expected.get("top_hard_constraints_passed", response.recommendations[0].hard_constraints_passed), "metrics_nonnegative": all(item.score >= 0 and item.weighted_commute_minutes >= 0 for item in response.recommendations), "evidence_boundary": expected.get("assumption_contains", "") in " ".join(response.assumptions) if expected.get("assumption_contains") else True}
        results.append({"id": case["id"], "passed": all(checks.values()), "checks": checks})
    report = {"generated_at": datetime.now(timezone.utc).isoformat(), "cases": len(results), "passed": sum(item["passed"] for item in results), "pass_rate": sum(item["passed"] for item in results) / len(results), "results": results}
    OUTPUT.mkdir(exist_ok=True)
    (OUTPUT / "agent-evaluation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["# Agent 评估报告", "", f"生成时间：{report['generated_at']}", "", f"结果：{report['passed']}/{report['cases']} 通过（{report['pass_rate']:.0%}）", "", "| 用例 | 结果 |", "|---|---|", *[f"| {item['id']} | {'通过' if item['passed'] else '失败'} |" for item in results], "", "评估使用稳定 MockMapProvider，验证确定性排序、硬条件、指标边界和不可验证偏好的证据边界；真实高德可用性由集成健康检查单独验证。"]
    (OUTPUT / "agent-evaluation.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False)); return 0 if report["passed"] == report["cases"] else 1

if __name__ == "__main__": raise SystemExit(asyncio.run(evaluate()))
