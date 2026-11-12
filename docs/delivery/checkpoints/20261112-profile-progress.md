# Checkpoint — TASK-0006/0007 资料设置与整体进度

## Completed

- 用户确认PC为重点开发/完整验收端，移动仅浏览器同页自适应查看；已同步项目上下文、NFR-USE-01、相关PBI/设计补记及TASK-0005，不再以移动专项阻塞PC主线。
- PBI-0002最小技术设计、TASK-0006/0007/0008、G3角色记录落档；资料/级别代码本机可运行。
- API分支task-0006-profile-level提交87f81b4；Web分支task-0007-profile-settings提交851bfc2。未合main，尚无组件仓远端。
- 已提供docs/delivery/development-progress.md：模块总览、全部26个PBI、暂缓项及下一批顺序，区分设计/编码/验收。

## Verified

- API ruff/mypy及47个测试通过；Web lint/typegen/tsc、32个测试及生产构建通过。
- PC实际链路：登录→首次资料→测试监护确认→保存→设置→当前3级/待生效4级→刷新保持；截图与证据见docs/verification/PBI-0002-local-profile.md。
- 跨日/取消/覆盖/冻结整数快照、PG事务回滚、版本拒绝、身份/字段校验和停用账号均有测试。
- 本机PGlite单连接问题已在.cache/dev-services/start-postgres.mjs以完整连接排队解决；应用仍用既定PG协议适配器，不把本机排队策略当生产方案。

## Current state

- PBI-0001/0002/0022为in-progress；G3通过3项，G4通过0项，未发布。
- TASK-0006/0007 in-verification；TASK-0008待正式依赖与学习会话历史集成。PBI-0003仅有年龄规则/测试留痕支撑，整体仍draft。
- 本机Web3000、API8000、SMTP1025/邮箱8025、fakeredis6379；PG代理5432→内部PGlite5433。全部loopback。
- 当前浏览器保留/settings的合成测试账号页面；正式生产入口继续关闭。

## Next actions

- 按进度表推进PBI-0006/0007题目输入与识别确认，同时补PBI-0005日限额，再接PBI-0008引导引擎；内容安全、AI标识及效果埋点随真实会话接入。
- 下一会话读取docs/delivery/status.md、本检查点，以及所选PBI及其引用的UX/技术设计；不要重扫docs或重读本会话聊天。
- 正式协议/check_text/真实PG与Redis及DirectMail验收、学习会话历史快照仍需独立证据；不要将测试同意当正式授权。

## Blockers

- ADR-001/002仍待GB，分别影响真实变式运行与内测发布访问边界。
- 真实云服务、正式协议和内容安全尚未交付；本轮无G4或发布决定。
- 当前真实会话与历史页面未实现，级别快照只有合同测试，不能算完整历史集成通过。

## Open questions

- 组件仓远端与分支保护仍未配置；本机CI配置没有远程执行证据。
- 分享/获客/邀请码按Backlog暂缓，PRD旧口径后续统一。

## Changed artifacts/files

- API代码/迁移/夹具/测试见87f81b4；Web页面/样式/路由/客户端/测试见851bfc2。
- docs/features/PBI-0002、0006、0012、0014、0024.yaml；pbi-0002-profile-implementation.md；账号/讲题/模考UX的PC优先补记。
- docs/tasks/TASK-0005/0006/0007/0008.yaml；docs/product/prd/05-nfr.md；.agent/local/project-context.md。
- docs/delivery/development-progress.md、component-repositories.md、status.md、G3记录、本检查点；本轮验证记录与PC截图。

## Last commit

- API87f81b4；Web851bfc2；交付仓此前fc8ac0d，本轮交付制品另行保存提交。

## 本机恢复

使用交付仓.cache/tools/uv/uv.exe或API .venv/Scripts/python.exe；开发依赖脚本仍在交付仓.cache/dev-services/，不是生产代码。
API启动时显式设LEGAL_DOCUMENTS_DIR=E:/AIworkspacke/gesp-tutor-api/tests/fixtures/legal及APP_ENV=local，生产禁止用此夹具。随机AUTH_SECRET只在进程内生成；不记录或提交。
先运行alembic upgrade head，再启动uvicorn工厂（--app-dir src --host127.0.0.1 --port8000）；Web npm run dev -- --port3000。真实生产配置和代理可信边界须另行验收。
