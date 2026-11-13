# Checkpoint — TASK-0025 历史与听懂

## Completed

- PBI-0011独立历史/标记切片精炼、G3及TASK-0025登记。
- 本人历史keyset分页、字面搜索/已听懂筛选、只读已发布阶梯回看、创建与最终级别分别展示。
- 听懂首次时间持久化、并发幂等、唯一事件及每日取数；不扣额度、不生成，不伪造变式/追问。
- PC历史页面与正常阶梯听懂入口接真实HTTP，AI正文经AiContent。

## Verified

- API ruff/mypy39源文件、248项全回归通过；Web lint/typecheck、126项测试与生产build通过。
- 迁移0009→0008→head在无标记数据时验证通过；之后浏览器QA标记已保存，不得为回退丢掉反馈。
- PC真实登录/搜索/空筛选/回看/点击听懂/刷新保持/列表筛选通过；PG证据仍1条确认扣次、1条听懂事件。正文为明确合成QA数据，不是真实模型。

## Current state

- API task-0025-history-understood / 151f471；Web同名分支 / aac2957。全量SHA见current-work.json。
- 迁移0009_understood(head)；本机前端3000、API8000、开发Redis6379/SMTP1025/邮箱8025已运行。浏览器保留/history便于用户查看。
- TASK-0025 in-verification，PBI-0011 in-progress；开始编码8/26 PBI，完整G4仍0。
- 三仓按workspace-sync推送任务与固定换机快照，远端核验以本轮收尾命令输出为准。

## Next actions

- 继续PBI-0009会话内追问；复用冻结final_level/当前阶梯及日额度，每次追问计1次，断线GET续接不重POST。
- TASK-0021仍负责真实模型/安全/预算与新原子入口/重试接入、供应商取消、实时SSE和PC真实讲题全链路。
- PBI-0010变式结果接入后补历史展示与已定稿“变式待复习”筛选；当前该筛选明确禁用，不编造状态。
- 其他电脑先拉取快照并读current-work.json，新机迁移到0009；开发数据库与测试账号不随Git迁移。

## Blockers

真实模型/对象存储/OCR/正式安全稍后配置；变式运行校验ADR待GB。没有本轮需用户回复的阻塞。

## Open questions

完整变式/追问AC、正式PG并发、真实内容安全与Mac/移动专项仍待后续证据。

## Changed artifacts/files

- API history仓储、understood迁移、session_routes/ops.events、11项测试及AGENTS。
- Web history客户端/页面/CSS、听懂组件/阶梯入口、17项测试及AGENTS。
- 交付仓任务/设计/G3/验证/截图、进度/组件登记/状态、current-work及本检查点。

## Last commit

API151f471、Webaac2957；交付仓以本检查点所在提交为准。未合main、未发布。
