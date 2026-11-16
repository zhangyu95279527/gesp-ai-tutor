# PBI-0015 诊断持久编排验证

2026-11-16；TASK-0029 in-verification。内部编排和本人回看基础通过，完整PBI/G4未通过。

## 版本与行为

- API task-0029-diagnosis-persistence / 7771c44；Web同名分支 / e8fa8ef；完整SHA见current-work.json。
- 0011_diagnosis：共享会话支持dia、创建幂等按本人/类型隔离；扩展三件套材料、诊断操作冻结revision与文本、诊断消息及降级保护。
- 复用识别publish/纠正edit事务与留痕；评测回显与题干同事务。复用ConfirmationService认证归属检查之后的内部锁/幂等/额度流程，diagnosis_create动作确认1次，并原子建立冻结操作。
- 原始代码与裁剪标记从已保存输入加载；输入安全拒绝/缺失/未配置、旧revision或超限不得受理。超限留账但不改快照；同键变化冲突，同键跨日/重启重放不收费。
- worker独立认领诊断操作，使用冻结的确认材料，输出结构/原文/安全/语义全部通过后再锁内复核revision与期限，原子发布。失败不保存候选正文、不退已受理次数、不自动重跑。
- 诊断复用已有操作状态/期限恢复；内部兼容l1_pending/l1_active状态编码，但不创建讲题steps、不写ladder_l1消息，页面不显示为讲题L1。
- 讲题SessionStore、确认/重识别、阶梯操作与历史按tut类型过滤；诊断读取/操作只接受dia，外人或错类型404。
- GET `/api/dia/sessions/{id}` 认证、no-store，只展示本人已完成已检结果；损坏结果503，未完成无正文。新建/确认/纠正POST继续503。
- `/diagnosis?id=...`通过GET回看及重读，复用AI卡片与完整静态分析/裁剪提示；生产新诊断页面仍关闭，修正按钮禁用。

## 自动化证据

API ruff src/tests/migrations及mypy50源文件通过；INTEGRATION_DATABASE_URL全回归无skip：

```text
346 passed in 34.53s
```

新增22项数据库/HTTP测试：创建幂等/类型命名空间与404隔离、共享纠正留痕/确认冻结、一次计费/已完成重放、输入检查缺失/拒绝/非布尔、生成关闭/陈旧revision、超限留账/新键重试、确认写故障回滚、缺输出检查/安全或语义拒绝/假引用/供应商异常/生成器偷换上下文/陈旧发布/超期/发布事件故障均无正文、期限扫描与归属、同键和不同键竞争只计1次、完成后新键拒绝、真实本人GET/写保护/未配置503/讲题404及损坏已保存结果拒绝展示。

Web `npm run check`通过（lint/typecheck/test/build）：

```text
Test Files 18 passed (18)
Tests 203 passed (203)
Compiled successfully in 15.6s
Finished TypeScript in 3.3s
Generating static pages (13/13)
```

新增20项：本人GET cookie/no-store与无POST、7种无正文状态、不完整/未检/错误能力字段拒绝、串会话/坏ID/401/404/503及已保存AI卡片回看。

首次规范检查发现SQL长行与模型标注，已修正；最终ruff/mypy通过。迁移往返前断言没有dia数据，保留既有QA聚合：

```text
0011 -> 0010 -> head passed; existing sessions/messages/events preserved: [1, 3, 5]
```

随后创建明确合成的本机诊断QA，再执行降级确认其报“Diagnosis records must be preserved”，head仍0011；未删除QA或业务数据绕过保护。本机仍使用PGlite协议代理，串行排队的竞争测试不等于正式PG并发/性能证明。

## PC真实HTTP与持久化验证

- API8000/Web3000已重启；使用已有本机QA账号，独立本机脚本注入合成识别/模型/检查值，没有改变生产装配或开放POST。
- 正常`/diagnosis?id=...`通过本人GET显示PG已保存结果，正文明确“【开发验证】不是实际诊断，仅验证已检持久输出”，AI标识/代码第3行/静态推断与裁剪提示可见。
- 点击“重新读取已保存状态”及整页刷新后，已保存结果仍显示，引导修正始终禁用。
- 浏览器操作后PG核对：该QA账号diagnosis_create=1、原session_create=1、原followup=1；当前诊断消息=1、session_steps=0，读取/刷新未增扣次或阶梯。
- 证据：[本人诊断回看](TASK-0029-diagnosis-saved.jpg)。不把该合成记录当真实错因结论或真实检查准确率证据。

## 完整AC差距

- AC4/5内部确认/纠正revision、冻结与1次额度事务有证据；PC真正的OCR→回显确认→诊断尚未打通，确认/纠正表单及正式供应商装配仍待补齐。
- AC1/3结果持久发布/原文引用/展示基础有证据；真实类别质量、语义依据与无确定口吻的盲评未通过。
- AC2不少于20例固定参数重复两次的一致性仍未执行；346项代码回归不替代模型一致性。
- 真实输入输出安全、OCR/对象存储、模型、资源预算/供应商取消、完整诊断历史列表、引导修正与解决状态待后续。没有Mac或移动专项验收；完整G4仍0。
