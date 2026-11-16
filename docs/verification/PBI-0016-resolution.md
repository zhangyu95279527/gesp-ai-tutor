# PBI-0016 解决状态回填验证

2026-11-16；TASK-0030 in-verification。仅AC2反馈记录切片，完整PBI/G4未通过。

## 实现与版本

- API task-0030-diagnosis-resolution / 8f35a63；Web同名分支 / c5d6491；完整SHA见current-work.json。
- 0012_resolution新增本人诊断当前反馈和幂等回执表；状态solved/unresolved、独立version和更新时间。不改变诊断生成revision、正文、冻结上下文或阶梯。
- GET/POST `/api/dia/sessions/{id}/resolution`需认证；写保护/来源/幂等键复用。只有本人dia类型、已检完成且无活动操作才可写；损坏诊断拒绝回填。
- 同键同负载返回原回执，同键变化冲突；新键版本不符409。改判留痕，同态不增加版本/状态事件，旧键回执不覆盖最新最终态。
- 当前反馈与回执同事务；核心写失败回滚。回填和改判不接触额度/模型/Judge；ops状态事件仅辅助，业务事实由当前表和回执保留。
- PC系统卡支持未填选择、未解决/已解决留痕与“改状态”；不是AI内容。请求不确定保留同键重试，POST后GET最新态，版本冲突重读后要求用户重新选择，不自动覆盖。
- 用户回填不表示系统重判或诊断准确；未解决追问和已解决变式入口明确暂未开放，修正阶梯仍未接入。

## 自动化证据

API ruff src/tests/migrations、mypy51源文件通过；配置INTEGRATION_DATABASE_URL后全回归无skip：

```text
364 passed in 34.05s
```

新增18项：最终态/改判/同态统计和原回执、幂等变化/旧版本冲突、本人及讲题类型隔离、未完成/失败/活动操作/损坏检查拒绝、写失败回滚当前态/回执/事件、同键和不同键竞争、7项严格合同、HTTP认证/保护/来源/422/409/no-store，以及NoQuota禁止额度访问。回填后诊断消息数1、steps0，原诊断消费仍1。

Web `npm run check`通过（lint/typecheck/test/build）：

```text
Test Files 19 passed (19)
Tests 223 passed (223)
Compiled successfully in 821ms
Finished TypeScript in 3.0s
Generating static pages (13/13)
```

新增20项：严格视图/版本时间一致性、可回填能力、固定幂等键/负载、POST写保护后GET最新态、网络和GET故障不自动重POST、旧回执不覆盖最终态、版本冲突、不合法请求无发送、同态不增版本、401/404/503以及系统记录无AI标识/无重新判题承诺。

首次坏ID测试暴露loadResolution同步抛错，已改为始终返回Promise并经错误提示路径处理；修复后223项及构建通过。新增后端检查与既有ready属性命名冲突、测试SQL长行/循环变量绑定亦已修复，最终规范/类型通过。

无反馈数据时验证：

```text
0012 -> 0011 -> head passed; previous sessions/messages/events preserved: [2, 4, 6]
```

PC回填后有反馈/回执数据，再执行降级被“Resolution feedback must be preserved”保护拒绝，head仍0012；未删除反馈绕过。开发数据库为PGlite协议代理，排队并发不等于生产PostgreSQL性能/竞争验收。

## PC与数据核对

- API8000/Web3000已重启，使用上轮明确合成的持久诊断QA；未添加模型/安全替身到公开服务。
- 正常诊断页出现“验证过了吗？”；点击“还没解决”后显示未解决、时间、改状态及禁用追问说明。
- 点击“改状态”→“已解决”，显示已解决留痕和禁用变式入口；整页刷新和重新读取后保持。
- PG最终状态solved/version2，回执2、dia状态事件2；统计当前反馈只有一条已解决，改判没有扩大已回填分母。
- 额度仍diagnosis_create=1、旧followup=1、旧session_create=1；诊断正文1条、steps0，没有回填扣次或重生成。
- 截图：[未解决](TASK-0030-unresolved.jpg)、[改判后刷新保持](TASK-0030-resolution-saved.jpg)。诊断正文仍明确开发验证，不作为真实解决率/输出质量样本。

## 未完成项

- AC2的状态记录/最终态统计基础已验证，未解决继续追问及其计次尚未开放。
- AC1真实修正阶梯及L3内容边界、AC3变式衔接仍待后续，不能只凭按钮占位认定完成。
- 真实诊断创建/识别/确认、模型/安全/预算与不少于20例一致性/盲评仍未验；诊断历史列表及运营统计报表也待接入。
- 无Mac/移动专项证据，G4完整验收仍0；新建/确认POST继续503。
