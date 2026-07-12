# RentWise AI 中文系统架构

## 1. 架构目标

系统采用“确定性决策内核 + Agent 流程编排 + 受约束 LLM”的结构：费用、通勤、硬条件和风险等级由代码或规则计算；LLM只处理开放语言和解释；所有关键结果都能回溯到输入快照和外部证据。

## 2. 总体架构

```mermaid
flowchart TB
    User["匿名租房用户"] --> Browser["React + TypeScript Web"]
    Browser --> Nginx["Nginx 静态站点与 API 代理"]
    Nginx --> API["FastAPI 异步 API"]

    API --> Identity["匿名 ID + Token 哈希认证"]
    API --> RentalGraph["LangGraph 租房决策图"]
    API --> ContractSkill["合同核验 Skill"]
    API --> ImageSkill["房源图片分析 Skill"]
    API --> Memory["偏好 / 收藏 / 历史 / 反馈"]

    RentalGraph --> ListingProvider["ListingProvider 统一房源接口"]
    ListingProvider --> MockListings["MockShanghaiProvider"]
    RentalGraph --> CommuteSkill["CommutePlanningSkill 必须调用"]
    CommuteSkill --> AMap["高德 Web 服务 API"]
    AMap <--> Redis["Redis 路线缓存 + 全局 3 QPS 限流"]
    RentalGraph --> LLM["硅基流动 OpenAI 兼容模型"]
    RentalGraph <--> Checkpoints["PostgreSQL LangGraph Checkpoints"]

    Identity --> PostgreSQL[("PostgreSQL")]
    Memory --> PostgreSQL
    ContractSkill --> PostgreSQL
    ContractSkill --> VisionOCR["视觉 OCR 模型"]
    ContractSkill --> LegalRules["版本化法律规则"]
    ImageSkill --> VisionOCR
    API -. "仅用户明确授权" .-> MinIO[("可选 MinIO")]
```

## 3. 分层说明

| 层级 | 组件 | 职责 |
|---|---|---|
| 交互层 | React、TypeScript | 需求向导、结果对比、历史、收藏、合同与图片上传、中英文切换 |
| 接口层 | Nginx、FastAPI | API代理、匿名认证、参数校验、错误边界、安全响应头 |
| Agent层 | LangGraph | 五阶段决策编排、节点轨迹、checkpoint 和恢复 |
| Skill层 | 通勤、合同、图片 Skill | 封装必须执行或高风险的能力边界 |
| Provider层 | ListingProvider、MapProvider、LLM | 隔离房源、地图和模型供应商实现 |
| 状态层 | PostgreSQL、Redis、MinIO | 事实数据、缓存限流、可选授权文件存储 |
| 工程层 | Docker Compose、Alembic、Pytest、Playwright | 部署、迁移、测试、评估和运维 |

## 4. 租房搜索时序

```mermaid
sequenceDiagram
    actor U as 用户
    participant W as React Web
    participant F as FastAPI
    participant P as PostgreSQL
    participant G as LangGraph
    participant L as ListingProvider
    participant C as 通勤 Skill
    participant R as Redis
    participant A as 高德 API
    participant M as LLM

    U->>W: 提交预算、偏好和多个目的地
    W->>F: POST /api/search + 匿名凭证
    F->>P: 创建 AgentRun
    F->>G: 以 agent_run_id 作为 thread_id
    G->>P: 保存初始 checkpoint
    G->>L: 搜索统一候选房源
    L-->>G: Listing 列表
    G->>M: 将开放偏好映射到已有标签
    M-->>G: 受约束 JSON 映射
    loop 每套房源
        G->>C: 强制计算多目的地通勤
        C->>R: 查询缓存并申请限流许可
        alt 缓存命中
            R-->>C: 路线结果
        else 缓存未命中
            C->>A: 请求真实路线
            A-->>C: 时间和距离
            C->>R: 写入缓存
        end
        G->>G: 计算成本、硬条件、公平性和得分
    end
    G->>M: 依据结构化证据生成解释
    M-->>G: 推荐理由与取舍
    G->>P: 每个节点保存 checkpoint
    G-->>F: SearchResponse
    F->>P: 保存历史快照和完成状态
    F-->>W: 排序结果
    W-->>U: 房源对比与一键联系
```

## 5. LangGraph 状态图

