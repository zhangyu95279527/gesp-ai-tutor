# PBI-0007 会话持久化基础验证 — 2026-11-12

状态：TASK-0015 in-verification，PBI-0007 in-progress；TASK-0016 draft；没有G4或发布。

## 环境与提交

- API：E:/AIworkspacke/gesp-tutor-api，task-0015-session-foundation / 02603a2，承接此前登录/资料/限额及输入合同全部增量。
- CPython3.12.16，锁文件未改变。INTEGRATION_DATABASE_URL使用本机5432代理→PGlite5433；已有回归使用fakeredis、本机邮件测试收件服务。生产PG/Redis并发未验。
- Web无改动、未重跑；本机8000服务未重启。没有新HTTP入口或公开成功创建；已有输入入口仍按缺配置拒绝。

## 命令与捕获结果

在API仓运行：

```powershell
$env:DATABASE_URL='postgresql://postgres:postgres@127.0.0.1:5432/postgres?sslmode=disable'
.venv/Scripts/python.exe -m alembic upgrade head
.venv/Scripts/ruff.exe check src tests migrations
.venv/Scripts/mypy.exe src
$env:INTEGRATION_DATABASE_URL=$env:DATABASE_URL
.venv/Scripts/python.exe -m pytest -q
.venv/Scripts/python.exe -m alembic current
```

最终输出：

```text
All checks passed!
Success: no issues found in 27 source files
........................................................................ [ 49%]
........................................................................ [ 99%]
.                                                                        [100%]
145 passed in 4.03s
0004_sessions (head)
```

新增tests/test_sessions.py共23项；专项先执行23 passed in 0.91s，随后完整145项无skip。首次规范检查有7处SQL长行，已排版修复后完成上述全回归。未执行远程CI、真实模型或生产部署。

## 基础合同证据

测试文件为API仓tests/test_sessions.py，数据均为随机owner UUID和显式合成识别夹具，不是真实识别产物。测试结束删除对应测试会话，关联question/operation由外键级联清理。

- 新建保留原题、代码、疑问点原样及账号级别快照；初始pending_recognition，没有original/draft_echo/final_level，不能将输入原文冒充识别题干。
- 创建同owner同键同输入重放返回原session_id；即使调用方后来传8级，原3级快照不变。同键换题409，不同owner键空间互不影响。
- 读取其他owner、缺失或非法会话ID都返回session_not_found/404；其他owner不能publish/edit，不泄露当前版本或内容。
- publish同事务保存识别题干/考点/判定级别/路径/置信度及draft_echo，才pending_confirm。重复发布同键重放不增版本；新键重复初次识别被状态检查拒绝。
- edit保存题干、考点、级别三字段纠正；每条含field、old、new、PG带时区时间、session_id。原始AI判定和账号快照不改；final_level仍NULL，不推进讲解或扣次。
- 同键不同纠正409、新键旧revision409；后续合法编辑完成后，重放此前操作仍返回其原revision/replayed，不重复纠正。当前内容通过get另读。
- 图片输入OCR路由与置信度持久保存；文本来源不能发布OCR路径。结构校验拒绝异常级别、空白考点、过长题干/考点、数量过多、无效OCR置信度及NaN。
- 重新构造SessionStore连接同一PG库可恢复输入、识别和纠正；将测试created_at设为两天前并将reidentify_count设2，重新构造后仍为2。这里只证明字段不被仓储初始化/读取重置，不代表已实现免费资格认领。
- 6个请求用4线程提交同一创建键，仅1个新建，其余重放。同一PGlite代理会排队连接，证据只覆盖本机并发请求下唯一键/事务行为，不是生产PG并行容量结论。
- 显式事务故障注入：更新后抛异常，重新读取revision仍0、操作记录0；相同键可重新合法发布到revision1。不是kill进程/连接丢ack演练。
- 仓储无额度、Redis、识别器或网关依赖；既有输入HTTP拒绝不触及额度的回归仍通过。完整confirm尚未实现，不宣称计次原子性验收。

## 逐条AC差距

编号按PBI-0007 acceptance_criteria的11条顺序。

| AC | 本轮证据 | 完整验收状态与差距 |
|---|---|---|
| 1 最终教学级别/首次免费不重赠 | 创建快照不改、编辑level与原判定分离、PG计数字段不初始化重置 | blocked：final_level冻结和重识别免费认领未实现 |
| 2 三字段可纠正/确认前无讲解 | 三字段draft_echo及纠正持久化，无生成调用 | blocked：真实识别、PC回显与confirm/L1尚未接入 |
| 3 confirm才计次/超限不推进 | 本基础不调用额度或推进L1 | blocked：confirm原子额度、超限与生成恢复尚未实现 |
| 4 同会话重新识别 | 仅初次publish状态合同 | blocked：重识别编排及重复回显UI未实现 |
| 5 首次免费/第二次起计次 | reidentify_count持久字段保留 | blocked：资格认领与额度联动未实现 |
| 6 失败提示/两种重试入口 | 无本轮UI交付 | blocked：真实失败及UI重试未验 |
| 7 识别失败不计次 | 状态/路由拒绝无额度依赖 | blocked：实际识别失败不扣次链路未验 |
| 8 corrections逐字段落痕 | 三字段旧/新值、PG时间、session_id及幂等测试通过 | blocked：真实用户UI纠正提交与安全检查未接入 |
| 9 route/confidence落库 | 合成text/ocr产物可恢复，结构/路由校验通过 | blocked：真实OCR/VL管线及识别指标取数未验 |
| 10 考纲外提示/通用讲解 | draft_echo级别0可保存且不覆盖快照 | blocked：真实考纲判定、用户二次确认及持续标注未验 |
| 11 P75首字≤5秒 | 无真实生成 | blocked：真实服务性能测量未执行 |

DoD：本机规范/类型/全回归、加法迁移和文档完成；所有完整AC、真实E2E、AI/内容安全有效性、运维保留/注销删除及生产恢复均未完成，不标done。数据库回退未执行，避免删除开发库数据；当前未部署，新增表的生产发布/回退须单独验证。
