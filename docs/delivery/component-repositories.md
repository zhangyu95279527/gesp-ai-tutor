# 组件仓登记 — 2026-11-11

用户确认：按默认位置新建独立组件仓，布局沿用已批准架构。

| 仓 | 本机路径 | 当前状态 |
|---|---|---|
| gesp-ai-tutor | E:/AIworkspacke/gesp-ai-tutor | 交付仓 |
| gesp-tutor-web | E:/AIworkspacke/gesp-tutor-web | Next.js + TypeScript；TASK-0001 已实现并进入验证；分支 task-0001-ai-content-foundation，提交 dca0590 |
| gesp-tutor-api | E:/AIworkspacke/gesp-tutor-api | 独立 Git 仓初始化，FastAPI 业务尚未实现 |

本次仅创建本机仓；尚未创建远端仓或配置 GitHub 分支保护、远程 CI、镜像发布与部署。不得将本机检查记为远程 CI 通过。

首个增量为 PBI-0022 的共用 AI 内容标识组件与渲染约束；真实业务页面接入仍待 TASK-0002，账号与讲题随后按 PBI 就绪推进。两份待审 ADR 只阻塞相关运行能力与发布，不妨碍本次纯前端渲染任务。
