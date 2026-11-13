# PBI-0011 历史与听懂验证

2026-11-13；TASK-0025 in-verification，完整PBI/G4未通过。

## 版本与接口

- API task-0025-history-understood / 151f471；Web同名分支 / aac2957。
- 本人GET history列表/详情、GET/POST sessions/{id}/understood，迁移0009_understood。
- PC /history搜索/已听懂筛选/分页，/history?id=只读回看；正常阶梯也有听懂控件。回看与标记不访问额度服务或生成器。

## 自动化验证

API：ruff包含src/tests/migrations、mypy39源文件通过，配置INTEGRATION_DATABASE_URL后完整pytest无skip：

```text
248 passed in 23.57s
```

新增11项覆盖本人隔离、只读不生成/不扣次、创建与最终级别分别显示、字面搜索（%/_/SQL文本不作通配）、游标损坏/筛选变化拒绝、同时间戳分页不重复、未确认记录不展示、听懂完成条件/活动操作拒绝、重复并发只保留首次时间/唯一事件、保存故障回滚、HTTP登录/写保护/非法参数，以及每日标记与队列标记率取数。

Web：npm run check含lint、typecheck、126项测试、生产build通过，新增17项客户端与SSR测试：列表/空态/坏记录拒收、编码筛选GET、幂等写保护/无额度字段、详情同ID/只读校验、HTTP错误不作空成功、题目转义、AiContent标识、禁用追问/未检结果不显示、标记返回必须有首次时间和印章状态。

```text
Test Files 14 passed (14)
Tests 126 passed (126)
Compiled successfully in 656ms
Finished TypeScript in 2.6s
Generating static pages (11/11)
```

迁移往返先断言无非空听懂标记，再0009→0008→head：

```text
0009_understood (head)
Verified 0009 -> 0008 -> head with no feedback data discarded.
```

初次新增统计测试漏导入psycopg导致1失败，补齐导入后248全回归通过；初次长行也已修正。开发API最初用PowerShell脚本启动受本机执行策略拒绝，改为常规Python启动入口，没有关闭或绕过系统执行策略。

## PC浏览器实测

IAB，127.0.0.1:3000；正常登录本机测试流程，SMTP仅投本机收件箱。后端8000为本轮真实应用进程，PG协议/Redis TCP/SMTP为本机开发服务。

- 列表读取本人PG记录，创建3级/本次5级分开展示，L1完成。搜索“数字”找到本人记录。
- 未标记时“只看已听懂”返回空态；进入详情后只显示已有已检L1，AI标识可见，没有L2/L3解锁入口。
- 点击听懂后显示“已听懂·已盖章”；页面刷新后印章仍在，按钮不再出现；返回列表勾选已听懂仍可查到同一记录。
- 真实PG核对QA owner：consumed额度记录仍为首次确认的1条，understood_marked事件为1条。回看/查询/标记没有新增扣次。
- 变式/继续追问明确未开放，无伪造结果。当前浏览器使用的题目/正文显式“开发验证、并非真实AI讲解”，是用于实际HTTP/PG交互的合成测试夹具，不是模型能力验收。

证据：[历史列表](TASK-0025-history-list.jpg)、[刷新后回看印章](TASK-0025-history-detail.jpg)、[最终浏览器状态](TASK-0025-history-browser.txt)。截图没有真实用户信息/验证码。

本轮只进行PC浏览器实测；窄屏使用同页响应式CSS，未新增移动专项证据。正式PG竞争、真实模型讲解/安全仍未验证。

## 统计取数

```sql
-- 每日首次标记数（北京时间）
SELECT (understood_at AT TIME ZONE 'Asia/Shanghai')::date AS day, count(*)
FROM ai_sessions WHERE understood_at IS NOT NULL GROUP BY 1;

-- 按首次有效讲解日期形成队列，再统计其中的已听懂比例
WITH completed AS (
  SELECT session_id,min(created_at) AS first_at
  FROM session_messages GROUP BY session_id
)
SELECT (c.first_at AT TIME ZONE 'Asia/Shanghai')::date AS day,
       count(*) AS completed_sessions,count(s.understood_at) AS understood_sessions
FROM completed c JOIN ai_sessions s ON s.id=c.session_id GROUP BY 1;
```

## 差距与运行状态

- AC1的记录/幂等/取数与PC操作已有证据；AC2的已发布阶梯回看已实现，但完整变式结果仍缺；AC3继续追问尚未实现。因此不标PBI done或G4通过。
- 听懂只记录反馈，不自动生成变式；变式ADR/真实校验/安全未就绪时不改变阶梯状态或填充题目。
- 生产history页面沿用环境开关显示未开放，公开新生成入口保持503。没有生产发布或远程CI通过声明。
- 3000前端开发服务已重启、8000API与6379/1025/8025本机服务已启动并保留。QA账号/会话留在本机供查看；其数据和启动临时文件均在忽略目录或开发数据库，不随Git迁移。
