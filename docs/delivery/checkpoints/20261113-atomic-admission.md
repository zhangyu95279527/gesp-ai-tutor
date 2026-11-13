# Checkpoint — TASK-0024 原子确认与持续同步

## Completed

- LadderAdmissionService在同一事务提交冻结级别/确认扣次/L1操作/steps，旧确认执行权交给阶梯。
- 过期旧孤立确认恢复为同ID中断操作，保留原时间，不自动生成或退费；与阶梯过期共用批次上限。
- 跨平台workspace-sync.py、current-work.json与每轮同步约定已落库。固定换机分支仅快进到完成进度。

## Verified

- API ruff、mypy38源文件、237项全回归通过；同步脚本7项临时Git仓测试通过。
- Web无变化，沿用c20356f；本轮不重复运行或宣称109项历史测试为新证据。
- 三仓推送及远端SHA需由本轮收尾脚本核对；失败时不得声称可完整换机。具体证据见docs/verification/PBI-0008-atomic-admission.md。

## Current state

- API task-0024-atomic-admission / c65dccb；Web chore-mac-mini-handoff / c20356f。交付仓task-0024-atomic-admission，提交以current-work.json所在提交为准。
- 固定远端换机分支仍chore-mac-mini-handoff，将与各仓最新完成提交同步。新电脑按该分支克隆/拉取，工作清单以current-work.json为准。
- 无新迁移，仍0008_ladder_deadline；API8000/Web没有启动或重启，无新浏览器/真实生成验证。
- TASK-0024 in-verification；PBI-0008 in-progress，完整G4仍0。公开生成入口仍关闭。

## Next actions

- TASK-0021真实装配时使用LadderAdmissionService，禁止恢复旧confirm提交后再attach的组合；原ConfirmationService保留兼容，但不作为新生成入口。
- 实现模型/正式安全/资源预算/失败成本，接入confirm/unlock/显式retry-l1与生命周期；供应商取消、实时SSE补发跟随和PC真实端到端仍待完成。
- 可独立推进追问/听懂/历史；真实服务按用户约定稍后配置，不以测试替身声称已交付。
- 每轮先fetch检查，再开发/验证/提交，更新current-work与检查点，运行workspace-sync.py --push。当前Windows可显式使用已有代理；Mac不继承Windows代理配置。

## Blockers

模型/对象存储/OCR/正式安全未配置，ADR-001/002待GB；不阻止独立基础开发。Mac/ARM验证仍需新机。

## Open questions

无本轮需用户回复问题。正式PG竞争、真实模型与安全/性能、跨电脑未完成工作协调仍需实际环境证据。

## Changed artifacts/files

- API ladder_admission、ladder_recovery、10项测试与AGENTS，见c65dccb。
- 交付仓同步脚本/7项测试、current-work、任务/设计/G3/验证、进度/组件登记/状态与本检查点；项目上下文保存持续同步授权。

## Last commit

APIc65dccb、Webc20356f；交付仓以本检查点所在提交为准。未合main、未发布。
