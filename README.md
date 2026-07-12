# RentWise AI

面向中国用户的租房决策 Agent。当前纵向切片通过结构化向导收集需求，使用模拟上海房源与确定性通勤数据，完成硬条件过滤、真实月成本计算、软偏好排序、推荐解释和原平台联系跳转。

> 当前模拟结果仅用于开发和评估，不是真实在租房源。后续通过相同 Provider 接口接入 RentCast、Google Maps 与高德地图。

## 快速启动

```bash
docker compose up --build
```

- Web: http://localhost:5173
- API: http://localhost:8000/docs
- Health: http://localhost:8000/api/health

本地开发：

```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload

cd ../frontend
npm install
npm run dev
```

## 当前业务链路

```mermaid
flowchart LR
    Wizard[结构化需求向导] --> Provider[ListingProvider]
    Provider --> Filter[硬约束过滤]
    Filter --> Map[MapProvider 多目的地通勤]
    Map --> Cost[真实成本计算]
    Cost --> Rank[偏好排序]
    Rank --> Explain[推荐与取舍解释]
    Explain --> Contact[跳转原平台]
```

## Provider 边界

- `MockShanghaiListingProvider`：开发阶段上海模拟房源。
- `MockMapProvider`：基于稳定输入生成确定性通勤，便于测试。
- `RentCastProvider`：待API Key到位后接入美国实时出租房源。
- `GoogleMapsProvider` / `AMapProvider`：分别用于真实验证与中国场景。

## 测试

```bash
cd backend
pytest -q

cd frontend
npm run build
```

## 开发路线

1. 当前：需求向导、搜索、成本、通勤、排序、解释、双语结果。
2. 下一阶段：PostgreSQL匿名档案、收藏、多目的地编辑、房源对比表。
3. Agent阶段：LangGraph状态流、OpenAI兼容模型、图片与合同法律核验。
4. 真实数据阶段：RentCast、Google Maps和高德Provider、缓存与额度保护。
5. 交付阶段：端到端测试、Agent评估集、完整架构和面试材料。
