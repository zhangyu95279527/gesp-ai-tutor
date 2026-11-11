# PBI-0022 前端标识最小实现设计

Status: approved
日期: 2026-11-11
范围: FEAT-006 / PBI-0022，沿用已批准 UI 与 FEAT-006 §3.4，不引入架构演进。

## 实现契约

- gesp-tutor-web 为独立 Next.js / TypeScript 仓，位于 E:/AIworkspacke/gesp-tutor-web；api 仓独立初始化，业务实现另随账号 PBI 推进。
- TASK-0001 建立前端工程、纸感 tokens、AiContent 与 AiBadge。AiContent 以 source 字符串渲染 Markdown，使用 ReactMarkdown 默认安全 URL 过滤并跳过原始 HTML；调用方不能传 children、className、style 或关闭标识参数。
- AiBadge 为组件内部固定行为，DOM 中保留「AI 生成」可访问文本，不可通过 hover、点击或流式状态关闭。沿用定稿布局；小号文字使用 ink-2 以保证阅读对比度。
- ESLint 禁止除 AiContent 外的源码导入 react-markdown 或下层 HTML/Markdown 渲染器，并禁止页面使用 dangerouslySetInnerHTML；测试验证绕过导入被实际拒绝。
- 开发组件预览位于 /dev/components，生产环境返回 404；样例仅为视觉与组件验证，不能被当作真实模型输出。
- TASK-0002 为讲题/历史、诊断、变式与模考讲评接入渲染入口，逐展示位取 UI 证据。各业务页面尚未落地时保持此任务待执行，PBI 不得通过 G4。

## 依赖与验证

已确认 Node v24.17.0、npm 11.13.0 可用，npm registry 可访问；版本以组件仓 lockfile 固定。此渲染切片无模型、SMTP、PG、Redis 或 ADR-001/002 运行依赖。后续真实页面集成须随对应 Feature 就绪推进，不冒认其完成。

AC1 → TASK-0001 提供唯一入口，TASK-0002 逐展示位接入并核验；AC2 → 两个任务验证固定标识、无关闭入口及响应式可见性。组件单测、安全输入、lint 实际拒绝、类型检查、生产构建与生产预览路由拒绝为 TASK-0001 验证证据。G4 必须补齐真实页面逐页清单。
