# Checkpoint — TASK-0026 会话内追问

## Completed

- PBI-0009独立切片G3/任务/设计登记。
- 追问操作与解锁共享活动互斥、计次事务/幂等/期限，用户问题与已检答案持久化，不升级阶梯。
- 历史/阶梯仅统计ladder正文，追问不误升级；输入/答案角色与消息seq统一存储。
- 会话与历史追问面板、草稿、失败提示、完成态SSE复用/GET恢复与已保存问答回看已编码。

## Verified

- API ruff/mypy41源文件、269项全回归；Web lint/typecheck、141项测试和生产build通过。
- 无追问数据时0010→0009→head验证通过，原听懂/L1未丢。PC回看/状态重读保留草稿、刷新恢复已保存问答、L1深度保持已查。
- QA题目/回答明确合成、并非模型回复；本轮没有真实生成能力验收，详见PBI-0009-followup.md。

## Current state

- API task-0026-session-followup / 4d5f979；Web同名分支 / 128ae59。全量SHA见current-work.json。
- 迁移0010_followup(head)。本机8000 API/3000 Web已重启，开发Redis/SMTP仍可用；上一轮QA账号/会话含一轮明确开发验证追问。
- PBI-0009 in-progress，TASK-0026 in-verification；开始编码9/26，完整G4仍0。
- 公开followups POST默认503，GET可回看已保存内容；正式模型/安全/预算未配置。
- 按workspace-sync同步任务与固定chore-mac-mini-handoff快照，远端核验以收尾命令输出为准。

## Next actions

- TASK-0021真实装配使用FollowupService/Worker及LadderAdmissionService：输入/输出/答案边界、安全资源预算、真实模型与供应商取消必须全部就绪才开放。
- 共用运行中SSE补发跟随/执行生命周期、用量即时刷新与PC真实输入→讲解→追问/重试/历史全链路仍待联调。
- 继续PBI-0010变式检验基础（运行校验受ADR约束）或错因诊断三件套输入；真实依赖按用户约定稍后配置。
- 更早追问分页/长期完整回看在现有最近20轮之外仍待补齐；当前上下文最近10条，禁止带原图。
- 新电脑拉快照、读取current-work并迁移到0010；不复制本机QA数据库/密钥。

## Blockers

真实模型/对象存储/OCR/正式安全未配置；变式校验ADR待GB。无本轮需用户回复的独立基础阻塞。

## Open questions

真实输出边界/盲评/预算和生产并发/运行中SSE/性能、Mac验证仍未通过。

## Changed artifacts/files

- API followup/followup_worker、0010迁移、ladder/recovery/history/ops/routes兼容、21项测试及AGENTS。
- Web追问客户端/面板/CSS、阶梯/历史接入、共用consume导出、15项测试与AGENTS。
- 交付仓任务/设计/G3/证据/截图、进度/状态/current-work与本检查点。

## Last commit

API4d5f979、Web128ae59；交付仓以本检查点所在提交为准，未合main/未发布。
