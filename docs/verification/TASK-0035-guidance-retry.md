# TASK-0035 诊断修正首层重试验证

2026-11-18，PBI-0016 AC1 部分验收。API 提交 `f5d11e3`，Web 提交 `d6a8a45`。

| 检查 | 结果 |
| --- | --- |
| API `ruff check src tests migrations` 和 `mypy src` | 规范检查通过，56 个源文件类型检查通过 |
| API `pytest -q --disable-warnings` | 444 passed，1 warning，55.36 秒 |
| Web `npm run check` | ESLint、TypeScript、292 项测试及 Next.js 生产构建通过 |
| 两组件 `git diff --check` | 通过 |

API 使用独立内存 PGlite，先运行 `alembic upgrade head` 至 0014，通过本地串行连接代理运行事务集成测试。额度配置使用测试 Redis。该环境验证请求和持久化结果，生产 PostgreSQL 多连接锁竞争仍待独立验证。

新增三项 API 集成测试覆盖同键并发重放、首次与重试键混用、旧失败操作、本人归属、已完成首层、到期恢复、额度拒绝后重放、写入异常回滚及公开接口的 401/403/404/409/422/503 响应。测试生成器产出合成内容。新增五项 Web 渲染用例覆盖失败、中断、额度不足、已受理和运行中。

公开生成仍关闭。真实模型、安全检查、线上计次及完整 G4 待后续验收。
