# PBI-0008 超时恢复与显式重试验证

日期：2026-11-12。TASK-0023 in-verification；PBI仍in-progress，完整G4仍0。

## 变更及版本

- API task-0023-ladder-recovery / d87f315：0008期限迁移、LadderRecovery、生命周期扫描器、旧执行期限守卫、本人状态与关闭的retry-l1 HTTP。
- Web同名分支 / 9d0ec44：operation元数据解析、OperationNotice、刷新后的失败重试计次确认。
- 两仓工作区干净，均本地任务分支提交，未合main、未推送、未发布。

## 自动化证据

API执行ruff、mypy及设置INTEGRATION_DATABASE_URL后的完整pytest：

```text
All checks passed!
Success: no issues found in 37 source files
227 passed in 17.06s
```

新增18项数据库/HTTP/异步生命周期测试：

- admitted/running过期均一次性变interrupted；原确认同步中断。活跃未过期、已完成正文不受影响；没有退费或自动生成。
- 到期未认领时不调用生成器；过期且尚未扫描时也无法发布；旧worker在回收/新重试之后不能覆盖新结果。
- L1显式新键重试计1次、同键复用、改被重试操作冲突、4个并发新键仅一个受理。重试保留final_level=5与账号快照3。
- 未失败原操作、未配置网关、陌生owner/未知操作拒绝不扣次；超限拒绝持久化，旧键不复活，新键可受理。
- 扣次后注入插入失败，账本事务回滚；生成期间人为使期限到期，候选不发布且不退额度。
- 快照惰性回收已到期L2并保留已发布L1；恢复器定时扫描、临时PG错误后下轮继续，退出后不再扫描。
- 本人状态HTTP返回中断、no-store，未登录401、陌生操作404；新retry-l1接口检查关联后503不扣次，缺写入保护403。

HTTP为ASGITransport应用实例；生成和检查器是测试代码注入的合成实现。PG协议运行于本机PGlite会话代理，不能据此声称正式PG竞争、进程kill或多实例恢复性能验收完成。

Web执行npm run check：

```text
Test Files 13 passed (13)
Tests 109 passed (109)
Compiled successfully in 1465ms
Finished TypeScript in 3.8s
Generating static pages (10/10)
```

新增14项测试：六种持久状态解析、坏ID/目标/状态/期限/私有错误码拒收、SSR中断通知与刷新后勾选要求/禁用按钮、处理中不出现自动重试入口、L1未配置禁用说明。现有阶梯/AI标识/SSE回归继续通过。

迁移前断言ladder_operations为空，执行0008→0007→head：

```text
0008_ladder_deadline (head)
Verified empty-operation migration 0008 -> 0007 -> head; no business data removed.
18 passed in 4.21s
```

本轮未重启API8000或Web开发服务，未重新进行浏览器实测/截图，没有运行远程CI。初次ruff发现长行，格式化后规范和类型全部通过。

## 验收边界

- 覆盖AC1/6/14～16的恢复与计次控制流，AC4/8的状态提示支撑；真实生成内容、安全边界、完整PC端到端和性能仍未通过。
- 扫描器仅终结过期操作，不中止已经发给供应商的网络请求。旧请求可继续耗资源，但不能发布；真实供应商超时/取消、预算与失败成本仍待TASK-0021。
- 进程退出后的未完阶梯最迟在持久期限到期后由扫描/读取恢复；不是退出瞬间标记。尚未attach_l1的孤立confirmation仍待统一装配处理。
- 公开confirm/unlock/retry-l1均保持生成未配置503。内部重试验证不代表用户现在可获得真实L1。
- 成功快照及失败提示已编码并通过SSR验证；正式PG并发和真实浏览器交互证据尚缺，不记完整G4。
