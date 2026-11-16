# Checkpoint — TASK-0032 诊断修正阶梯

## Completed

- PBI-0016 AC1切片设计/G3/Task登记；共享阶梯类型与验证钩子、冻结上下文、三级持久编排及PC本人回看实现。
- L1包含在首次诊断，L2/L3各1次；诊断与修正内容分离，未检/未完成不展示，真实新生成仍关闭。

## Verified

- API421项、ruff/mypy55源文件；Web271项、lint/typecheck/build通过。
- 0013往返保留旧记录，有引导后降级保护；PC历史→三级引导→重读/刷新通过，见PBI-0016-guidance.md及截图。
- PG诊断消费1、unlock2、原追问1/讲题1不变；原诊断1/引导3/steps3，反馈solved/version2保留。

## Current state

- 三仓task-0032-diagnosis-guidance；API 7c5fa29803f8850b66d87d126ecccd6958f097df、Web 387772b1def66f808fbd22fa12062bd3f2d2e393；0013_guidance(head)。TASK-0032 in-verification，完整G4仍0，已开始12/26。
- API8000/Web3000已重启，Redis/SMTP保留；浏览器只读持久开发占位，不代表真实质量。读取不生成/扣次。
- 使用workspace-sync同步任务与chore-mac-mini-handoff；最终远端核验以收尾执行输出为准。

## Next actions

- 推进诊断继续追问：冻结当前修正阶梯与级别，复用共享互斥/计次；补输入材料回看和真实创建确认闭环。
- 真实供应商/安全/语义边界/预算装配后才开放生成并做盲评；补SSE/取消、L1付费重试和变式检验。
- Mac从固定快照拉三仓，按手册重建依赖并迁移0013，不复制Windows缓存或本机QA库。

## Blockers

真实模型/OCR/存储/安全/预算尚未配置；变式ADR待GB。无本轮需要用户立即回复的基础开发阻塞。

## Open questions

真实分层语义与诊断一致性/盲评、生产性能及Mac/移动实机验证未完成。

## Changed artifacts/files

- API core/session/ladder、dia/guidance三文件与路由、ops事件、0013迁移、36项专项与AGENTS。
- Web引导组件/客户端/样式、诊断卡片入口整合、引用验证复用、23项专项与旧测试更新、AGENTS。
- 交付Task/PBI/设计/G3、验证与截图、current-work/派生状态/进度、组件/Mac记录及本检查点。

## Last commit

API 7c5fa29803f8850b66d87d126ecccd6958f097df、Web 387772b1def66f808fbd22fa12062bd3f2d2e393；交付仓以本文件所在提交为准，未合main、未发布。
