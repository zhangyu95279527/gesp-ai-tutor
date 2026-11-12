# PBI-0007 确认受理基础验证 — 2026-11-12

状态：TASK-0017 in-verification，PBI-0007仍in-progress；完整TASK-0016 draft。没有G4或发布。

## 环境、提交与命令

- API：E:/AIworkspacke/gesp-tutor-api，task-0017-confirmation-admission / 2e009fa，承接02603a2及此前所有增量。
- CPython3.12.16；锁文件无变更。本机5432 PG协议代理→PGlite5433，额度用fakeredis Lua；不是生产PG/Redis并行环境。
- Web无改动/未重跑。8000服务未重启；新确认类没有HTTP或生产装配，generation_ready默认False。所有确认放行测试均显式使用测试就绪回调与合成识别产物，不代表真实模型可用。

在API仓执行：

```powershell
$env:DATABASE_URL='postgresql://postgres:postgres@127.0.0.1:5432/postgres?sslmode=disable'
.venv/Scripts/python.exe -m alembic upgrade head
.venv/Scripts/ruff.exe check src tests migrations
.venv/Scripts/mypy.exe src
$env:INTEGRATION_DATABASE_URL=$env:DATABASE_URL
.venv/Scripts/python.exe -m pytest -q
.venv/Scripts/python.exe -m alembic current
```

捕获最终输出：

```text
All checks passed!
Success: no issues found in 29 source files
........................................................................ [ 45%]
........................................................................ [ 90%]
................                                                         [100%]
160 passed in 5.12s
0005_confirmation (head)
```

新增tests/test_confirmation.py共15项。先11项专项通过，随后补最后一次额度竞争与严格标志验证并完成全回归160项，无skip。git diff --check通过；没有远程CI或线上部署证据。

## 可复核内部合同证据

来源：API tests/test_confirmation.py；测试随机owner UUID，最终清理测试session及quota/events数据。

- 正常受理：确认6级、创建快照3级、原判定3级各自保留；同一PG事务写纠正、final_level=6、revision2、l1_pending、确认admitted及正式扣1次。之后新键确认或edit被状态拒绝。
- 超限：配置0次时仅保存quota_rejected及额度拒绝日志；确认前后SessionStore.get完整快照相同，包含版本/纠正/级别。配置恢复为1后，同键仍返回原拒绝，新键才允许重新申请。
- 同键重放与提交响应丢失模拟：忽略首个已提交结果，跨上海日期、清Redis、重建服务后用同键读回相同operation_id及原额度决定，旧账期仅1条流水，新账期used=0。不是实际网络丢ack或kill进程演练。
- 事务失败：Lua成功后、保存确认前注入异常，确认记录和PG额度记录均0，会话revision仍1；Redis暂留used1，下次usage按账本恢复used0，再同键确认仅正式消费1次。
- Redis故障：模拟eval不可用，PG事务回滚，不冻结final_level/不推进revision。
- 账号隔离/旧revision：其他owner确认404，旧版本409，无扣次。严格校验expected_revision布尔/负值与字符串继续标志。
- 考纲外：level0未显式继续时拒绝且used0；显式continue_out_of_syllabus后才保存final_level0/out_of_syllabus=True，原账号快照3保留。
- 生成缺失：默认readiness返回False，确认503 generation_unavailable，不扣次、不改版本。生产尚无实际ready实现。
- 并发同键：4线程6请求仅1次新受理，其他重放；4线程6次claim_start仅1次成功。不同session竞争同账号最后1次额度，仅1个admitted，另一个quota_rejected且保持待确认。
- 执行认领：其他owner不能claim；running不能重复claim。标interrupted后重建worker仍不能重领，额度used仍1，不自动退款。这里只测试状态，没有模型执行或L1发布。
- 新consume_in_transaction拒绝autocommit与尚未开启事务的连接；PG异常回滚测试也证明该接口未偷偷提交调用方事务。

PGlite开发代理会串行处理完整连接，本机多线程证据不能替代生产PG并行、锁等待/吞吐或进程终止验证。限额算法和Redis恢复均沿用既有服务，不在core/session直接访问限额表。

## AC映射与剩余差距

| AC | 本轮基础证据 | 完整验收状态 |
|---|---|---|
| 1 教学级别/不重赠首次免费 | 正式确认冻结final_level，账号与原判定快照不改 | blocked：真实后续讲解适配、重识别资格未接入 |
| 2 回显纠正/确认后讲解 | 受理持久化、单次worker认领、无占位输出 | blocked：真实PC回显/生成与内容检查未接入 |
| 3 confirm计1次/超限不推进 | 共享PG事务、最后1次竞争、回滚/重放及超限快照相同 | blocked：公开确认/SSE/真实L1与安全/资源预算未接入 |
| 4 重识别回显 | 本轮无新增 | blocked：同会话重识别未实现 |
| 5 首次免费/后续计次 | 本轮无新增 | blocked：持久资格认领及计次未实现 |
| 6 识别失败提示/重试入口 | 本轮无UI | blocked：真实识别失败与PC重试未验 |
| 7 识别失败免费 | 既有基础拒绝回归通过 | blocked：真实识别失败链路未验 |
| 8 纠正留痕 | 正式confirm同事务追加纠正且重试不重复 | blocked：真实用户纠正提交及安全检查未接入 |
| 9 route/confidence | 沿用TASK-0015证据 | blocked：真实管线及指标取数未验 |
| 10 考纲外继续/持续标注 | 显式继续校验与通用标志持久化 | blocked：真实判定、PC提示和持续标注未验 |
| 11 P75首字≤5秒 | 无真实生成 | blocked：性能统计未执行 |

DoD：本机规范/类型/全回归、迁移和文档通过；完整AC、真实E2E、AI/安全有效性、生产恢复及发布未完成。没有自动恢复扫描器或L1完成态发布，中断后显式重新生成的计次流程仍需后续实现。数据库降级未执行；存在l1_pending数据时旧约束会拒绝降级，不能静默丢掉冻结状态。
