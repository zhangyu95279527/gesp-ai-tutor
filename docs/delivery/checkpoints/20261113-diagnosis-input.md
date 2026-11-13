# Checkpoint — TASK-0027 诊断三件套输入

## Completed

- PBI-0014输入基础切片设计、G3及任务登记，PC诊断入口/三材料区/本地核对预览已编码。
- UTF-8代码文件导入、5001字符全文保留并阻止继续、原输入保留与裁剪风险提示已实现。
- 服务端严格合同、本人图片实际字节/安全检查与关闭的POST入口已实现；无诊断生成/扣次。

## Verified

- API ruff/mypy45源文件，287项全回归；Web lint/typecheck、156项测试和生产build通过。
- PC缺项、5001粘贴/文件、非法UTF-8保留原代码、评测截图本地预览、手填状态与修改后撤下旧预览已查。
- 明确未上传/未OCR，开始识别禁用；详见PBI-0014-input.md及TASK-0027截图。

## Current state

- API task-0027-diagnosis-input / 80d3798；Web同名分支 / dbcec3e，完整SHA见current-work.json。
- 迁移仍0010_followup(head)，本机3000/8000已重启，开发Redis/SMTP保留。
- TASK-0027 in-verification；PBI-0014 in-progress；已开始10/26，完整G4仍0。
- 新诊断开发页面仅本地输入，生产表单关闭；POST默认503，不写会话/额度。
- 三仓任务与chore-mac-mini-handoff快照同步，最终远端状态以workspace-sync输出为准。

## Next actions

- 继续PBI-0015六类错因结果的严格合同/已检持久化/PC展示基础，遵循定稿设计；真实模型未配置时保持关闭，不造诊断答案。
- 待真实存储/OCR/安全就绪，补三件套即贴即传、可纠正识别回显与状态识别用例，再装配诊断生成。
- TASK-0021真实模型/安全/答案边界/资源预算、供应商取消、运行中SSE、PC讲题/追问全链路仍需接入。
- Mac mini拉取三仓快照，按手册重建依赖、迁移到0010并回归；不要复制Windows虚拟环境、QA数据库或密钥。

## Blockers

真实模型/对象存储/OCR/正式安全未配置；变式运行ADR待GB。无需要用户立即回复的输入基础阻塞。

## Open questions

完整上传/状态识别/诊断输出质量、正式PG并发/性能、Mac和移动基础操作未验；本地草稿刷新清空。

## Changed artifacts/files

- API dia合同/准备服务/路由、app安装、18项专项测试及AGENTS。
- Web诊断页面/组件/CSS/导入校验、讲题/历史导航、dia代理、15项测试与AGENTS。
- 交付仓PBI/Task/设计/G3/证据截图、进度/状态、current-work、换机手册与本检查点。

## Last commit

API80d3798、Webdbcec3e；交付仓以本检查点所在提交为准，未合main/未发布。
