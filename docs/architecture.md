# 系统架构

## 组件

```mermaid
flowchart TB
    Browser[React + TypeScript] --> Nginx[Nginx]
    Nginx --> FastAPI[FastAPI]
    FastAPI --> Auth[匿名 ID + Token 哈希认证]
    FastAPI --> Graph[LangGraph 决策流]
    Graph --> Listing[MockShanghaiListingProvider]
    Graph --> CommuteSkill[CommutePlanningSkill 必须调用]
    CommuteSkill --> AMap[AMapProvider]
    AMap --> Redis[(Redis)]
    AMap --> AMapAPI[高德 Web 服务 API]
    FastAPI --> Postgres[(PostgreSQL)]
    FastAPI --> ContractSkill[RentalContractReviewSkill]
    ContractSkill --> Rules[确定性法律规则]
    ContractSkill --> LLM[证据约束 LLM 解释]
```

PostgreSQL 是匿名档案、收藏、历史、反馈和 Agent 运行记录的事实来源。Redis 只保存可丢弃的地图响应缓存和共享限速状态。

## LangGraph 状态图

```mermaid
stateDiagram-v2
    [*] --> search_candidates
    search_candidates --> interpret_preferences
    interpret_preferences --> evaluate_and_rank
    evaluate_and_rank --> explain_recommendations
    explain_recommendations --> finalize_response
    finalize_response --> [*]
```

- `search_candidates`：通过 ListingProvider 获取统一 Listing 模型。
- `interpret_preferences`：将开放偏好映射到已有可验证标签。
- `evaluate_and_rank`：执行真实通勤、成本、硬约束、偏好和公平性计算。
- `explain_recommendations`：只根据结构化证据生成推荐理由和取舍。
- `finalize_response`：生成稳定的结构化响应和假设说明。

状态图中的偏好解析和解释节点可调用 OpenAI 兼容 LLM。LLM 只负责开放偏好理解和自然语言解释，不负责计算成本、通勤或法律结论；失败时保留确定性规则结果。

## 数据表

- `anonymous_users`：匿名身份和 Token 哈希。
- `rental_profiles`：当前租房偏好 JSON 快照。
- `favorites`：收藏时房源快照。
- `search_history`：搜索输入和结果摘要。
- `recommendation_feedback`：用户显式反馈。
- `agent_runs`：LangGraph 运行状态、轨迹和摘要。
- `contract_reviews`：合同文件哈希和风险报告，不保存合同正文。

数据库结构由 Alembic 管理，容器启动前执行 `alembic upgrade head`。LangGraph 每个节点状态由独立 PostgreSQL checkpoint 表持久化；Redis 仍只承载可丢弃缓存与限流状态。
