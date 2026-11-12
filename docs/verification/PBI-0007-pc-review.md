# PBI-0007 PC回显与HTTP切片验证 — 2026-11-12

状态：TASK-0019 in-verification；PBI-0007仍in-progress，TASK-0016完整集成仍draft，无G4或发布。

## 代码与环境

- API：task-0019-session-review / 169b50f，承接450a06b。
- Web：task-0019-session-review / 6ca6442（主体ad8c1cf，原文保真修复6ca6442），承接8d4ce81。
- 两组件工作区干净，未合main或推送。沿用CPython3.12.16、Node24.17.0与锁文件。
- API使用本机PGlite协议代理5432→5433/fakeredis等原开发依赖；HTTP成功读写证据来自ASGI应用实例及PG测试记录，未运行真实浏览器登录→识别→保存的完整端到端。
- Web回环3000开发服务已启动；临时生产3019已验证后停止。开发样例数据只在浏览器内存，明确显示“不是真实识别、不写数据库、不扣次数”。

## 自动化与构建

API执行ruff check src tests migrations、mypy src，设置INTEGRATION_DATABASE_URL后pytest -q。结果：

```text
Success: no issues found in 34 source files
183 passed in 9.76s
```

API新增test_review_routes.py5项，验证本人读取/白名单字段/no-store、非本人/非法ID404、无登录401、同源写保护、持久纠正/同键重放/版本冲突、生产无安全503、未配置confirm/reidentify不改状态且不访问额度。测试使用NoQuota，一旦触及额度即失败。

Web执行npm.cmd run check，lint、next typegen/tsc、Vitest及next build均通过：

```text
Test Files 9 passed (9)
Tests 71 passed (71)
Compiled successfully in 709ms
Finished TypeScript in 3.4s
Generating static pages using 7 workers (9/9) in 295ms
/session: Dynamic
/dev/session-review: Static (production notFound)
```

新增review.test.tsx15项，覆盖响应验证/非法ID不发请求、读取归属/缓存合同、同一保存键重试、409语义、识别503、三字段合并/清空考点/长度限制、AI标识与未开放按钮、考纲外与待识别不伪造结果。最后补C++尖括号/Markdown原文保真，避免题干被当HTML吞掉或转成外链。输入页新增useRouter后，原SSR测试补路由mock；最终全部71项执行通过。未运行远程CI。

## PC浏览器观察

IAB访问http://127.0.0.1:3000/dev/session-review，全部为显式合成样例，不能算真实识别或PG保存E2E。

- AI回显通过AiContent展示并有“AI生成”角标；用户修正输入区单独呈现。题干、逐行考点、候选级别0可修改保存，回显随之更新，创建时3级快照保留。
- 选择考纲外后出现“该题超出GESP考纲范围”及“通用编程问题、不针对考级”提示。
- 选择模拟版本冲突，保存提示其他页面已更新，完整修正仍在输入框；切换模拟连接失败仍保留；恢复正常后保存成功并清空修正表单，回显更新。
- 确认L1与重识别按钮均禁用，明确服务未开放；没有假讲解、假L2解锁或假额度。
- /session输入原题、代码、疑问并预览后，点击“识别题目”实际发请求。当前本机API连接不可用，显示“连接暂时不可用，输入已保留”，三字段及原文预览均保持；未跳到假会话。未据此宣称真实识别503链路浏览器通过，503合同由client/API测试覆盖。
- 390×844临时视口下clientWidth=scrollWidth=375，无横向溢出；恢复默认PC视口。仅做基础响应式DOM检查，未做移动专项验收。

证据：[PC回显截图（明确合成样例）](TASK-0019-review-desktop.png)、[浏览器快照](TASK-0019-review-browser.txt)。默认PC截图展示原型纸感布局、样例标记、AI角标与更新回显；保存/失败提示见快照与上列实测。

## 生产关闭检查

对临时next start生产3019进行真实HTTP请求：

```text
{path: /dev/session-review, production_status: 404, contains_fixture: False}
Stopped temporary production check
```

正常/session在生产继续显示服务未开放，不注入样例。API production local=False时capabilities.edit=False且POST echo返回503 safety_unavailable，避免用本机允许验证替代真实安全。

## AC映射与差距

| AC | 本轮证据 | 完整验收状态 |
|---|---|---|
| 1 教学级别与快照 | PC分别展示创建级别和候选；原冻结/重识别合同回归 | blocked：真实后续讲解与跨服务恢复未验 |
| 2 三字段纠正/确认前无讲解 | PC表单/AI回显、HTTP纠正落库与重放；未开放生成 | blocked：真实识别→PC→confirm→L1未连通 |
| 3 confirm计次/超限不推进 | 未配置入口503/NoQuota及已有确认回归 | blocked：真实生成/SSE/超限PC全链路未验 |
| 4 重识别回显 | 按钮禁用；既有内部资格/结算回归 | blocked：真实重识别及轮询UI未接入 |
| 5 重识别首次免费/失败释放 | 文案与已有内部测试 | blocked：实际请求/用量UI与生产环境未验 |
| 6 失败重试入口 | 连接失败/冲突不丢修正，读取重试/重新输入入口 | blocked：真实识别失败、重新上传入口未联调 |
| 7 识别失败免费 | 无配置不扣次，既有结算测试回归 | blocked：实际模型/安全失败链路未验 |
| 8 纠正留痕 | HTTP持久逐字段审计、幂等；PC表单合同通过 | blocked：真实浏览器登录会话保存和正式安全未验 |
| 9 路径/置信度 | API白名单不暴露内部路径；已有存储合同回归 | blocked：实际管线与指标未验 |
| 10 考纲外提示 | PC候选0级提示、保留创建级别 | blocked：真实判定及正式继续/SSE持续标注未验 |
| 11 P75首字≤5秒 | 无真实生成 | blocked：性能未测 |

DoD：本机规范/类型/自动化/生产构建、PC交互及文档通过；完整AC、真实服务E2E、安全/AI有效性、完整SSE/性能与发布仍未完成。本轮没有新增L1/L2/L3、追问或历史功能，不以回显页替代讲题闭环。
