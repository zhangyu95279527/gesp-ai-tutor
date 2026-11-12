# Checkpoint — TASK-0015 会话与回显持久化

## Completed

- PBI-0007独立持久化基础设计、TASK-0015/0016 DAG及限定G3已落档；仅TASK-0015放行，真实识别任务仍draft。
- API core/session新增models/store；0004_sessions新增ai_sessions/questions/session_operations，保存输入/owner/创建级别、识别产物、draft_echo、逐字段纠正与操作幂等。
- 内部pending_recognition→pending_confirm状态；编辑不等于confirm、不冻结final_level、不扣次、不生成讲解。无新HTTP或前端成功入口。

## Verified

- 本机迁移至0004_sessions(head)。ruff(src/tests/migrations)、mypy27源文件、145测试全通过，无skip；新增会话23项。
- 隔离/重放/冲突、版本控制、原始快照与识别产物保留、逐字段纠正、连接重建恢复及事务异常回滚已验证。证据见docs/verification/PBI-0007-session-foundation.md。
- PGlite排队协议与测试夹具不算生产PG并发或真实模型验收；未kill进程、未部署或远程CI。

## Current state

- API task-0015-session-foundation / 02603a2，承接05370ed；Web仍task-0012-unified-input / 8d4ce81。未合main/推送。
- TASK-0015 in-verification；PBI-0007 in-progress；6/26 PBI开始编码、G4仍0。
- 本机8000未重启；公开tut创建入口仍按缺安全/存储返回503，尚不调用SessionStore；Web/session仍本地输入预览。
- SessionStore只供可信内部编排调用，创建方须认证owner并经ProfileService.get_level_snapshot取得级别，不能采信客户端owner/快照。

## Next actions

- TASK-0013/0016真实依赖就绪后接上传/安全/识别、资源预算/频率保护与公开创建；publish只接已通过安全检查的识别产物。
- confirm与额度/L1持久操作协调仍未交付：final_level冻结、考纲外继续确认、同键恢复和超限不推进必须一起设计，不把edit当confirm。
- 同会话重识别资格须PG认领并联动额度，不按日期/缓存重置；当前只有计数字段，没有免费资格服务。
- 无外部模型时可继续独立confirm/操作状态基础，但须先分任务及明确失败恢复契约，不用合成结果替代真实端到端验收。

## Blockers

真实模型/存储/OCR/安全尚未配置；ADR-001/002仍待GB。基础仓储不依赖这些服务，已完成本轮授权增量。

## Open questions

考点最多20项/每项100字符属于显式结构保护假设；完整保留/账号删除、生产PG并发、进程中断恢复仍待集成验证。无本轮需用户回复的问题。

## Changed artifacts/files

- API core/session/models/store、迁移0004、test_sessions、README/AGENTS，详见02603a2。
- 交付仓PBI-0007、专属基础设计、TASK-0015/0016、限定G3、验证、整体进度/status、组件登记与本检查点。

## Last commit

API02603a2；交付制品同批提交，ID由git log查询。未发布。
