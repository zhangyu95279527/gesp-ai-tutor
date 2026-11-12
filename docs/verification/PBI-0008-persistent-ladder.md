# PBI-0008 持久阶梯切片验证

日期：2026-11-12。TASK-0022；状态in-verification，PBI仍in-progress，未产生G4。

## 变更

- API task-0022-ladder-persistence / 20bf1aa，承接f59aa7e；新增迁移0007_ladder、LadderStore/Worker、已完成SSE回放、质量/成功事件与状态模型。
- Web同名分支 / 5370b26，承接312d9e1；接受l1/l2/l3_active，刷新加载进入现有阶梯页，AI正文仍使用AiContent。
- 两仓本地提交、工作区干净；未合main、未推送、未发布。没有以真实模型或生产数据库运行本轮合成测试。

## 自动化证据

API：ruff检查通过；mypy 36源文件通过；配置INTEGRATION_DATABASE_URL后全量pytest，无skip：

```text
209 passed in 13.55s
```

新增19项测试覆盖：

- 确认到L1不二次扣次；同操作只认领一次；L1发布后confirmation completed，刷新/新建仓储实例仍恢复同一正文/步骤。
- L1→L3跳级与重复已完成层拒绝；同键同目标复用、同键不同目标冲突；四个不同键并行仅一个受理，额度只增加一次。
- 解锁超限保持已发布L1，拒绝决定持久化；额度配置恢复后原键仍不重新收费。活动操作禁用解锁。
- 生成失败不退日额度；原操作终态不重跑，显式新键重试再次扣次。
- 两次答案边界不通过均不写消息，质量事件各记一次，无成功学习事件；第二次候选通过只发布第二次正文，成功用量包含内部重生成。
- 安全检查False或字符串passed均关闭发布；生成异常中的供应商私有文本不进入历史/回放。
- 发布正文INSERT后注入状态约束失败，消息/steps用量/状态/成功事件全部回滚；额度仍按受理计次。扣次后注入仓储失败则整个受理事务回滚，Redis下次按PG账本恢复。
- 陌生owner读取、认领、承接、回放均404；默认关闭的新解锁不扣次。冻结final_level=5与创建快照3差异保留。
- 本人HTTP真实PG持久记录读取；完成态SSE含delta/done，可从after=1续取，after=-1拒绝，未知操作404、未登录401，响应no-store。

HTTP由ASGITransport调用应用实例，生成与检查器仅是测试中注入的合成实现。并发测试经本机PG会话代理排队，不构成正式PostgreSQL行锁高并发证明。

Web：npm run check全部通过，包含eslint、Next typegen/tsc、Vitest与next build：

```text
Test Files 12 passed (12)
Tests 95 passed (95)
Compiled successfully in 353ms
Finished TypeScript in 4.0s
Generating static pages (10/10)
```

新增4项持久状态解析回归，沿用既有阶梯UI/SSE测试。本轮未新增可见布局，未重新进行PC浏览器实测；此前TASK-0020截图是协议演示，不能作为本轮真实生成证据。

迁移：在断言本轮新增三表均为空后执行0007→0006→head，结果：

```text
0007_ladder (head)
Empty-table migration downgrade/upgrade verified; existing data preserved.
19 passed in 4.74s
All checks passed!
```

约束故障注入测试首次因DDL参数类型不明确失败，改用psycopg.sql.Literal后全量209通过；未将失败轮记为通过。本机启动检查曾遇5433已占用，沿用原有开发PG代理，未删除或重建数据目录。生产PG/远程CI未执行。

## AC与剩余差距

| AC | 本轮覆盖 | 仍未满足的完整验收 |
|---|---|---|
| 1、13 | 候选先检查再发布、最多两次、质量事件；完成回放无被拒正文 | 真实安全与答案边界检测准确性、实时输出和历史全链路 |
| 5、6、14～16 | PG相邻/幂等、原子扣次、超限保留、失败不退、新键重试 | 公开生成入口、正式PG并发、真实模型故障与浏览器端到端 |
| 7～9 | steps受理留痕、已完成消息、本人快照、按层聚合测试/SQL | 本人PC真实会话回看；日报完整取数与上线规模验证 |
| 10、12 | 按冻结final_level编排，既有考纲外状态字段保留 | 真实级别贴合盲评、考纲外生成端到端 |
| 2～4、11、17 | 沿用PC层级展示，未增加自动升级路径 | 真实L1/L2/L3内容、拓展边界、P75≤5秒 |

当前GET仅回放完成态三帧；运行态409，不是实时SSE。公开confirm/unlock仍503且不扣次。没有真实模型、对象存储、OCR和正式安全服务的验收结果。

L1失败后的公开付费重试、资源预算及失败调用token结算、进程退出扫描/恢复、运行中SSE跟随仍待TASK-0021。生产不能仅设置ready=True就开放，必须完成安全/模型/预算/恢复网关装配。度量事件采用既有保存点尽力写入策略，失败需监测补偿，不宣称完整效果度量交付。
