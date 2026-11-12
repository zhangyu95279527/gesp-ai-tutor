# PBI-0007 重识别资格与结算基础验证 — 2026-11-12

状态：TASK-0018 in-verification，PBI-0007 in-progress；TASK-0016真实集成仍draft，无G4或发布。

## 决策、代码与环境

- 用户明确选择“识别失败不扣次（采用预留后结算）”；已同步PRD、PBI-0005/0007及特性设计。首次免费资格按放行尝试计，首次失败不重赠；后续预留成功回显才扣，失败/中断释放。普通讲解失败不退规则不变。
- API：E:/AIworkspacke/gesp-tutor-api，task-0018-reidentify-lifecycle / 450a06b，承接2e009fa。CPython3.12.16，锁文件未改变。
- 首次迁移连接超时；只读检查确认5432/5433无监听及原PG脚本进程。使用原.cache/dev-services/start-postgres.mjs及原pgdata目录隐藏启动，未删除/重建数据。恢复后沿用5432代理→PGlite5433；脚本只监听回环。日志在忽略目录.cache/dev-services/postgres-task0018*.log。
- Redis使用独立fakeredis/Lua，识别产物为明确合成夹具。真实readiness默认False，无HTTP/真实模型或前端变更。8000服务未重启；不声称已部署新能力。

## 命令与结果

在API仓，配置本机INTEGRATION_DATABASE_URL与DATABASE_URL（PG协议5432，sslmode=disable、connect_timeout=5），执行：

```powershell
.venv/Scripts/python.exe -m alembic upgrade head
.venv/Scripts/python.exe -m pytest tests/test_reidentify.py -q
.venv/Scripts/ruff.exe check src tests migrations
.venv/Scripts/mypy.exe src
.venv/Scripts/python.exe -m pytest -q
.venv/Scripts/python.exe -m alembic current
```

捕获输出：

```text
18 passed in 3.21s
All checks passed!
Success: no issues found in 33 source files
........................................................................ [ 40%]
........................................................................ [ 80%]
..................................                                       [100%]
178 passed in 9.35s
0006_reidentify (head)
```

新增tests/test_reidentify.py18项，完整178项无skip，git diff --check通过。没有远程CI或生产PG/Redis/识别服务验证。

## 合同证据

来源：API仓tests/test_reidentify.py；随机owner/会话、测试后清理对应PG数据，fakeredis互相隔离。

- 首次免费：即使daily_limit=0仍可认领首次免费（独立资源预算仍由后续readiness负责）；ordinal来自PG，客户端传ordinal被拒绝。默认识别未就绪503不增count/revision。
- 同键重放：跨上海日期、清空Redis、重建服务后返回原operation_id/ordinal，不重赠；换expected_revision复用键409，非本人404、旧版本409，无额外认领。
- 活动互斥：admitted/running存在时，新edit/confirm/重识别拒绝。所有入口先锁session；数据库另有单活动唯一索引兜底。4线程6个同键请求只认领1次，执行认领仅1次成功。
- 发布：只有running可提交VL结果；同结果重复发布重放，不重复结算。当前questions/draft_echo更新为新识别，旧AI判定与纠正候选存于input_snapshot；仍pending_confirm、final_level=NULL，创建快照保持3级。
- 失败：首次失败/中断保留旧回显，免费资格不重赠；跨日/清缓存后第二次ordinal2仍需预留。运行任务不自动重领，已成功任务不能再标失败。
- 预留：第二次起used0/reserved1；成功发布后used1/reserved0；失败后used0/reserved0。中断跨午夜释放回原账期，新账期不再扣。
- 拒绝：配置0拒绝第二次，PG count/revision/回显完全不变；配置恢复后同键仍原拒绝，新键再次申请仍ordinal2。
- 幂等释放：同一失败重放不重复释放，后续第三次预留保持reserved1，不被旧失败重放误清。
- 故障注入：预留Lua后抛异常，PG计数/业务记录/账本回滚，usage从账本修复Redis，再尝试仍ordinal2。发布时提交额度Lua后抛异常，PG回显及结算回滚，usage恢复used0/reserved1，重试成功只正式扣1次。
- 旧consume重识别被显式拒绝，避免绕过失败不计次政策；普通确认/限额及其他既有160项测试仍通过。

PGlite代理会串行处理完整连接，多线程证据不等于生产PG并行容量或锁压力测试。进程中断通过明确worker终态模拟，未实际kill执行进程；无自动恢复扫描器。无安全/模型效果评估或PC错误提示验收。

## 完整AC差距

| AC | 本轮基础证据 | 完整验收状态 |
|---|---|---|
| 1 教学级别/首次免费不重赠 | PG ordinal、跨日/清缓存/重建服务不重赠；已有final_level合同回归 | blocked：真实后续讲解适配及进程恢复未验 |
| 2 可编辑回显/确认后讲解 | VL产物更新待确认，原快照保留，活动互斥 | blocked：PC回显及真实L1未接入 |
| 3 confirm计次/超限不推进 | 原确认全回归通过，活动重识别阻止新confirm | blocked：真实公开confirm/SSE/预算未验 |
| 4 同会话重识别 | 持久认领→单次执行→再次回显，状态仍待确认 | blocked：真实VL及UI未接入 |
| 5 首次免费/后续成功计次 | 预留提交/释放与幂等、跨午夜合同通过 | blocked：真实请求/用量UI/生产基础设施未验 |
| 6 失败提示/重试入口 | 失败保留旧回显和显式终态 | blocked：真实识别失败及PC重试提示未接入 |
| 7 识别失败不计次 | 失败/中断释放预留，used0，旧失败重放不误释放新预留 | blocked：实际模型/安全失败与恢复未验 |
| 8 纠正留痕 | 既有corrections保留、操作快照留存输入候选 | blocked：真实UI纠正提交/安全未接入 |
| 9 route/confidence | 强制VL、保存新产物及操作历史 | blocked：真实识别管线/指标未验 |
| 10 考纲外提示 | 既有确认规则回归通过 | blocked：真实判定/PC提示与持续标注未验 |
| 11 P75首字≤5秒 | 无真实生成 | blocked：性能统计未执行 |

DoD：本机代码检查、迁移、全回归及文档完成；完整AC、真实E2E、AI/安全有效性、生产恢复和发布未完成。预留没有TTL退款，恢复需核实任务后显式publish/fail；坏结果校验异常须编排显式归类失败，不将未检查结果发布。新快照/产物的保留与注销删除仍待集成，数据库降级未执行。
