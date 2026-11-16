# Checkpoint — TASK-0031 诊断历史列表

## Completed

- 诊断历史设计/G3及Task登记，PBI-0011与PBI-0016保持进行中。
- 本人已受理诊断分页、稳定时间排序、完整题干字面搜索/最终反馈筛选与已检类别摘要已实现。
- PC历史列表、讲题/诊断导航、条目进入持久回看与空态已实现；未回填单独呈现。

## Verified

- API ruff/mypy52源文件、385项全回归；补强隔离场景后专项21项通过。Web lint/typecheck、248项与生产build通过。
- PC导航→列表→筛选/搜索→原诊断回看→列表刷新通过；原反馈solved/version2、消费diagnosis1/追问1/讲题1、诊断正文1/steps0保持。
- 浏览器仅一条持久QA，分页由API五条同时间记录与客户端去重测试覆盖；见PBI-0011-diagnosis-history.md及截图。

## Current state

- API task-0031-diagnosis-history / 998f63f；Web同名分支 / 299d4c8，完整SHA见current-work.json。
- 无新迁移，仍0012_resolution(head)；8000/3000已重启，开发Redis/SMTP保留。
- TASK-0031 in-verification；已开始12/26，完整G4仍0。新建/确认/修正/诊断追问/变式仍未开放。
- `/history?type=diagnosis`列出本人已受理诊断；`/diagnosis?id=...`读取原结果与反馈。查询/刷新不生成、不扣次。
- 三仓任务和chore-mac-mini-handoff快照按workspace-sync同步，最终核验以收尾输出为准。

## Next actions

- 推进诊断修正阶梯基础，复用操作锁/期限/计次；诊断结果不是L1，引导内容遵守L1自查/L2定位/L3修正要点，不给完整改后代码。
- 诊断继续追问需冻结当前修正阶梯与级别并复用计次；变式运行按既定ADR与校验能力推进。
- 补真实识别/回显确认与输入材料回看，供应商/安全/预算齐备才开放创建确认；补真实一致性/盲评及PC全链路。
- Mac mini从固定快照拉三仓，按手册重建依赖并迁移0012，不复制Windows缓存或QA数据库。

## Blockers

真实模型/OCR/存储/安全/预算尚未配置，变式校验ADR待GB；无本轮需用户立即回复的列表基础阻塞。

## Open questions

真实生成/修正内容边界、追问/变式、生产PG性能与Mac/移动验证未完成；筛选不提供跨页不可变快照。

## Changed artifacts/files

- API dia/history与路由、21项测试、AGENTS。
- Web诊断历史组件/客户端/样式、历史type入口与跨页导航、25项测试、AGENTS。
- 交付仓Task/设计/G3/PBI引用、验证截图、current-work/状态/进度、组件与Mac记录及本检查点。

## Last commit

API998f63f、Web299d4c8；交付仓以本检查点所在提交为准，未合main/未发布。
