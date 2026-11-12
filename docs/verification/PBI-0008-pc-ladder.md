# PBI-0008 PC阶梯与SSE客户端验证 — 2026-11-12

状态：TASK-0020 in-verification，PBI-0008 in-progress；TASK-0021真实引擎仍draft，没有G4或发布。

## 代码与环境

- API：task-0020-pc-ladder-stream / f59aa7e，承接169b50f。
- Web：同名分支 / 312d9e1，承接6ca6442；未合main或推送。
- CPython3.12.16、Node24.17.0及原锁文件，无新增依赖/迁移。API沿用PGlite协议代理5432→5433及fakeredis等本机环境。
- 新阶梯GET只返回本人真实的空steps和can_unlock=false，没有已发布讲解时不造内容；unlock校验后固定503不访问额度。API HTTP证据为ASGI+PG测试实例，未启动/重启8000或实际SSE生产者。
- /dev/ladder仅浏览器内存中的协议演示，预置L1及后续正文均明确“开发占位，不是真实讲解/不含答案”，不向真实API扣次。不能当真实内容评估或模型服务证据。

## 命令与捕获结果

API运行ruff check src tests migrations、mypy src；设置INTEGRATION_DATABASE_URL后pytest -q：

```text
All checks passed!
Success: no issues found in 34 source files
190 passed in 10.60s
```

新增test_ladder_routes.py7项：本人空快照/no-store、缺失/未登录/非本人、非法target1/4/布尔/字符串、写保护，以及未配置target2/3均503且会话完全不变。NoQuota一旦访问即测试失败。

Web执行npm.cmd run check，lint/typegen/tsc/Vitest/build通过：

```text
Test Files 11 passed (11)
Tests 91 passed (91)
Compiled successfully in 1844ms
Finished TypeScript in 3.7s
Generating static pages using 7 workers (10/10) in 317ms
```

新增17项ladder-stream测试及3项ladder-ui测试。覆盖逐字节中文/emoji及CRLF拆分、多行data/注释/EOF半帧、过大帧/坏UTF8、未检meta/先chunk/错层级/非法游标、空done/多个终态、重复游标去重、POST幂等键/target、GET原operation+after续接、不自动重POST、429/503、恢复换操作拒绝、快照跳级/未检正文拒绝，以及手动相邻入口/AI标识/无结果/考纲外显示。未运行远程CI。

## PC浏览器观察

IAB，http://127.0.0.1:3000/dev/ladder。以下全部为合成协议演示，服务端元数据检查声明不代表真实模型已通过安全评估。

- 初始仅L1已完成，只提供手动解锁L2，无L3跳级入口。点击L2后才出现L3；再点击L3后全部完成，已完成层级与时间可见。没有定时自动解锁。
- 断线场景只收到已检前缀，标“尚未完成”、L2仍未解锁；“继续接收原讲解”通过同一客户端GET游标续接后，前缀未重复，L2才完成，出现L3入口。请求方法/游标由网络合同测试进一步断言为POST→GET，未用新POST续接。
- 429场景保留L1、L2仍未解锁，显示既有QuotaExhausted，无购买入口/假历史链接。
- 安全截断保留已检部分并明确“后续内容未通过检查，已停止生成”，L2不完成；不误称内容过长。显式再次生成需勾选新请求计次，未勾选按钮禁用。
- 生成失败不升级；新生成需明确勾选计次。未检查meta场景拒收L2正文，只显示格式异常及重新读取入口，不提供不确定状态下的新扣次重试。
- 临时390×844视口DOM测得clientWidth=scrollWidth=375，无横向溢出，随后恢复PC默认视口；未进行移动专项验收。

证据：[PC截图（协议占位）](TASK-0020-ladder-desktop.png)、[最终浏览器快照](TASK-0020-ladder-browser.txt)。截图为L1/L2已完成而L3仍需手动解锁，所有正文明确不是实际讲解。

## 生产关闭检查

临时next start监听回环3020，实际HTTP结果：

```text
{path: /dev/ladder, production_status: 404, contains_placeholder: False}
Stopped temporary production check
```

首次检查命令存在引号错误，未作为通过证据；改独立脚本.cache/ladder/check-production.py重跑得到上述404。临时生产服务已停止，3000开发服务保留。

## 完整AC差距

| AC | 本轮证据 | 完整验收状态 |
|---|---|---|
| 1 不发布未检候选 | 未检meta/先chunk拒绝、续接只接受原操作 | blocked：声明checks不证明真实安全/答案边界，真实历史未实现 |
| 2 L1只有方向 | L1卡片/占位明确，无假答案 | blocked：真实L1内容未生成/评估 |
| 3 L2无完整代码/L3完整 | 分层卡片与手动入口 | blocked：真实L2/L3内容及代码边界未验 |
| 4 仅手动解锁 | PC两次手动点击及SSR不请求通过 | blocked：真实生成全链路未验 |
| 5 相邻解锁 | 客户端仅提供当前下一层，target1/4拒绝 | blocked：真实服务端阶梯状态机仍待实现 |
| 6 重复解锁不重计 | 断线不重POST、完成后不重复同层入口 | blocked：真实解锁幂等账本/计次未接入 |
| 7 session_steps留痕 | 本轮无持久steps | blocked：解锁记录落库未实现 |
| 8 本人解锁历史 | UI支持已完成列表/时间，本人GET隔离 | blocked：真实持久步骤读取仍为空 |
| 9 深度聚合 | 本轮无后端取数 | blocked：session_steps聚合未实现 |
| 10 final_level贴合 | 页面读取本次级别，未使用账号级别冒充 | blocked：真实内容级别贴合/盲评未验 |
| 11 L3拓展视野 | 本轮不填充拓展/答案 | blocked：实际L3内容检查未验 |
| 12 考纲外同阶梯 | 通用标注组件合同通过 | blocked：真实考纲外生成/留痕未验 |
| 13 违规候选重试/质量事件 | 客户端拒收未检声明 | blocked：服务端候选检查/重生成/质量事件未实现 |
| 14 解锁计次 | 显式消耗提示，关闭接口不扣次 | blocked：真实unlock额度事务未实现 |
| 15 超限不推进/回看 | 429保留完成卡片，不完成L2 | blocked：真实额度与持久内容全链路未验 |
| 16 生成失败不退/新请求计次 | 失败保留，重试须显式确认，续接GET | blocked：真实生成与计次流水未接入 |
| 17 P75首字≤5秒 | 无真实生成 | blocked：性能未测 |

DoD：本机规范/类型/全回归/构建、PC交互/基本响应式与文档通过；真实引擎、SSE服务器、持久steps/消息、AI/安全内容有效性、真实E2E/性能/生产恢复未完成，不标done。未知操作号时只允许重新读取；后续服务端快照须在活动操作存在时禁用新解锁，不能因前端刷新而再次扣次。
