# 原子受理与持续Git同步验证

日期：2026-11-13。TASK-0024 in-verification，完整G4仍0。

## 改动

- API task-0024-atomic-admission / c65dccb，基于换机准备4e98e79。新增LadderAdmissionService，L1操作/steps与确认冻结/扣次共享PG事务。
- 旧孤立确认恢复接入原扫描器，总批次上限50，恢复中断记录供显式重试，不自动生成或收费。
- 交付仓新增跨平台workspace-sync.py、current-work.json；记录用户每轮提交/推送和固定换机快照约定。
- Web没有源代码变化，仍c20356f；未重新运行其109项历史基线或浏览器测试，不把历史结果算成本轮新验证。

## 证据

API：ruff含src/tests/migrations通过，mypy38源文件通过；配置INTEGRATION_DATABASE_URL后完整回归：

```text
All checks passed!
Success: no issues found in 38 source files
237 passed in 19.20s
```

新增10项测试覆盖：

- 确认成功即存在同ID L1操作；原确认执行权已交阶梯，旧认领器不能重复认领。级别冻结保留，同键重放及完成后重放不再次计次。
- L1操作/steps插入之后注入异常，确认/会话/额度/操作/steps均回滚；下一次同键可正常受理，Redis按PG账本修复。
- 未配置与超限不创建L1；旧admitted/running/interrupted且过期的孤立确认转为同ID中断操作，created/deadline来自原受理时间。
- 恢复不调用模型或扣退额度；恢复终态不能认领生成，但可显式新计次重试。未到期旧确认不误中断。
- 并发扫描只恢复一次，重复attach返回原操作，不重复计次；恢复持久化故障回滚后可再恢复。
- 两条孤立记录分两批limit=1恢复，确认孤立/阶梯回收共享批次上限。

数据库仍为本机PGlite协议代理，未重新配置或迁移（仍0008）。代理排队的并发测试不等于正式PG锁竞争证明。初次规范检查发现长行、最后新增测试有导入排序问题，修正后ruff通过；导入排序未改变已通过的测试逻辑。

同步脚本：Python标准库unittest使用临时本地Git工作仓/裸远端，无外部凭据：

```text
Ran 7 tests
OK
```

覆盖任务/快照双ref推送与核验、脏树拒绝、全部仓前置检查后才推送、远端较新不覆盖、预检后另一电脑修改快照导致双ref原子拒绝、current-work组件SHA过期拒绝、缺检查点拒绝。实际GitHub同步结果由本轮最后的脚本输出核对，不以本地commit代替远端保存。

## 限制

- 新原子服务尚未接到公开confirm；真实安全/模型/预算未配置，公开confirm/unlock/retry-l1仍503不扣新次数。
- 本轮解决旧孤立记录和新内部入口的事务缺口，不代表真实生成、实时SSE、供应商取消或PC全链路通过。
- 同步脚本可保证单仓两ref原子更新，三仓之间仍可能网络部分成功；组件先于交付仓，失败需重新检查后重试。脚本不提交未保存文件、不强推、不搬运密钥或开发数据库。
- Mac运行与远程CI没有新的通过声明。换机须使用快照分支并读取current-work.json；默认main仍未合入最新功能。
