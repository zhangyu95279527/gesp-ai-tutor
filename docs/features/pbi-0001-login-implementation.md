# PBI-0001 邮箱登录实现切片

Status: approved
日期: 2026-11-11
继承: GA 架构基线、FEAT-001 技术设计、已定稿账号 UI；不实现 PBI-0002/0003/0012，不批准 ADR。

## 任务与实现边界

- TASK-0003：FastAPI 工程与账号模块，Redis 原子验证码/固定期限会话、PostgreSQL users 适配器及迁移、SMTP send_mail 适配器；本机单测使用 fakeredis 和测试账号仓，SMTP 用本机收件服务器。生产启动必须显式提供 Redis/PG/SMTP 配置，不能自动回退内存或 SQLite。
- TASK-0004：Next.js /login，两端复用定稿 A1/A2/A3；同源代理至 API，验证码输入、60 秒重发、错误次数与锁定提示；验证成功只确认身份。资料/监护同意功能未交付前，不假装已完成 onboarding 或开放讲题。
- TASK-0005：真实 Redis/PostgreSQL/SMTP 联调、测试邮箱收件与两端浏览器验收。当前无可用服务，保持待执行，PBI 不得通过 G4。

## 并发与安全细化

1. 服务端生成 6 位随机数字；验证码以绑定规范化邮箱的 HMAC-SHA256 保存，密钥仅来自环境变量；日志和响应不含验证码或邮箱原文。
2. 发码先以 Redis 原子脚本认领限时发送租约，检查邮箱锁、60 秒冷却与上海自然日 20 次上限；SMTP 成功后校验租约所有权并发布验证码、冷却及日计数。发送异常只释放自己持有的租约，不删除旧码/他人状态、不占用正式次数。租约过期的旧请求不得覆盖新请求。
3. 校验为单脚本原子判断、累计错误及消费验证码。重复并发正确提交只能消费一次。重发不清零连续错误次数，成功校验或十分钟锁定窗口结束后清除。
4. 发码中暂拒校验，避免新旧验证码发布竞态。五分钟过期、十分钟锁定、日计数边界在服务端判断；时间测试注入时钟，不 sleep。
5. 邮箱统一小写，users.email 唯一；INSERT ON CONFLICT 只更新 active 用户，不重新激活已注销用户。验证码消费后 PG/Redis 下游失败，拒绝登录、不签发 Cookie；提示重新获取验证码，无法跨 PG/Redis 伪装为单事务。
6. 不透明 256bit token，Redis 中仅保存 token 摘要键、uid 与固定 30 天 expires_at；读取不滑动续期。Cookie HttpOnly/Secure/SameSite=Lax，生产必须 HTTPS；本机 HTTP 仅显式开发配置允许关闭 Secure。
7. 写接口要求 X-Requested-With: GESP-Web，并校验配置的同源 Origin（缺省 Origin 的非浏览器请求可通过自定义头）；CORS 不开放。每 IP 每分钟发码/验证分别限频，使用直连客户端 IP，不信任任意 X-Forwarded-For。
8. 所有认证响应 Cache-Control: no-store；错误只返回约定业务码与 retry_after/attempts_left/unlock_at。验证码或 token 不进入 URL、localStorage 或诊断日志。

## REST 契约

- POST /api/auth/email-code `{email}` → `{expires_in:300,retry_after:60}`；验证邮箱格式后才受理。
- POST /api/auth/verify `{email,code}` → `{authenticated:true,profile_complete:false}` 并 Set-Cookie；本切片新账号尚无资料，前端明确下一步资料待接入。
- GET /api/auth/me → `{user:{id,profile_complete:false}|null,guest:boolean}`；过期或缺凭证返回访客，服务存储故障返回 503，不误报已登录。
- POST /api/auth/logout → 204，服务端删除当前 token 并清 Cookie。
- GET /health → `{status:ok}`；不泄漏配置与依赖地址。
- 错误主体 `{code, ...fields}`，422 无效邮箱/验证码格式；429 send_too_frequent/code_locked/daily_send_limit/ip_rate_limited；400 code_expired/code_mismatch；409 send_in_progress；502 mail_send_failed；503 auth_unavailable。

## 开发依赖确认与正式验收边界

2026-11-11 已配置标准 CPython 3.12.16 与 uv 锁定环境，开发验证依赖已实际连通：PGlite 的 PG 协议端点 SELECT 1、fakeredis TCP PING、本机 SMTP NOOP 均成功。应用使用与生产相同的 PG/Redis/SMTP 协议适配器，不引入生产内存或 SQLite 回退。此环境仅确认 TASK-0003/0004 可执行；真实 PostgreSQL/Redis 的并发语义、DirectMail 投递和正式协议内容由 TASK-0005 验证，缺证据不能过 G4 或发布。G3 是开发就绪判断，不是生产依赖验收。

Windows 兼容：PG 适配器采用 psycopg 同步连接并经 asyncio.to_thread 调用，避免 Windows 默认 Proactor 与异步 psycopg 不兼容；不阻塞 FastAPI 事件循环。邮箱规范化为小写存储，数据库 text + lowercase CHECK + UNIQUE 实现既有大小写不敏感唯一语义。


## 本次 UI 接入约束

正式用户协议/隐私政策正文与首次资料/监护同意尚未交付；本机开发登录页以明确的测试确认替代正式协议勾选，不生成正式同意留痕。生产登录入口保持关闭。此为开发联调状态，不将其作为定稿 A1 协议部分已实现的证据；TASK-0005 须在正式协议与相关 PBI 就绪后复核。

移动视口验证尝试中，浏览器 viewport capability 接受设置后实际 DOM 宽度仍为 1197/1280，未得到 390px 视口；因此本次只记录桌面真实浏览器通过，移动验收保持 pending，未把桌面截图误记为移动证据。
