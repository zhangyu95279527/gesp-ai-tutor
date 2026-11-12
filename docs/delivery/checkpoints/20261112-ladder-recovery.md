# Checkpoint — TASK-0023 阶梯恢复与显式重试

## Completed

- 新增持久期限、L1重试关联、到期扫描与本人读取惰性恢复，旧执行期限守卫；不自动生成/退费。
- L1内部显式重试共享额度事务、同键语义与活动互斥；公开retry-l1仍503。
- PC持久操作状态提示；刷新后的L2/L3失败重试仍要求勾选新计次，L1未配置禁用。
- 独立切片设计、TASK-0023、限定G3及证据已登记。

## Verified

- API ruff/mypy37源文件、227项回归通过；Web lint/typecheck、109项测试与生产build通过。
- 新增API18/Web14测试，迁移0008→0007→head及18项复验通过；未删现有业务数据。
- HTTP为ASGI+本机PG协议，UI为SSR/合同验证。本轮未进行浏览器实测，未启动/重启API8000或Web服务。

## Current state

- API task-0023-ladder-recovery / d87f315；Web同名分支 / 9d0ec44，本地提交、工作区干净，未合main/推送。
- 迁移0008_ladder_deadline(head)，整操作期限为受理后120秒；扫描每10秒最多50条。
- TASK-0023 in-verification，TASK-0021仍draft；PBI-0008 in-progress，完整G4仍0。
- 生产模型/安全/预算未装配，公开生成入口继续503不扣次。

## Next actions

- TASK-0021装配真实模型/安全与资源预算/成本结算、供应商取消；不要仅设置ready=True就开放。
- 原confirm已扣次但未attach_l1的孤立确认记录仍需统一恢复/受理；新生成生命周期要保证退出/取消时写入终态。
- 接通公开retry-l1、confirm/unlock后，完成运行中SSE补发再跟随及PC真实输入→确认→L1/L2/L3→失败/刷新重试链路。
- 后续推进追问/听懂/历史；保持未配置的真实依赖与可独立推进的基础能力分别记录。

## Blockers

真实模型/对象存储/OCR/正式安全未配置，依既有用户约定稍后接入；ADR-001/002仍待GB。

## Open questions

无本轮需用户回复问题。硬期限选值需真实性能验证；供应商超时/取消、正式PG竞争及进程kill恢复仍待验收。

## Changed artifacts/files

- API app、ladder、ladder_recovery、session_routes、0008迁移、恢复测试、AGENTS，见d87f315。
- Web ladder-client/LadderSession/OperationNotice、恢复测试、AGENTS，见9d0ec44。
- 交付仓TASK-0023/0021、PBI-0008、恢复设计/G3/验证、组件登记/进度/status与本检查点。

## Last commit

APId87f315、Web9d0ec44；交付制品同批本地任务分支提交，提交号由git log查询。未发布。
