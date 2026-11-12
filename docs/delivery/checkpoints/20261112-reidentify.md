# Checkpoint — TASK-0018 重识别资格与结算

## Completed

- 用户确认“重识别失败不扣次，预留后结算”。已同步PRD/PBI/特性设计；普通讲解失败不退规则不变。
- PG持久认领ordinal：首次免费；后续reserve→成功已检VL回显commit/失败中断release。免费资格按放行尝试消耗，不因失败/日期/缓存清理重赠。
- ReidentifyService/Worker、活动互斥、单次认领、操作快照/终态及迁移0006已实现；新edit/confirm在重识别活动中拒绝。没有HTTP/真实模型或UI接入。

## Verified

- 专项18项、完整178项全部执行通过；ruff及mypy33源文件通过；0006_reidentify(head)。
- 预留/发布阶段Lua后PG故障回滚、账本重建、失败幂等释放、跨午夜释放及免费资格持久化已测。证据见docs/verification/PBI-0007-reidentify.md。
- 本机PG原已停止；恢复原start-postgres.mjs/pgdata，未重建数据。仍为回环PGlite开发代理及fakeredis，不是生产PG/Redis或真实识别验收。

## Current state

- API task-0018-reidentify-lifecycle / 450a06b，承接2e009fa；Web仍8d4ce81。未合main/推送。
- TASK-0018 in-verification；PBI-0007 in-progress；6/26 PBI开始编码，G4仍0。
- PG5432→5433服务已恢复；8000未重启。新类未装配，recognition_ready默认False；Web/session仍本地预览。
- 第二次起额度以原受理日预留/结算，不能先consume或根据客户端ordinal发免费。running不能自动重跑，恢复须核实后显式终态结算。

## Next actions

- 真实服务尚未配置时，可继续独立资源预算/频率保护基础；真实readiness必须覆盖模型/安全/预算/持久执行者，不能使用测试lambda True代替。
- TASK-0013/0016接私有上传/安全/OCR/VL、PC回显/纠正/重试、confirm/SSE及真实L1和终态恢复。完整回显/讲解链路仍未交付。
- 自动恢复扫描、实际进程kill/提交丢ack、生产PG/Redis并行、指标与跨存储保留/删除仍待验证。

## Blockers

模型/对象存储/OCR/安全未配置；ADR-001/002仍待GB。本轮计次口径已获用户明确决定，没有待回复问题。

## Open questions

真实资源预算配置与服务接入时间仍待后续；本轮无阻塞问题。任何未检查/无效识别输出须显式失败释放，不能发布；悬挂预留不可按TTL自动退款。

## Changed artifacts/files

- API reidentify*、locks、store/confirmation活动保护、lmt共享事务预留/结算、迁移0006、test_reidentify、README/AGENTS，详见450a06b。
- 交付仓TASK-0018与0016依赖、重识别设计/验证、PRD/PBI-0005/0007/特性设计及限定G3、整体进度/组件登记/本检查点。

## Last commit

API450a06b；交付制品同批本地提交，ID由git log查询。未发布。
