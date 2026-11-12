# PBI-0007 PC回显与接口接入

Status: approved
日期：2026-11-12；TASK-0019。将既有内部会话基础接到可操作PC页面，不启用未配置的识别/生成。

- GET /api/tut/sessions/{id}读取本人会话的session_id/state/revision/level_snapshot/reidentify_count/final_level/out_of_syllabus/echo/capabilities；不返回存储key、OCR路径、原始代码、内部操作账本或其他账号内容。缺失/非法/非本人统一404。
- POST /api/tut/sessions/{id}/echo要求现有同源写保护、登录、幂等键，接收三字段及expected_revision，经SessionStore.edit持久保存纠正。修改能力可独立于模型；能力关闭/生产缺文本安全检查时拒绝提交，不能绕过内容安全。开发仅允许显式local模式验证。
- confirm/reidentify路由校验请求及本人归属，当前返回503 generation_unavailable/recognition_unavailable；capabilities显式返回false，前端禁用并解释。不触及额度或伪造生成成功。
- /session?id=...读取并展示回显/状态。AI展示仍经AiContent，用户修正表单单独输入（空白保留现值，清空考点需显式勾选），不更改AiContent子节点/隐藏契约。展示创建级别与本次候选级别，0级提示考纲外。保存只写纠正，不算正式确认或扣次。
- 加载/失败/401/404/冲突/保存重试有明确恢复入口。写请求同一payload重试复用键；更改payload使用新键，expected_revision防覆盖。失败保留用户修正，不因读取失败伪造内容。
- 输入页在本地预览后可尝试提交文字识别；当前API返回未配置错误时保留原文/代码/疑问。图片签名/直传仍待TASK-0013，当前只提示服务未开放，不制造对象key。
- 新增仅开发环境/dev/session-review，明显标注合成样例、仅本页交互，不是真实识别/不写数据库；用于PC表单和错误分支验证，生产404。样例不混入正常入口、不产生答案或假讲解。
- 当前没有L1/L2/L3/追问/历史交付，不以回显页面代替完整讲题。TASK-0016继续承担真实服务与全链路。

停止条件：API鉴权/隔离/写保护/纠正落库与冲突/未配置拒绝测试通过，Web client与表单合同/构建通过，并保存PC浏览器证据；真实识别、SSE与PC完整AC仍未通过。
