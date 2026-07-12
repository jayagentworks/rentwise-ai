# 简历项目描述

## 精简版

**RentWise AI｜React、FastAPI、LangGraph、PostgreSQL、Redis、Docker**

- 设计租房决策 Agent，将候选房源统一为 Provider 接口，确定性计算真实月成本、多目的地通勤上限、家庭公平性和偏好得分。
- 接入高德 Web API，以 Redis 缓存和 Lua 全局限流将路线请求稳定控制在 3 QPS；外部服务失败时显式返回错误，避免随机数据污染决策。
- 使用 LangGraph 编排五阶段决策流，并通过 PostgreSQL checkpointer 持久化节点状态、支持失败恢复；LLM 仅执行标签约束偏好解析和证据忠实解释。
- 实现合同照片/扫描 PDF OCR 与版本化法律规则 Skill、房源图片观察 Skill、匿名长期记忆、反馈学习、收藏和可回放历史。
- 建立 Pytest、Playwright 和 Agent 固定评估集；使用 Alembic、Docker Compose、可选 MinIO、生产安全头和备份脚本完成工程化交付。

## 可量化结果

- 15 项后端自动化测试通过。
- 2 条核心 Playwright 端到端流程通过。
- Agent 基准评估 3/3 通过。
- 高德路线请求上限 3 QPS，缓存跨实例共享。
