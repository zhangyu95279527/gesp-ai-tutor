# PBI-0002 本机资料与级别验证 — 2026-11-12

状态：PBI in-progress；TASK-0006/0007 in-verification；完整G4未通过，未发布。

## 被测代码与环境

- API：task-0006-profile-level / 87f81b4，位于 E:/AIworkspacke/gesp-tutor-api。
- Web：task-0007-profile-settings / 851bfc2，位于 E:/AIworkspacke/gesp-tutor-web。
- 沿用CPython3.12.16、Node24.17.0及两仓锁文件；PG协议开发环境为PGlite，Redis为fakeredis，本机SMTP收件。没有把这些替身当成真实云服务验收。
- 已执行Alembic upgrade head至0002_profile；users资料/待生效级别、user_consents测试标记均落库。

## 最终检查（本次控制台摘录）

API：ruff check src tests migrations、mypy src、带本机INTEGRATION_DATABASE_URL的pytest -q。

```text
All checks passed!
Success: no issues found in 12 source files
............................................... [100%]
47 passed in 1.74s
```

Web：npm run check（lint、next typegen/tsc、Vitest、生产构建）。

```text
Test Files  6 passed (6)
Tests  32 passed (32)
Compiled successfully in 653ms
Finished TypeScript in 2.6s
Generating static pages using 7 workers (7/7)
```

未执行远程CI。47/32是整个当前后端/前端回归集合，不是本PBI独有的验收标准数量。

## AC与合同证据

| AC/规则 | 证据 | 结论 |
|---|---|---|
| AC1 首次资料、缺项及本人权限 | test_profile.py：缺项422逐字段、非法额外owner字段、未登录401；PC登录自动进入/onboarding，完成后进入/settings | 本机通过；真实主功能入口仍待学习会话集成 |
| AC2 1–8级与设置 | 严格整数拒绝0/9/bool/string；本人PATCH；PC保存当前/待生效级别及刷新读取 | 本机通过 |
| AC3 上海次日生效 | 服务测试：修改当日仍旧级别、翌日滚动、重复修改最后一次为准、改回当前级别取消；原整数快照保持不变 | 合同测试通过；真实会话/历史页面尚未实现，实际历史集成未验收 |
| 月份监护要求 | 14岁生日月首末日、次月、跨年、二月边界；前端7组月份测试；PC合成月份触发测试监护确认 | 支撑代码通过，不等同PBI-0003完整完成 |
| 资料与同意同事务 | 故意触发PG约束失败后资料/同意均未写入；重复提交409，不重复留痕 | 本机PG协议验证通过；真实PG并发待验证 |
| 版本/文本/安全前置 | 版本不一致409、正文哈希不符拒绝；test_only清单生产拒绝；缺check_text或被拦截拒绝 | 本机测试通过；正式文本与真实内容安全未交付 |
| 停用账号 | 服务端拒绝继续写资料与级别，不重新激活 | 本机通过 |

协议哈希统一为UTF-8/LF文本规范，避免Windows/Unix换行差异影响同一文本的校验；正文实质变化仍被拒绝。

## PC实际操作

使用合成测试账号完成：邮箱验证 → 自动进入首次资料 → 填写测试昵称和测试出生月份 → 选择3级 → 页面出现测试监护确认 → 提交后进入设置页 → 选择4级保存 → 显示当前3级、2026-11-13 00:00北京时间起4级生效 → 刷新仍保留该状态。

[PC设置页截图](TASK-0007-profile-desktop.jpg)。账号资料为合成测试数据，协议和监护勾选明确是测试流程，未将其记录为正式授权。

联调中发现PGlite开发端点默认仅允许一个连接：串行资料/协议/留痕读取200，设置页并行读取有503。已在交付仓本机.cache/dev-services/start-postgres.mjs增加完整连接排队（5432→内部PGlite5433），保留生产应用的PG适配器；随后设置页并行加载、保存和刷新均通过。开发脚本未作为生产部署代码提交，也不声称验证生产并发能力。

## 最新移动端口径

2026-11-12用户确认PC为主开发/验收端，移动仅通过同一浏览器页面基础自适应查看。已同步NFR-USE-01、相关PBI与设计交接补记；本次不做移动编辑器/软键盘或完整移动旅程专项，旧视口工具问题不再阻塞PC推进。基础响应式CSS已提供，未虚构移动浏览器实测证据。

## 待办

- TASK-0008：正式协议、check_text、真实PG/Redis及新旧学习会话/历史快照集成。
- PBI-0003：账号注销、15工作日副本/备份删除等仍未实现，不能以本轮年龄和测试留痕代码代替。
- 本轮设置页只修改级别，昵称/出生年月只读；其他资料修改另行按相关PBI细化。
- 生产/onboarding、/settings和/login入口继续关闭；不得把测试文本、测试同意或本机替身算正式上线条件通过。
