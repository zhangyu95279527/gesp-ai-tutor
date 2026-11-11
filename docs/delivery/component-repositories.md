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
