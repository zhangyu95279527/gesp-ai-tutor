# PBI-0008 持久阶梯独立切片

日期：2026-11-12。TASK-0022；沿用既有PC界面与FastAPI/PG边界，不引入架构变更。

## 事实与范围

- TASK-0020已有PC阶梯、流式解析器与关闭的生成入口；TASK-0017已有确认扣次事务。本轮无需真实服务即可验证持久编排，真实服务稍后配置的用户约定继续有效。
- TASK-0022从TASK-0021拆出可独立验证的持久化基础。TASK-0021仍负责真实生成装配、资源保护、实时SSE与PC完整链路；不将本切片当作其全部完成。
- 未装配生产模型/安全检查；测试候选和检查器仅在测试代码中提供，不新增生产合成讲解接口。

## 合同

- 新增ladder_operations保存每次受理/运行/完成/失败/中断/超限状态。同会话活动操作唯一；会话锁先于操作锁，额度按已有owner锁在同一PG事务内受理。
- attach_l1承接已扣次的confirmation，只从admitted认领，不再次扣次；confirmation与L1操作共享ID，重复承接返回原ID。完成后确认账本也进入completed，旧认领器不能再次执行。
- unlock只接受2或3、当前已完成层的相邻下一层；同键同目标返回原操作，同键不同目标冲突。相邻/活动校验先于额度；超限不推进状态，持久保存拒绝决定。同键跨日或重启不重新收费。
- session_steps在受理时首次写入层级与时间，失败不把会话升级；session_messages只保存通过安全和答案边界检查的有效正文。完成阶梯深度取已发布messages与steps连接，不能把失败受理当作已完成解锁。
- worker先完整生成并检查。安全失败直接终止；答案边界失败最多重生成一次，每次记录ladder_compliance_violation。两个候选均失败则只返回无正文错误；候选不写入消息/回放。检查接口必须返回布尔True，字符串声明不能放行。
- 生成使用questions.final_level与冻结回显，不使用创建时账号级别。真实级别贴合及答案检查准确性仍需后续模型评估，本轮测试只证明检查结果与发布控制流。
- 正文、单调seq、steps的token用量、会话active状态、operation完成及成功事件共享发布事务。成功发布token累计含本次操作内部重生成；失败调用的完整成本/预算账本仍待TASK-0021。
- 失败不退日额度，不自动认领终态；L2/L3显式新键重试重新计次。L1失败后的公开付费重试及进程退出扫描恢复仍待TASK-0021，不自动补跑。
- 本人GET ladder读取真实已发布层级，生产生成入口关闭时can_unlock=false。Web接受l1/l2/l3_active并进入既有LadderSession，AI正文仍经AiContent展示。
- GET operations/{id}/events?after=0..3只回放已完成消息：固定meta/chunk(delta)/done三帧，从持久消息重建稳定ID/正文/时间。done仅在发布事务提交后可见。活动态409 operation_pending，失败态无正文409，超限429，陌生owner404；不冒充运行中的实时流，也不发起生成或扣次。
- 当前公开POST confirm/unlock仍保持503；没有对象存储/OCR/模型/正式安全时不开放新生成。此切片不存在浏览器可创建成功讲解的兜底。

## 聚合与回滚

完成深度取数（包含全部已发布层，失败受理不计）：

```sql
SELECT depth, count(*) AS sessions
FROM (
  SELECT s.session_id, max(s.ladder_level) AS depth
  FROM session_steps s
  JOIN session_messages m
    ON m.session_id=s.session_id AND m.ladder_level=s.ladder_level
  GROUP BY s.session_id
) completed GROUP BY depth;
```

迁移0007_ladder为增量表与状态约束。降级前先恢复旧状态约束，遇到已发布active/confirmation completed即拒绝降级；不得删除已发布数据强行回退。回滚代码时先关闭生成与页面入口，保留表数据，由后续兼容修复恢复。

停止条件：本机规范、类型、PG协议回归、Web回归/生产构建及交付记录齐备。真实内容评估、正式PG并发、实时流、进程终止恢复及性能证据不计入本轮通过项。
