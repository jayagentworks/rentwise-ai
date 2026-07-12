# 部署与运维

## 本地开发

1. 复制 `.env.example` 为 `.env`，配置高德及可选 LLM。
2. `docker compose up -d --build`
3. 验证 `http://localhost:8000/api/health` 和 `http://localhost:5173`。

后端启动前自动执行 `alembic upgrade head`。禁止直接删除生产数据库卷处理迁移问题。

## 生产覆盖

```powershell
$env:PUBLIC_ORIGIN="https://your-domain.example"
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

TLS 应由入口网关或云负载均衡终止。生产环境必须替换 PostgreSQL、MinIO 和 API 密钥，限制 8000/5432/6379/9000 端口不对公网暴露。

## 可选对象存储

默认 `OBJECT_STORAGE_ENABLED=false`，合同和房源图片不会保存。仅在确有业务需要并取得用户明确授权后：

```powershell
$env:OBJECT_STORAGE_ENABLED="true"
docker compose --profile storage up -d
```

`POST /api/artifacts` 还必须携带表单字段 `consent=true`；用户可通过删除接口移除对象。

## 备份与恢复

运行 `./scripts/backup.ps1` 生成 PostgreSQL custom-format 备份。恢复前先停止写入，再使用 `pg_restore` 到新数据库并运行 `alembic upgrade head`。Redis 只承载缓存和限流状态，不作为事实数据备份源。

## 发布检查

- `docker compose config --quiet`
- `docker compose exec -T backend pytest -q`
- `cd frontend && npm run build && corepack pnpm test:e2e`
- `docker compose exec -T backend python -m evals.run_eval`
- 检查 `/api/health`、安全响应头、Alembic 版本和 checkpoint 表。
