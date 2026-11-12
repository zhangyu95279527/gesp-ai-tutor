# Checkpoint — TASK-0022 持久阶梯

## Completed

- 从TASK-0021拆出独立TASK-0022，补齐设计、限定G3、依赖及验证记录。
- PG持久操作、受理steps、检查后消息发布、L1确认承接、相邻解锁扣次、失败/中断不退、质量与成功事件已实现。
- 本人ladder GET读取持久正文，完成态events GET按固定游标回放；Web兼容active状态并进入原阶梯页。

## Verified

- API ruff/mypy36源文件、209项全回归通过，无skip；Web lint/typecheck、95项测试、生产build通过。
- 空新增表前置检查后0007降至0006再升head通过，新增19项数据库/HTTP回归通过。没有删除/重建原数据。
- 真实证据及限制见docs/verification/PBI-0008-persistent-ladder.md；ASGI+PG协议测试不是浏览器生成端到端。

## Current state

- API task-0022-ladder-persistence / 20bf1aa；Web同名分支 / 5370b26。工作区已提交，未合main/推送。
- 迁移0007_ladder(head)；公开confirm/unlock仍503不扣次，生产ready默认False；没有真实生成网关装配。
- TASK-0022 in-verification；TASK-0021 draft，依赖本切片；PBI-0008 in-progress；完整G4仍0。
- API8000未启动/重启，Web未重启；本轮未进行浏览器截图或生产页面复验。原有开发数据库继续使用，本轮没有启动新的数据库实例。

## Next actions

- 在TASK-0021复用LadderStore/Worker；装配前必须提供真实安全/边界评估、模型资源预算、调用超时/频率保护与失败成本结算。
- 接通confirm到attach_l1，解锁受理后交给执行生命周期；同会话仅一操作，新POST不得承担断线恢复。
- 完成L1失败的显式新计次重试、超时/进程退出标记与读取恢复。运行中events应补发再跟随，当前只完成态回放。
- PC真实输入→确认→已检L1→手动L2/L3→刷新回看端到端；随后追问/听懂/历史，不以新增协议演示代替真实页面。

## Blockers

真实模型/对象存储/OCR/正式安全未配置；用户约定稍后配置。ADR-001/002待GB。未阻塞本轮独立基础。

## Open questions

无本轮需回复问题。真实内容边界/级别贴合、生产并发/进程恢复与性能仍待验收。

## Changed artifacts/files

- API新增0007迁移、ladder/ladder_worker、test_ladder_engine；更新models/session_routes/ops.events/AGENTS，见20bf1aa。
- Web更新client/SessionReview/AGENTS，新增ladder-persistence.test，见5370b26。
- 交付仓TASK-0022/0021、PBI-0008及切片设计/G3/证据/进度/组件登记/status/本检查点。

## Last commit

API20bf1aa、Web5370b26；交付制品同批本地任务分支提交，ID由git log查询。未发布。
