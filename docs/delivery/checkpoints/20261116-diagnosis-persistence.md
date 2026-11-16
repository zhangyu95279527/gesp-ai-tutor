# Checkpoint — TASK-0029 诊断共享持久编排

## Completed

- 扩展PBI-0015设计/G3和任务，复用共享会话与确认事务，不另建状态机。
- dia类型/材料、识别纠正留痕、1次诊断计费、冻结确认revision/文本、检查后持久消息与期限恢复已实现。
- 本人GET和PC只读回看/刷新、tut/dia类型隔离已实现；新建/确认HTTP继续关闭。

## Verified

- API ruff/mypy50源文件、346项全回归；Web lint/typecheck、203项及生产build通过。
- 无dia数据时0011→0010→head往返，原1会话/3消息/5事件保留；加入合成QA后降级被保护拒绝，仍0011。
- PC本人真实GET、重新读取、整页刷新恢复通过；PG核对诊断仅扣1次、消息1/阶梯steps0。详情见PBI-0015-persistence.md。

## Current state

- API task-0029-diagnosis-persistence / 7771c44；Web同名分支 / e8fa8ef，完整SHA见current-work.json。
- 数据库0011_diagnosis(head)。本机8000/3000已重启，Redis/SMTP保留；QA诊断明确为合成记录。
- TASK-0029 in-verification，PBI-0015 in-progress；已开始11/26，G4完整验收仍0。
- 公开GET本人只读可用；新建/确认/纠正POST仍503，正式OCR/模型/安全/预算未装配。前端生产新诊断关闭。
- 三仓任务与chore-mac-mini-handoff快照按workspace-sync同步，收尾核验以工具输出为准。

## Next actions

- 推进PBI-0016引导修正与解决状态基础：复用共享操作/消息，区分诊断结果与修正阶梯，不把诊断当L1；状态回填及幂等留痕可独立验。
- 补PC诊断回显/纠正表单、识别/确认入口与诊断历史列表；真实服务齐备后才放开创建/确认，不用测试识别替代。
- 真实OCR/存储/输入输出安全/模型/语义检查/预算配置后，完成至少20例重复一致性、盲评与PC真实全链路。
- TASK-0021实时SSE/取消/预算和讲题追问联调仍待；Mac mini从快照拉三仓并迁移0011、重新回归，不复制Windows依赖或QA数据库。

## Blockers

真实供应商与正式安全未配置；变式运行ADR待GB。无需要用户立即回复的内部基础阻塞。

## Open questions

正式PG竞争/性能、真实诊断质量/安全/一致性、PC创建确认闭环及Mac/移动验收未完成。

## Changed artifacts/files

- API 0011迁移、共享类型/事务钩子、诊断session/admission/operations/worker/routes、恢复装配、22项测试及AGENTS。
- Web诊断读取客户端/Reader、id入口、20项测试及AGENTS。
- 交付仓Task/设计/G3/证据截图、current-work/状态/进度/组件记录、Mac手册与本检查点。

## Last commit

API7771c44、Webe8fa8ef；交付仓以本检查点所在提交为准，未合main/未发布。
