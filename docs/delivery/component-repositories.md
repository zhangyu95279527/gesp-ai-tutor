# 组件仓登记 — 2026-11-11

用户确认：按默认位置新建独立组件仓，布局沿用已批准架构。

| 仓 | 本机路径 | 当前状态 |
|---|---|---|
| gesp-ai-tutor | E:/AIworkspacke/gesp-ai-tutor | 交付仓 |
| gesp-tutor-web | E:/AIworkspacke/gesp-tutor-web | Next.js + TypeScript；TASK-0001 已实现并进入验证；分支 task-0001-ai-content-foundation，提交 dca0590 |
| gesp-tutor-api | E:/AIworkspacke/gesp-tutor-api | 独立 Git 仓初始化，FastAPI 业务尚未实现 |

本次仅创建本机仓；尚未创建远端仓或配置 GitHub 分支保护、远程 CI、镜像发布与部署。不得将本机检查记为远程 CI 通过。

首个增量为 PBI-0022 的共用 AI 内容标识组件与渲染约束；真实业务页面接入仍待 TASK-0002，账号与讲题随后按 PBI 就绪推进。两份待审 ADR 只阻塞相关运行能力与发布，不妨碍本次纯前端渲染任务。


## 邮箱登录增量 — 2026-11-11

- Web: task-0004-email-login / 1861c52；API: task-0003-email-auth / c0de418。各自工作区已提交，任务分支未合 main，仍无远端。
- 本机登录入口 http://127.0.0.1:3000/login；API 127.0.0.1:8000；本机测试收件箱127.0.0.1:8025。
- 验证与待办见 docs/verification/PBI-0001-local-login.md；TASK-0003/0004进入验证，TASK-0005仍待真实依赖和两端验收。


## 首次资料与级别 — 2026-11-12

- API: task-0006-profile-level / 87f81b4；Web: task-0007-profile-settings / 851bfc2；工作区已提交，未合main、未创建远端。
- 本机/settings已验证，缺资料账号由/login自动进入/onboarding。协议和内容安全仍为开发验证边界，生产入口未开放。
- 研发与验收口径改为PC优先，移动仅同页基础自适应；总体进度见docs/delivery/development-progress.md。

## 限额与统一输入基础 — 2026-11-12

- API最新：task-0009-daily-quota / 4e971d4；Web最新：task-0012-unified-input / 8d4ce81，包含此前task-0010限额增量90878ad。两仓均未合main、未推送。
- /session开发页已具备本地图文输入及预览，真实上传/安全/识别未接入；不会生成假识别或扣次。详见最新输入检查点及验证记录。

## 服务端输入合同 — 2026-11-12

- API最新：task-0014-input-contracts / 05370ed，承接此前限额4e971d4；Web仍task-0012-unified-input / 8d4ce81。未合main、未推送。
- 新增严格输入合同、Pillow图片字节解码与未配置503响应，无会话/模型/额度副作用；HTTP验证为ASGI测试实例，8000本机服务未重启。真实对象存储/安全/识别仍待TASK-0013，详见服务端输入检查点。

## 会话与回显持久化基础 — 2026-11-12

- API最新task-0015-session-foundation / 02603a2，承接05370ed；Web仍8d4ce81。未合main、未推送。
- 本机迁移0004_sessions(head)，内部SessionStore已验证输入/级别快照、隔离、状态、识别产物与逐字段纠正、持久幂等/版本及事务恢复基础；145项后端回归通过。8000未重启、公开创建入口未接仓储，真实识别/confirm额度与UI仍待后续任务。
