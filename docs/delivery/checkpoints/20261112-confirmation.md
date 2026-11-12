# Checkpoint — TASK-0017 确认受理基础

## Completed

- 内部ConfirmationService、ConfirmInput及ConfirmationWorker已实现；迁移0005增加确认操作表、l1_pending与考纲外标志。
- 通过QuotaService.consume_in_transaction共享PG事务，core不跨模块直写额度表。成功原子冻结final_level/保存纠正/扣1次；超限不推进会话。
- 同键持久重放/冲突、默认生成缺失不扣次、考纲外显式继续、单次worker认领与中断不自动重领/退款。

## Verified

- ruff(src/tests/migrations)、mypy29源文件、160项全回归通过，无skip；新增15项确认测试。迁移0005_confirmation(head)。
- 模拟Lua后PG失败：账本/会话同时回滚，后续重建Redis；模拟提交后丢弃响应跨日重放不再扣；最后一次额度仅一个session放行。
- 测试来自PGlite/fakeredis及合成产物；未执行真实进程kill、生产PG并发、真实模型、安全有效性或远程CI。详见docs/verification/PBI-0007-confirmation.md。

## Current state

- API task-0017-confirmation-admission / 2e009fa，承接02603a2；Web仍8d4ce81。未合main、未推送。
- TASK-0017 in-verification；PBI-0007 in-progress；6/26 PBI开始编码，G4仍0。
- 本机8000未重启。没有新增公开确认入口；新类未装配，generation_ready默认False，Web/session仍本地输入预览，没有真实L1。
- 受理结果只有admitted表示已计次，不表示可再次执行。执行者必须claim_start；running/中断均不可自动重领。l1_pending不等于已发布L1。

## Next actions

- 无外部模型时可推进同会话重识别的PG资格认领与计次基础，先登记任务及故障恢复契约，验证跨日/缓存清空不重赠。
- TASK-0013/0016真实依赖就绪后接安全/上传/识别、回显UI与公开confirm、预算/频率保护、真实worker/SSE、L1已检内容发布及终态恢复。
- 真实readiness必须覆盖模型/安全/预算/持久worker，不能用测试lambda True替代。后续完成态和重新生成流程须避免重复推理/退款，并保持既有失败不退次规则。

## Blockers

模型/对象存储/OCR/安全未配置；ADR-001/002仍待GB。本轮内部基础已完成，真实端到端未交付。

## Open questions

共享事务固定单session→quota owner锁顺序，不能在外层再锁其他session。自动恢复扫描器、真实进程退出/提交丢ack、生产并发与降级仍待集成验证。无本轮需用户回复的问题。

## Changed artifacts/files

- API confirm_contracts/confirmation、models/store、lmt/service、迁移0005、test_confirmation、README/AGENTS，详见2e009fa。
- 交付仓TASK-0017及0016依赖、确认设计、PBI/会话/限额设计、限定G3、验证记录、整体进度/组件登记与本检查点。

## Last commit

API2e009fa；交付制品同批本地提交，ID由git log查询。未发布。
