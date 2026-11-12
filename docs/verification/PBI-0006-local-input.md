# PBI-0006 本机输入基础验证 — 2026-11-12

状态：TASK-0012 in-verification；完整PBI仍in-progress，TASK-0013 draft等待真实依赖。没有G4或发布。

## 可复核环境与命令

Web：E:/AIworkspacke/gesp-tutor-web，task-0012-unified-input / 8d4ce81；Node24.17.0，沿用锁文件。API本轮未改动，也未重跑后端测试。

在Web仓执行 `npm.cmd run check`，依次为eslint、next typegen/tsc、vitest、next build。首次lint发现effect同步setState和首页原生链接问题，已修复后完整重跑。最终输出：

```text
Generating route types...
✓ Types generated successfully
Test Files  8 passed (8)
Tests  56 passed (56)
Duration  2.98s
✓ Compiled successfully in 1060ms
Finished TypeScript in 3.2s
✓ Generating static pages using 7 workers (8/8) in 407ms
Route (app): /session
```

新增tests/input.test.tsx共16项：10000/10001题干、5000/5001代码、Unicode码点、10MiB/+1字节图片、空文件、PNG/JPEG/WebP与其他类型、过短输入、互斥来源、附加字段不冒充题干、剪贴板文件提取、开发文案与生产关闭表单。未运行远程CI。

## PC浏览器实测

入口http://127.0.0.1:3000/session，IAB浏览器，全部合成输入。

- 空题干点击预览：提示至少10字符，未进入预览。
- 填题干、C++代码、疑问：原文预览一致，识别按钮不可用；没有AI结果。
- 浏览器剪贴板Ctrl+V文字：准确进入题干。再粘截图时提示先清除文字，原文保留。
- 清除题目再Ctrl+V合成PNG：出现clipboard.png附件；可本地预览，未产生识别结果。
- 移除后通过文件选择器选择broken.png（无效字节）：提示图片无法读取，可改用文字；重选有效fixture.png后能再次预览。
- 清除题目不会丢失代码/疑问；编辑后旧预览关闭。截图blob由URL生命周期清理；客户端不调用fetch，不写本地持久存储。
- 临时390×844视口下DOM测得clientWidth=scrollWidth=375，无横向溢出；该模式截图发生浏览器缩放异常，因此仅记DOM检查，未据此宣称移动视觉验收通过。已恢复默认PC视口。

证据：[PC截图](TASK-0012-input-desktop.png)、[最终浏览器可访问性快照](TASK-0012-browser.txt)。测试图片仅用于文件处理检查，不是截图模糊识别证据。

## 完整AC证据差距

| AC | 本轮客户端证据 | 完整验收状态/差距 |
|---|---|---|
| 1 文字/截图同区即贴即传 | 两类真实Ctrl+V、来源保护 | blocked：尚未接上传及识别，当前仅本地预览 |
| 2 10000字/10MB限制 | 边界测试通过，错误可恢复 | blocked：服务端字节/大小校验及不进入识别待TASK-0013 |
| 3 文件选择/无直拍 | 真实选择器有效/损坏图片，accept白名单、无capture | blocked：对象存储上传与移动相册实际设备未验；DOM基础响应式已查 |
| 4 明显无效提示且不计次 | 过短、空/坏图片提示；无任何消费调用 | blocked：非题目语义/模糊检测、安全检查与真实用量集成未验 |
| 5 代码5000/疑问 | 边界测试与浏览器原文预览 | blocked：真实提交接口持久化与回显待TASK-0013 |

DoD：本地自动化及构建通过、文档与输入边界记录完成；完整AC、真实集成/E2E、安全服务及AI评估未通过，不能标done。小于10字符拒绝为显式实现假设；服务端不得依赖前端MIME或客户端校验，后续必须补充字节检测与对象归属。