```mermaid
stateDiagram-v2
    [*] --> search_candidates
    search_candidates --> interpret_preferences
    interpret_preferences --> evaluate_and_rank
    evaluate_and_rank --> explain_recommendations
    explain_recommendations --> finalize_response
    finalize_response --> [*]

    search_candidates --> Failed: Provider 异常
    interpret_preferences --> Failed: 模型或状态异常
    evaluate_and_rank --> Failed: 地图异常
    explain_recommendations --> Failed: 未处理异常
    Failed --> Resume: POST /agent-runs/id/resume
    Resume --> LastCheckpoint: 使用相同 thread_id
    LastCheckpoint --> interpret_preferences
    LastCheckpoint --> evaluate_and_rank
    LastCheckpoint --> explain_recommendations
    LastCheckpoint --> finalize_response
```

LLM解释失败通常会走确定性降级模板；高德失败不会用随机时间替代，而是显式返回服务不可用并保留 checkpoint。

## 6. 评分数据流

```mermaid
flowchart LR
    Listing["房源费用与属性"] --> Cost["真实月成本 / 首月现金"]
    Preferences["结构化需求"] --> Hard["硬条件检查"]
    AMap["多目的地路线"] --> Commute["加权 / 最差 / 每周总量"]
    Commute --> Fairness["家庭成员通勤差距"]
    Custom["开放偏好"] --> Mapping["只映射已有标签"]
    Feedback["历史点赞与点踩"] --> Bounded["有限区间反馈调整"]
    Cost --> Score["确定性推荐分"]
    Hard --> Score
    Commute --> Score
    Fairness --> Score
    Mapping --> Score
    Bounded --> Score
    Score --> Rank["硬条件优先 + 分数排序"]
    Rank --> Evidence["结构化推荐证据"]
    Evidence --> Explanation["LLM 受约束解释"]
```

## 7. 合同核验架构

```mermaid
flowchart TD
    Upload["合同照片 / 扫描PDF / 文本文件"] --> Validate["数量、类型和大小校验"]
    Validate --> Extract{"是否存在可提取文本"}
    Extract -->|是| Text["文本标准化"]
    Extract -->|否| Render["PDF逐页转图片"]
    Render --> OCR["视觉 OCR"]
    Upload --> OCR
    OCR --> Text
    Text --> Jurisdiction["全国规则 + 城市适用过滤"]
    Jurisdiction --> Rules["确定性风险规则"]
    Rules --> Sources["法律来源、生效日、地区、核验日"]
    Sources --> Explain["LLM 不改变等级的通俗解释"]
    Explain --> Report["风险报告"]
    Report --> Hash["仅保存哈希与报告"]
```

## 8. 数据存储边界

| 存储 | 保存内容 | 不保存内容 |
|---|---|---|
| PostgreSQL | 匿名 Token 哈希、偏好、收藏快照、搜索历史、反馈、AgentRun、checkpoint、合同报告 | 明文 Token、合同正文和原图 |
| Redis | 高德地理编码与路线缓存、全局限流状态 | 用户长期档案和关键业务事实 |
| 浏览器 localStorage | 匿名 ID、匿名访问 Token | 合同文件和完整服务端历史 |
| MinIO | 仅在启用且用户明确授权时保存的文件 | 默认不保存任何上传原件 |

## 9. 部署架构

```mermaid
flowchart LR
    Internet["用户浏览器"] --> TLS["云负载均衡 / TLS 网关"]
    TLS --> Frontend["Nginx + React"]
    Frontend --> Backend["FastAPI 容器"]
    Backend --> PostgreSQL[("PostgreSQL Volume")]
    Backend --> Redis[("Redis AOF Volume")]
    Backend -. "可选 profile" .-> MinIO[("MinIO Volume")]
    Backend --> AMap["高德"]
    Backend --> SiliconFlow["硅基流动"]
    Backup["backup.ps1 / pg_dump"] --> PostgreSQL
```

生产覆盖配置为后端和前端启用只读文件系统、健康检查、资源限制和自动重启。TLS由入口网关处理，数据库、Redis和MinIO端口不应暴露公网。

## 10. 当前边界与扩展点

- 当前 ListingProvider 是模拟上海数据；真实中国房源数据源是主要剩余业务集成。
- `ListingProvider` 和 `MapProvider` 保持统一接口，新增 Provider 不需要重写 Agent 主流程。
- 法律规则目前覆盖全国基础规则和上海地方规则；其他城市会显示明确缺口提示。
- checkpoint 需要在生产环境配置保留期、清理和归档策略。

