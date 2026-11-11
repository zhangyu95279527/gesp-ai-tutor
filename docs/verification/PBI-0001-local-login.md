# PBI-0001 本机登录增量验证 — 2026-11-11

状态：PBI in-progress；TASK-0003/0004 in-verification；G4 未通过，未发布。

## 被测代码与环境

- API: E:/AIworkspacke/gesp-tutor-api，分支 task-0003-email-auth，提交 c0de418。
- Web: E:/AIworkspacke/gesp-tutor-web，分支 task-0004-email-login，提交 1861c52（基于已交付 TASK-0001 工程分支）。两仓均未合并 main，尚无远端。
- CPython 3.12.16，uv 0.13.7；Node v24.17.0；具体依赖固定于 uv.lock 与 package-lock.json。
- 应用使用生产 PG/Redis/SMTP 协议适配器，开发验证后端为 PGlite 0.5.16 + pglite-socket 0.2.19、fakeredis 2.40.0 TCP、本机 aiosmtpd 1.4.6。它们不是生产 PostgreSQL/Redis/DirectMail 的替代验收。
- 迁移：本机 PG 协议端点运行 Alembic upgrade head，users 表已建立；适配器测试仅操作随机 test-* 账号并清理。

## 最终检查结果（控制台摘录）

API 仓执行 ruff check src tests migrations、mypy src、INTEGRATION_DATABASE_URL 指向本机开发库的 pytest -q：

```text
All checks passed!
Success: no issues found in 8 source files
................... [100%]
19 passed in 0.98s
```

Web 仓执行 npm run check（包含 next typegen、tsc、Vitest、生产构建）：

```text
Generating route types...
Types generated successfully
Test Files  4 passed (4)
Tests  20 passed (20)
Compiled successfully in 194ms
Finished TypeScript in 2.0s
Generating static pages using 6 workers (5/5)
```

生成类型文件不再入仓，先 typegen 再类型检查，避免新 checkout 尚无 .next 类型产物而失败。未执行远程 CI，CI 配置存在不代表运行通过。

## AC 验证矩阵

| AC | 本机证据 | 当前结论 |
|---|---|---|
| AC1 六位验证码、5分钟有效 | tests/test_auth.py 格式/300秒边界；tests/test_adapters.py SMTP收件；桌面浏览器本机收件箱收到邮件 | 开发验证通过；DirectMail实际邮箱投递待验收 |
| AC2 60秒重发 | 0/59/60秒边界、并发10请求只发1封、失败不占额度、失败重发保留旧码；页面倒计时可见 | 开发验证通过；真实Redis并发待验收 |
| AC3 五次错锁10分钟 | 剩余4/3/2/1、第五次锁600秒、重发不清错、锁期拒绝send/verify、解锁后再发 | 开发验证通过；真实Redis及移动完整旅程待验收 |
| AC4 新邮箱注册/已有账号登录 | PG适配器同邮箱重复登录ID一致、已注销不激活；单码并发只成功1次；桌面注册/登录成功 | 开发验证通过；正式协议、资料/监护同意与完整用户旅程待相关PBI及TASK-0005 |
| AC5 固定30天 | 注入时钟的30天边界不滑动测试；Cookie HttpOnly/SameSite/Max-Age；浏览器刷新仍登录，退出后回到邮箱页 | 开发验证通过；正式服务与两端验收待补 |

附加检查：Redis/PG故障不签发Cookie，HMAC验证码无明文Redis键、超时旧发送租约不能覆盖新码、IP分动作限频、跨上海自然日日限额、同源/自定义头防护、生产拒绝不安全配置与生产登录表单关闭条件。

## 浏览器观察与截图

使用 CUA 在桌面浏览器完成：测试邮箱发码 → 本机SMTP收件 → 输入错误码提示「还可尝试4次」→ 正确码登录成功 → 刷新仍显示已登录 → 退出并恢复邮箱输入页。未使用真实私人邮箱，未保存验证码或token到交付证据。

[桌面登录页截图](TASK-0004-login-desktop.jpg)。截图为退出并刷新后的状态，展示定稿布局与明确的开发联调说明。

尝试设置390×844移动视口后，实际DOM宽度仍为1197/1280；因此未取得移动视口通过证据，不把桌面截图命名为移动截图。临时视口设置已清除。

## 未完成项与后续

- TASK-0005：真实PostgreSQL/Redis、DirectMail邮件投递、两端完整UI/自动化验证、正式协议与首次资料/监护同意的集成。
- 开发页的「确认使用本机测试流程」不表示正式协议同意，不写同意记录；生产入口暂未开放，未据此批准公开注册或内测发布。
- 用户资料/级别/年龄字段后续迁移补齐；当前 users 仅承接认证最小字段。注册及认证事件的运营接入随既定 ops 契约与后续集成验收补齐。
- 部署时须明确受信代理与真实客户端IP的处理，避免所有请求被计作代理IP或信任任意伪造转发头；本机限频测试仅使用直接客户端IP。
- ADR-001/002 继续待 GB，本次没有批准或实施其提案。
