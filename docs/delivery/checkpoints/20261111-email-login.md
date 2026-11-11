# Checkpoint — TASK-0003/0004 邮箱登录

## Completed

- 配置项目缓存内 uv 0.13.7、标准 CPython 3.12.16 和 API 独立虚拟环境；未改系统 PATH。
- PBI-0001 最小技术设计、三任务 DAG 及 G3 角色评估落档；PBI 为 in-progress。
- 后端实现验证码原子发码/校验、SMTP、PG users、30天会话、退出与同源防护，提交 c0de418。
- 前端实现登录页、六格输入、冷却/锁定、Cookie恢复/退出，提交1861c52；生产入口因正式协议/资料尚未交付保持关闭。

## Verified

- API：ruff、mypy、19个测试通过，含PGlite PG协议适配器和真实本机SMTP收件测试。
- Web：lint、typegen/tsc、20个测试、生产构建通过。
- 桌面浏览器本机链路：发码、错码剩余次数、正确登录、刷新保留会话、退出通过。
- 移动视口覆盖请求未生效，实际宽度仍1197/1280；移动验收pending。截图和全部边界见 docs/verification/PBI-0001-local-login.md。

## Current state

- TASK-0003/0004 in-verification，TASK-0005 ready但缺完整验收输入；无G4 go、无发布。
- Web分支task-0004-email-login基于TASK-0001基础分支；API分支task-0003-email-auth。未合并main，未配置远端。
- 本机服务：Web3000，API8000，PGlite5432，fakeredis6379，SMTP1025，本机邮箱8025；均只监听127.0.0.1。

## Next actions

- 优先推进PBI-0002/0003资料与合规：读取各自PBI、FEAT-001技术设计及账号UI；补任务/依赖，承接邮箱身份后的昵称/级别/出生年月/监护同意。
- 正式协议正文及版本由产品提供/确认；不能用测试确认代替正式留痕。
- 配置真实PostgreSQL/Redis/SMTP或CI验证并补充移动浏览器证据，再由TASK-0005评判登录PBI验收。
- 核验部署可信代理/客户端IP，补认证事件与运营契约集成；然后进入题目输入/确认/L1主线。

## Blockers

- 无真实云服务投递/并发证据；正式协议与资料/监护同意尚未交付，生产入口不能开放。
- 浏览器viewport设置未得到390px实际视口，移动验收仍缺证据。
- ADR-001/002仍待GB，阻塞相关能力及内测发布，不阻塞已实现的本机登录切片。

## Open questions

- 远端组件仓及分支保护尚未配置。
- 当前本机PG/Redis为开发验证替身，不得推导生产语义或容量结论。

## Changed artifacts/files

- API源码/配置/迁移/测试见c0de418，Web页面/样式/客户端/测试/类型生成配置见1861c52。
- docs/features/PBI-0001.yaml、pbi-0001-login-implementation.md；docs/tasks/TASK-0003/0004/0005.yaml。
- docs/delivery/gates/20261111-g3-pbi-0001-go.yaml、component-repositories.md、status.md、本检查点。
- docs/verification/PBI-0001-local-login.md、TASK-0004-login-desktop.jpg。

## Last commit

- API c0de418，Web1861c52；交付仓此前9f8f7ea，本次交付制品另存G3提交。

## 本机恢复入口

- Python: E:/AIworkspacke/gesp-tutor-api/.venv/Scripts/python.exe；uv: 交付仓.cache/tools/uv/uv.exe。
- 开发依赖脚本：交付仓.cache/dev-services/start-postgres.mjs（Node）及start-mail-redis.py（API的Python）。这些为本机缓存，不入仓；缺失时按记录的官方pglite-socket/fakeredis/aiosmtpd创建开发环境，生产配置不得依赖它们。
- API按其README与.env.example配置环境变量；AUTH_SECRET每次用secrets.token_urlsafe独立生成，仅给进程，不输出或提交。先运行alembic upgrade head，再运行uvicorn工厂入口。
- Web仓npm run dev -- --port 3000；仅启动Web而没有API/开发依赖时无法发码，不把不可用页面算验收通过。
