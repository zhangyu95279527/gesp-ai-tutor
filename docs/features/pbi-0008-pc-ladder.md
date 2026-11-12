# PBI-0008 PC阶梯与流式消费切片

Status: approved
日期：2026-11-12；TASK-0020，独立客户端/关闭服务合同；真实引擎由TASK-0021实现。

- 本人GET /api/tut/sessions/{id}/ladder返回阶梯快照。当前无session_steps或已发布讲解，诚实返回level0/steps空/unlock=false；POST unlock校验本人/幂等键/target2或3，固定503 generation_unavailable，不扣次。
- PC页面有L1/L2/L3卡片、当前层级、逐级手动解锁及已完成记录；只有成功done才把候选升级为已完成，流式片段/失败/安全中断不升级。不能跳级，不自动解锁。
- SSE使用fetch+ReadableStream。事件id为递增正整数；meta绑定operation_id/message_id/ladder_level/prompt_version，并声明checks.safety与checks.ladder均passed。客户端只接受已声明检查通过的流，不将其结构校验冒充实际安全/答案边界检查。实际服务端必须先检查再发，未就绪不开放。
- done必须携带非负数字usage及有效ISO completed_at，后者用于显示服务端已完成记录；真实服务应在持久发布成功后再发done。活跃操作存在时快照can_unlock必须false；取不到operation_id的断线只能重新读取，不得自动重发POST。协议错误不等于已确认生成失败，不提供新计次重试，须先读状态。
- 支持UTF-8跨字节、CRLF跨分片、注释/多行data；未知事件/坏JSON/未检meta/先chunk/错误层级/过大数据拒绝，不发布违规帧。AiContent负责所有AI正文标识。
- 终态done、安全截断safety_truncated、error分开。连接在终态前结束视为disconnected，保留已检部分并标未完成；已知operation_id可GET /api/tut/operations/{id}/events?after=cursor续接，禁止重发POST或新键自动扣次。未取得operation_id时提示重新读取状态，不自动重发。
- POST解锁由显式按钮触发且提示消耗1次，target只能当前最高层+1（2/3）。失败后的新生成需再次显式确认计次；续接为原GET不计新次。HTTP429使用现有QuotaExhausted且保留完成卡片，不造历史入口。
- 事件/快照使用checked元数据合同，实际模型答案边界与安全评估仍在服务端。客户端不能靠字符串规则证明L1/L2没有答案。
- 正常/session?id在l1_pending接入阶梯页面，真实接口目前仅显示等待和不可用。开发/dev/ladder明确合成占位，不是真实讲解，无可抄答案/真实扣次；生产404。演示可选择正常、断线续接、超限、安全截断和失败。

停止条件：API合同/隔离/无副作用、Web解析器/网络/组件合同与构建通过，PC手动逐级/断线/超限/安全提示实测并落档。完整内容合规、真实输出、持久steps、SSE端到端与性能不宣称通过。
