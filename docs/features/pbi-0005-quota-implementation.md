# PBI-0005 日限额最小实现设计

Status: approved
日期: 2026-11-12
范围：FEAT-005 / PBI-0005；沿用既有PG/Redis/FastAPI边界，不提供公网扣次接口，不实现模型或图片识别。

## 原子与恢复契约

- Redis Lua 检查 used+reserved，执行扣次、预留、提交与释放；默认日限额15，Redis hash quota:config 的 daily_limit 即时控制新放行。缺配置取15，损坏/负数配置拒绝，不默默放大额度。
- PG quota_operations 保存全生命周期幂等账本；quota_usage仅记录正式计次与拒绝，操作ID绑定owner/action/session/重识别序号。网络重试返回原结果，换payload复用ID返回409。跨日重放沿用原账期，不在新日期再扣。
- 每个owner的PG行锁串行化账本与Redis同步窗口。取得owner锁后按上海当前时间决定账期，避免排队跨日误记；进入Lua前从已提交账本重建该日used/reserved，解决Redis丢失及“Lua执行成功但PG事务失败”的计数漂移；Lua仍是原子放行判定点，Redis不可用不绕过。PG提交成功前不向模型调用方返回放行。
- 普通动作受理即正式计次，没有退款接口；LLM失败/中断仍占用。同一operation_id只获一次计次资格，业务引擎须依据replayed与自身操作状态避免重复推理。
- 变式必须reserve→commit/release，不能直接consume。提交已有预留不再检查新额度，释放仅影响未提交预留，已提交不能释放；跨午夜结算回原账期。悬挂预留保留保守占用，不按TTL自动赠送；业务恢复确认“未发布题面”后显式release，确认已发布后幂等commit。
- quota_usage与quota_rejected事件写入都带稳定operation_id。事件由ops模块record接口负责，不跨模块直接写events；事件异常使用保存点回滚事件，不阻断限额决定，实际度量完整性仍待后续运营集成。

## 计次矩阵

计次：session_create、diagnosis_create、unlock、followup、exam_review；reidentify由会话持久化认领后的ordinal决定（首次免费，后续计1）。variant仅走预留。免费注册：judge、wrong_book_browse、wrong_book_repractice（非AI部分）、recognition_failed、invalid_input、input_safety_blocked。

ordinal不得来自客户端；本模块不自称已实现跨日重识别免费资格认领。guest OwnerRef保留命名空间，实际访客策略由PBI-0012注入前拒绝，不能给访客误发15次。输出安全截断属于已受理普通动作，保持已计次。

## 任务与接口

TASK-0009：账本/流水/ops事件最小迁移、Redis计数与配置、consume/reserve/commit/release/usage及行为测试。
TASK-0010：GET /api/lmt/usage仅查询本人；共用C1用量与C2超限组件。先挂载PC设置页验证，后续讲题/历史页复用；未实现的历史路由不渲染假链接。
TASK-0011：真实Redis并发/进程中断、学习会话幂等、变式发布结算、访客与重识别序号、运营维度/日志/保留与删除集成验证。未齐备不产生G4。

GET /api/lmt/usage返回limit/used/reserved/remaining/billing_date/reset_at（Asia/Shanghai），无客户端owner参数。额度控制是内部服务，不开放消费、充值或管理员配置HTTP入口。扣次结果包含state/allowed/replayed，调用方不能只凭allowed忽略已有执行状态。

## 验证与已知限制

已确认本机PG协议端点SELECT1及Redis TCP PING可用；测试用fakeredis Lua和PGlite协议环境，不等于生产并发或容量结论。首批无模型/对象存储依赖，真实模型/对象存储/OCR/内容安全当前未配置；不使用固定答案冒充识别。

设计保留每owner持久化行锁，增加PG往返以换确定的恢复边界；当前规模合理，延迟与生产吞吐仍须实测。异常停机后的悬挂预留安全占用直至业务恢复，不虚构自动释放成功。

任务AC编号按PBI acceptance_criteria从1开始：TASK-0009覆盖AC1–10、14–17的服务合同；TASK-0010覆盖AC8、12、13、18的展示合同；TASK-0011补齐全部18条真实业务证据。当前仅有合同/组件通过，不代表对应完整AC通过；逐条差距见验证记录。Redis配置自身丢失会恢复默认15，配置持久化/恢复由部署保障。

## TASK-0017 共享事务补充

新增consume_in_transaction供内部确认编排使用，要求已开启的非autocommit PG连接。限额模块拥有全部账本/流水/Lua操作；返回的事务内决定尚未提交，调用方必须外层commit成功后才放行生成。锁顺序为单session→quota owner，不得在该外层事务再锁其他session。普通consume/reserve等原有独立事务接口保持不变。

确认、纠正、教学级别冻结及计次账本由同一PG事务提交；回滚后Redis计数沿用下次从已提交账本重建的恢复机制。确认operation_id在PG提交时随业务记录持久化，提交响应丢失时读回，不另扣。TASK-0017仅验证内部合同，不取代TASK-0011真实基础设施或TASK-0016实际生成/SSE验收。
