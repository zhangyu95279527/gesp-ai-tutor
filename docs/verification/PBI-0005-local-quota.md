# PBI-0005 本机日限额验证 — 2026-11-12

状态：PBI in-progress；TASK-0009/0010 in-verification；TASK-0011待执行。无G4通过或发布。

## 代码与环境

- API：E:/AIworkspacke/gesp-tutor-api，task-0009-daily-quota / 4e971d4。
- Web：E:/AIworkspacke/gesp-tutor-web，task-0010-quota-display / 90878ad。
- 沿用锁文件、CPython3.12.16、Node24.17.0。Alembic已升级至0003_quota。
- 开发PG协议由PGlite提供，完整TCP连接排队；Redis测试为fakeredis/Lua，本机界面使用fakeredis TCP。没有据此认定真实PG/Redis并发与容量通过。
- 用户确认先完成基础功能，稍后配置模型/对象存储/OCR/内容安全；本轮未调用这些服务。

## 最终校验

API执行ruff check、mypy src，以及设置INTEGRATION_DATABASE_URL后的pytest -q：

```text
All checks passed!
Success: no issues found in 18 source files
76 passed in 3.20s
```

Web执行npm run check：lint、next typegen/tsc、Vitest、生产构建。

```text
Test Files 7 passed (7)
Tests 40 passed (40)
Compiled successfully in 244ms
Finished TypeScript in 1993ms
Generating static pages using 7 workers (7/7)
```

这些数字为整个当前回归集合，不是本PBI验收标准数量。曾使用错误联调变量，得到46通过/29跳过；已改用项目规定的INTEGRATION_DATABASE_URL重跑，上述76项全部执行，无跳过。未运行远程CI。

## AC追溯与差距

编号按PBI-0005 acceptance_criteria顺序，从1开始。以下通过均限于本机服务合同或组件层，未宣布完整业务AC通过。

| AC | 本轮证据 | 完整验收尚缺 |
|---|---|---|
| 1 幂等/并发 | 操作ID重放、payload冲突409、写后丢ack回滚及账本重建 | 真实业务重复推理保护、断线与进程终止 |
| 2 变式预留结算 | reserve/commit/release、重复结算、跨日、禁止退已计次 | 变式发布状态与故障恢复、首次判读不重扣 |
| 3 P0五类计次 | 普通计次参数化；variant必须预留 | 各真实入口绑定和变式完整链路 |
| 4 P1讲评注册 | exam_review规则计1 | FEAT-007入口后续接入 |
| 5 免费项 | 免费动作及首次reidentify规则测试 | 会话免费资格持久认领 |
| 6 第二次起重识别计次 | ordinal参数规则校验；不开放客户端认领接口 | 服务端持久序号、防跨日重复免费 |
| 7 失败矩阵 | 免费项不扣、变式失败释放、已扣不退 | 模型/安全失败实际入口与留痕 |
| 8 15次拒绝 | 默认15，第16次返回内部rejected决定和reset_at | 业务路由转换429 quota_exhausted及UI集成；无公开消费接口 |
| 9 并发原子性 | 剩1次6请求并发仅1放行；Lua+持久owner锁 | 真实Redis/PG并发和容量 |
| 10 上海零点 | 上海/UTC边界、跨日重放/结算、等待owner锁跨午夜按受理日记账 | 真实部署时钟与进程恢复 |
| 11 当前轮不中断 | 本轮额度查询不控制/中断现有输出 | 尚无流式业务，不能声称通过 |
| 12 超限引导 | C2正确文案，无假历史链接 | 历史页真实入口及实际触顶界面 |
| 13 常驻用量 | C1可用/已用/预留分离；PC设置页真实读取和刷新；revision接入合同 | 会话页常驻与每次结算刷新；异步轮询未单独做浏览器时序故障注入 |
| 14 流水 | 正式扣次/拒绝各写一次quota_usage，不重复写 | 真实日报取数与保留/删除集成 |
| 15 拒绝事件 | ops拥有record；稳定事件ID去重；保存点故障不破坏计次事务 | 完整事件维度、投递故障度量及日报 |
| 16 动态配置 | 15→3→0，计数不清零；坏配置拒绝 | 运维配置持久化与演练；Redis配置丢失回默认15 |
| 17 受理即计次 | 普通扣次无退款；新操作ID重新计次 | 真实模型调用失败/中断绑定 |
| 18 无付费入口 | 超限组件无购买或充值入口 | 完整业务页面集成检查 |

## PC联调

127.0.0.1:3000/settings，沿用合成账号：显示“今日可用15次、已用0、处理中预留0”，刷新后重新读取同样结果。未对真实用户数据扣次。本人GET鉴权、额外owner参数不改变归属、no-store和不存在公共消费/配置接口由API测试覆盖。

[PC截图](TASK-0010-quota-desktop.jpg)。视口1197×1199，恢复默认浏览器视口后保存普通截图；曾遇fullPage截图排版异常，未作为最终证据。PC布局实际读取为1120宽网格、764宽主卡，最终普通截图正常。

## 恢复边界与下一检查点

PG提交前不返回放行；每次从已提交账本重建Redis used/reserved，覆盖Redis丢失和Lua写后PG回滚。已有操作重放返回持久决定及replayed，调用方必须结合业务状态避免再次推理，不能只检查allowed。

悬挂预留保持保守占用，未实现自动任务释放；恢复须先核实题面是否发布，再commit/release。访客策略尚未交付，当前guest返回不可用。普通额度服务不提供真实重识别资格认领，也不接受客户端自报免费资格。

TASK-0011继续负责真实基础设施、会话、访客、重识别、变式发布、运营维度与数据保留/删除。没有真实服务配置不阻止其他基础功能继续开发。
