# FEAT-006 运营支撑 — 特性技术设计

Status: draft <!-- 文档生命周期: draft | in-review | approved | living | superseded -->
日期: 2026-10-23
覆盖 PBI: PBI-0019 / 0020 / 0021 / 0022
输入: Architecture Baseline（GA go 2026-10-23）、PRD 03/04/05、FEAT-006 各 PBI、FEAT-002 特性技术设计（埋点事件与安全串联的下游使用方）
受影响仓: gesp-tutor-api（主：modules/ops、core/safety、Langfuse 集成、Grafana 看板配置）、gesp-tutor-web（显式标识组件、拦截提示与申诉入口）、gesp-ai-tutor（本文档）

> 本文是 G3 判据 tech-design-ready 的输入。设计约束全部继承架构基线；超出基线的项集中在文末"基线缺口与开放决策"，按纪律路由 PO/GB，不在本文静默变更。
> 本文同时是 backlog Arch-3（横切合规机器可读化）的定稿载体：过滤 / 标识 / 埋点在此成为引擎与渲染层的默认行为，契约由本文定义，各会话类特性不再各自决策接入方式。

## 1. 范围与最小切片

本特性的最小技术切片 = 效果度量数据地基 + 合规横切层，四条线：

```
埋点   统一事件信封 → events 表 → Grafana 效果日报看板（NFR-REL-02 全指标 + 级别段×模块交叉）
盲评   抽样 CLI → Langfuse 标注队列 → 评分回写 → 仲裁 → 日报（BR-EVA / BR-VAR-2 / NFR-REL-03）
安全   core/safety 薄接口 → LLM 网关串联（输入前置 / 输出滑窗截断）→ 拦截留痕 → 邮件申诉入口
标识   web AiContent/AiBadge 组件族 → 全部 AI 展示位强制"AI 生成"角标、不可关闭
```

明确不做（本期）：

- 自研运营后台 UI：基线已定运营入口为 Grafana / Langfuse（各自账号体系、邀请制），不建第三套。
- 分享卡片图片角标与 EXIF/XMP 隐式标识：随 FEAT-004 暂缓；恢复时的落地规格登记于 §10-D3。
- 体验转化漏斗的"注册引导"交互属 PBI-0013；本文仅定义漏斗事件契约（§3.1）与取数口径（§5.4）。
- 日报的调度基础设施：不引入调度组件；日报产出动作初期由人工/主机 cron 触发 CLI（§4），看板实时可查。

## 2. 组件落位与模块边界

```
api（FastAPI 单体）
 ├─ modules/ops/            事件记录（record_event 进程内接口）；events / blind_eval_*
 │                          表所有权；盲评抽样与评分回写 CLI；效果日报 SQL 与 CLI 渲染
 ├─ core/safety/            内容安全薄接口（check_text / check_image，阿里云内容安全为首期实现）；
 │                          safety_blocks 表所有权
 ├─ core/llm/               安全串联与埋点接入点：输入前置过滤、输出滑窗送检器
 │                          （管道规格在 §6.1 定稿，FEAT-002 已定位其调用位）
 └─ core/session/           会话框架状态机钩子统一发会话域事件（§6.1），并填充 module/level_band

web（Next.js）
 ├─ components/ai/          AiContent / AiBadge：AI 生成内容的唯一渲染入口（§3.4）
 └─ 拦截提示组件            safety_blocked / safety_truncated 提示 + 邮件申诉入口（mailto）

可观测性服务组
 ├─ Grafana                 效果日报看板（dashboard JSON provisioning，存 api 仓部署目录）
 └─ Langfuse                盲评标注队列与评分（工具自带账号体系，基线身份/安全节既定）
```

数据表所有权（对齐基线"模块拥有各自数据表、跨模块只走进程内接口、不联表"）：

| 表 | 所有者 | 说明 |
|---|---|---|
| events | modules/ops | 埋点事件，日报与漏斗数据源（基线数据节已列） |
| blind_eval_samples / blind_eval_scores | modules/ops | 盲评抽样与评分（基线数据节已列） |
| safety_blocks | core/safety | 拦截留痕（申诉核查上下文）。本表为基线"主要实体"清单之外的新增，属基线声明的"字段级设计在各特性技术设计中完成"范畴，不改稳定边界，不路由 GB |

跨模块纪律：会话框架 / lmt / acc 等只经 record_event 写事件，不直连 events 表；盲评抽样对会话域表（ai_sessions / session_steps / session_messages / variant_attempts）为只读查询（抽样是运营分析动作，只读不构成所有权违反；会话表所有权仍属 core/session）。

## 3. 接口契约

### 3.1 埋点事件（modules/ops 进程内接口）

```python
class EventRecorder(Protocol):
    def record(self, event: Event) -> None: ...

@dataclass
class Event:
    event_type: str            # 事件目录内注册的类型名
    owner_type: Literal["user", "guest"]
    owner_id: str              # user_id 或访客指纹 hash
    session_id: str | None     # 会话域事件必填（AC3 对账依据）
    module: str | None         # tut / dia / exa / acc / lmt / ops / shr
    level_band: Literal["1-4", "5-8"] | None
    props: dict                # 事件特定属性
```

写入纪律：

- 同步插入；写失败仅记日志与 `event_record_failures` 计数指标，**不阻断业务流**（度量完整性让位于用户旅程，失败率入 Grafana 监控）。
- 会话域事件的 `module` / `level_band` 由会话框架统一填充（取 ai_sessions.type 与 level_snapshot 派生），调用方不传；账号域事件由 acc 模块按 users 所报级别填充；访客事件允许 level_band 为空。
- 事件类型必须先登记入目录再发射，record 对未登记类型拒绝并告警——目录即契约，防止各特性私造事件导致日报口径漂移。

事件目录（本特性定义的契约；生产者分布于各特性，FEAT-002 §6.3 清单全部继承）：

| event_type | 生产者 | 关键 props | 日报用途 |
|---|---|---|---|
| session_started / echo_confirmed / ladder_unlocked(level) / followup_asked / understood_marked / variant_pushed / variant_answered(correct) | core/session（FEAT-002/003/007） | 见 FEAT-002 §6.3 | 会话数、解锁深度、轮次、听懂率、变式做对率 |
| recognition_succeeded(route) / recognition_failed(reason) / echo_corrected / reidentify_used / ladder_compliance_violation(level) / ocr_fallback | core/session | route / reason / level | 质量过程指标 |
| guest_experience_started / guest_experience_completed | core/session（FEAT-001 体验模式编排按本契约发射） | sample_question? | 体验漏斗前两步 |
| user_registered | acc（FEAT-001，PBI-0013 承接） | guest_fingerprint?（归因） | 漏斗终点 |
| quota_rejected(action) | modules/lmt（FEAT-005） | action | 触顶率、触顶次日留存 |
| safety_blocked(stage, category) / safety_truncated(category) | core/safety / core/llm | stage=input/output、命中类别 | 安全拦截率 |

`ladder_unlocked`、`variant_answered`、`understood_marked` 等关键事件必须携带 session_id，保证与盲评导出数据可对账（PBI-0019 AC3）。

### 3.2 内容安全（core/safety 薄接口 + 输出滑窗送检器）

```python
class ContentSafety(Protocol):
    def check_text(self, text: str, scene: SafetyScene) -> SafetyVerdict: ...
    def check_image(self, image_ref: str, scene: SafetyScene) -> SafetyVerdict: ...

@dataclass
class SafetyVerdict:
    passed: bool
    category: Literal["politics", "porn", "violence", "bullying", "other"] | None
    vendor_label: str | None   # 厂商原始标签，留痕用
```

- 首期实现：阿里云内容安全（同 region 内网 endpoint，基线集成节既定）；切换厂商 = 新增接口实现类 + 配置，应用代码零改动。
- `scene` 枚举：`tut_input / dia_input / followup / variant_answer / llm_output / image_recognition`，用于拦截日志归因与分类统计。
- 超时与失败口径：输入检测 3s 超时，输出滑窗检测 2s 超时；**均 fail-closed**——输入超时按拦截处理（提示稍后重试），输出检测超时/不可用按命中处理（截断）。理由：NFR-SAFE-01 是未成年人产品的合规底线，不可 fail-open；代价是内容安全服务不可用即 AI 会话不可用，与基线告警表"内容安全服务不可用 = P1 立即"一致。置信度 80。
- 输出滑窗送检器（位于 core/llm，对 SSE 分片流工作）：
  - 累积分片，每满 W=200 字符且在句读边界切窗，相邻窗保留一句重叠（防跨窗断词漏检）；逐窗异步送检。
  - 命中 → 立即中止上游 LLM 流 → 下发 `safety_truncated` 事件 → 已发分片落库并标记 `safety.truncated=true`；尾包在流结束时终结送检。
  - W=200 为初始值，联调期按误拦率与"截断前上屏量"权衡校准（§10-D4），校准只改配置。
- 输入侧接入点（FEAT-002 §6.1 已定，本文确认不变）：所有用户文本与截图经 check_text / check_image 前置，命中 → 422 `safety_blocked`，不计数，写 safety_blocks。
- 申诉入口：拦截与截断提示组件固定展示申诉邮箱 mailto 链接（配置 `OPS_APPEAL_EMAIL`），文案含拦截时间与类别说明以便核查；无后端接口（FR-OPS-03 证据 = UI 检查）。

### 3.3 盲评（modules/ops ↔ Langfuse）

抽样与导出（运营动作，CLI 形态，不建 UI）：

```bash
docker compose exec api python -m modules.ops.blind_eval sample \
    --mode iteration --iteration-tag <tag>   # BR-EVA：重大迭代后抽 30 个
docker compose exec api python -m modules.ops.blind_eval sample \
    --mode daily                             # NFR-REL-03：当日随机 10 个，同一入口
docker compose exec api python -m modules.ops.blind_eval sync    # 评分回写 + 仲裁
```

- 候选集：存在 L1 讲解消息（ladder_l1）且自上次 iteration 抽样之后创建的 ai_sessions；`--mode iteration` 按 级别段（1-4/5-8）× 模块（tut/dia）四层分层随机，每层 ≥6，余量由各层按比例补齐至 30；某层不足 6 个则全取并在批次元数据记 `shortfall`（导出清单证据中可见）。同一会话不重复入 iteration 批次。
- 导出动作：对每个样本，按字段白名单（§5.2）从会话域表捞取评分所需完整上下文，快照写入 `blind_eval_samples.context`，同一份内容写入该会话各 Langfuse trace 的 metadata 并将 trace 加入标注队列。会话 ↔ trace 经 session_messages.llm_trace_id 关联（FEAT-002 §5.1 已建该字段）。
- 评分录入：教练在 Langfuse 标注队列打分（基线可观测性节既定入口）；`sync` 经 Langfuse API 拉取 scores 写入 blind_eval_scores。Langfuse 具体 API 端点与队列对象为部署版本相关实现细节，任务分解时按所部署版本文档定稿，不构成本文契约变更。
- 评分模型（PBI-0020 AC 两维度独立计分 与 BR-EVA-3/BR-VAR-2 的整合）：
  - **引导效果组**（数值 1–5）：引导性、正确性、级别贴合度、表达与安全（BR-EVA-3 四子维度）。2 名教练独立评分取均值；单维度分差 >1 → 第三人复评，终值取三人中位数并标 arbitrated。金标准"盲评均分 ≥3.5"= 引导效果组四子维度全样本均值。
  - **变式题质量组**（档位）：难度校准 相当/偏易/偏难（BR-VAR-2），两名教练档位不一致 → 第三人裁定取多数档。"偏易"占比 >20% 触发 prompt 回炉（BR-VAR-2），该占比入日报。
  - 两组独立归因：讲解效果差与题目质量差互不污染（PBI-0020 AC 的设计意图）。

### 3.4 AI 生成内容显式标识（web 组件契约）

- `components/ai/AiContent`：所有 AI 生成文本/Markdown 的**唯一渲染入口**，内部固定渲染 `<AiBadge />`（"AI 生成"角标），不提供关闭 prop；结构化 AI 内容位（变式题卡片、诊断结论卡）以 `<AiBadge />` 直接标注。
- 覆盖清单（PBI-0022 AC 逐页检查单即据此执行）：讲题会话页（含历史回看）、诊断结果页（FEAT-003 落地时接入同一组件）、变式题卡片、模考讲评（P1 接入时复查补勾）；考纲外"通用讲解"标注与 AI 标识并存、互不替代。
- 强制执行手段：
  1. 组件内聚：badge 是渲染器内部行为，不是调用方选项；
  2. 依赖约束：ESLint `no-restricted-imports` 禁止会话/诊断/模考页面绕过 AiContent 直接导入底层 Markdown 渲染器；
  3. 组件测试断言 badge 渲染存在；逐页检查单作为 G4 证据。

## 4. 对外接口

本特性无新增用户侧 REST 接口。运营面入口：

| 入口 | 形态 | 说明 |
|---|---|---|
| Grafana 效果日报看板 | dashboard JSON provisioning（api 仓 `deploy/grafana/`） | PG 只读数据源账号；看板 = NFR-REL-02 全指标 + 盲评组（§5.4） |
| 日报留档 CLI | `python -m modules.ops.daily_report --date <d>` | 复用看板同一组 SQL，渲染 markdown 快照，供"日报输出样例核对"（PBI-0019 AC1 证据）与复盘留档；每日产出动作初期人工/cron 触发 |
| 盲评 CLI | §3.3 | sample / sync |
| Langfuse 标注队列 | 工具自带 UI | 教练打分入口（基线既定） |
| 申诉入口 | 前端 mailto | §3.2 |

## 5. 数据设计（字段级）

### 5.1 events（modules/ops 所有）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid PK | |
| occurred_at | timestamptz | 默认 now()；日报按日聚合依据 |
| event_type | text | §3.1 目录内注册类型 |
| owner_type | enum(user,guest) | |
| owner_id | text | user_id 或访客指纹 hash（不存原始指纹） |
| session_id | uuid? | 会话域事件必填；关联 ai_sessions |
| module | enum(tut,dia,exa_review,acc,lmt,ops,shr)? | 模块维度（AC2 交叉查询一轴）；会话域事件取值对齐 ai_sessions.type 枚举 |
| level_band | enum('1-4','5-8')? | 级别段快照（AC2 另一轴），发射时派生固化为列，避免日报查询回联 users/ai_sessions |
| props | jsonb | 事件特定属性（route/reason/level/correct/category...） |

索引：`(occurred_at)`、`(event_type, occurred_at)`、`(owner_type, owner_id, occurred_at)`（次日留存与去重活跃）、`(session_id)`（盲评对账）。

### 5.2 blind_eval_samples / blind_eval_scores（modules/ops 所有）

**blind_eval_samples**

| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid PK | |
| batch_id | uuid | 一批抽样（同一次 sample 命令） |
| mode | enum(iteration,daily) | BR-EVA / NFR-REL-03 |
| iteration_tag | text? | 重大迭代标识（prompt 版本/模型变更/新模块） |
| session_id | uuid | 抽样会话 |
| level_band | enum('1-4','5-8') | 分层属性快照 |
| module | enum(tut,dia) | 分层属性快照（exa_review 随 P1 扩展枚举） |
| layer_shortfall | bool | 所在分层不足 6 个的全取标记 |
| context | jsonb | 导出上下文快照（白名单字段，见下） |
| exported_by / created_at | text / timestamptz | 操作留痕 |

`context` 白名单字段（PBI-0020 AC2 评分上下文 + AC4 字段审计证据）：

```
session_id, level_snapshot, module,
steps[]      阶梯解锁留痕（ladder_level, unlocked_at）
messages[]   逐轮内容（seq, role, kind, content, ladder_level, prompt_version）
variant      变式题题面 / 首次作答 / 判读对错 / validated
明确不含：邮箱、昵称、出生年月、设备指纹、IP、oss_key 原文（图片以 Langfuse trace 内既有引用为准，不另行导出）
```

**blind_eval_scores**（原始评分，只追加不更新）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid PK | |
| sample_id | uuid FK→blind_eval_samples | |
| evaluator | text | 教练标识（Langfuse 账号名；仲裁人同列区分） |
| dimension | enum(guidance,correctness,level_fit,expression_safety,variant_difficulty) | 前四为引导效果组（数值），末为变式题质量组（档位） |
| score_num | smallint? | 1–5，引导效果组 |
| score_label | enum('相当','偏易','偏难')? | 变式题质量组 |
| comment | text? | 自由评语 |
| synced_at | timestamptz | 回写时间 |

终值不物化，由 SQL 视图 `blind_eval_final` 计算：每 sample × dimension，无仲裁取 2 人均值，有仲裁取 3 人中位数；变式题质量组取多数档。日报与 Grafana 直接查视图，避免回写计算状态与原始评分漂移。

### 5.3 safety_blocks（core/safety 所有）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid PK | |
| occurred_at | timestamptz | 拦截时间（PBI-0021 AC2） |
| owner_type / owner_id | enum(user,guest) / text | 账号；访客记设备标识 hash（AC2） |
| stage | enum(input,output) | 输入拦截 / 输出截断 |
| content_type | enum(text,image) | 命中内容类型（AC2） |
| category | text | 命中类别：politics/porn/violence/bullying/other + vendor_label 入 props（AC2） |
| scene | text | §3.2 SafetyScene |
| session_id | uuid? | 关联会话（申诉核查定位） |
| excerpt | text | 命中片段截断留存（≤500 字符；图片存 oss_key 引用不落图） |
| trace_id | text? | OTel trace，串联日志与 Langfuse |

索引：`(occurred_at)`、`(owner_type, owner_id, occurred_at)`（申诉核查按人查）。保留期对齐 NFR-DATA-02（至 2027-01 考后复盘完成）。

### 5.4 效果日报取数口径（PBI-0019 AC1 逐指标映射）

| 指标 | 数据源与口径 |
|---|---|
| 活跃用户（按天去重） | events：当日 distinct (owner_type='user', owner_id) |
| 会话数 | ai_sessions 按 created_at 日聚合，按 type 分列 |
| 阶梯解锁深度分布 | session_steps：每会话 max(ladder_level) 的当日分布 |
| 变式题首次做对率 | variant_attempts.first_correct 当日均值 |
| 听懂标记率 | 当日完成 L1 的会话中 understood_at 非空占比 |
| 会话轮次分布 | session_messages 中 role='user' 且 kind∈(followup_q, variant_answer) 的每会话计数分布 |
| 限额触顶率 | 当日有 quota_rejected 的 distinct 注册用户 / 当日活跃用户（访客额度触顶属漏斗范畴，另列） |
| 触顶用户次日留存率 | D 日触顶用户中 D+1 有任一事件者占比；同看板并置"当日活跃未触顶用户次日留存"对照（NFR-REL-02 回审 O3 的判据） |
| 体验转化漏斗 | 当日 guest_experience_started（设备去重）→ guest_experience_completed → 同批指纹 7 日内 user_registered 归因转化（归因窗口见 §10-D2） |
| 盲评均分 / 偏易占比 | blind_eval_final 视图按 batch/iteration_tag 聚合（PBI-0020 AC"进日报"） |

级别段 × 模块交叉查询（AC2 证据形态，Grafana 同构 panel）：

```sql
SELECT date(occurred_at) AS d, level_band, module, event_type, count(*)
FROM events
WHERE level_band IS NOT NULL
GROUP BY 1, 2, 3, 4
ORDER BY 1 DESC, 2, 3, 4;
```

关键事件一致性抽查（AC3 证据形态）：以 session_id 对 join events 与会话域表，验证解锁留痕 / 变式首答双侧一致：

```sql
SELECT e.session_id, e.event_type, e.props, s.ladder_level, s.unlocked_at
FROM events e JOIN session_steps s
  ON s.session_id = e.session_id AND s.ladder_level = (e.props->>'level')::int
WHERE e.event_type = 'ladder_unlocked' AND e.occurred_at >= current_date - 1;
```

## 6. 横切集成（Arch-3 合规横切层定稿）

### 6.1 LLM 网关管道（默认行为，调用方零决策）

```
模块调用 LLM 网关
 → 输入内容安全前置（core/safety.check_text / check_image，命中即拒，写 safety_blocks + safety_blocked 事件）
 → 生成（流式）
 → 输出滑窗送检（命中截断，写 safety_blocks + safety_truncated 事件）
 → 落库（safety 记录入 session_messages.safety，FEAT-002 §5.1 字段已预留）
 → Langfuse trace + token 计量
```

任何模块（tut/dia/exa_review）经网关调用即获得过滤 + 计量 + trace，不存在"忘记接安全"的路径。埋点同理：会话框架状态机转移钩子（确认 / 解锁 / 追问 / 听懂 / 变式 / 关闭）内置 record_event 调用，module 与 level_band 由框架填充——事件发射是会话框架的默认行为，不是各 PBI 的可选动作。

### 6.2 渲染层标识（默认行为）

AI 内容渲染唯一入口 AiContent（§3.4），标识为渲染默认行为；ESLint 约束封堵绕过路径。两者合起来回应 Arch-3：过滤 / 标识 / 埋点成为引擎与渲染层默认行为。

### 6.3 可观测性增量

- 指标新增：`event_record_failures`（埋点写入失败率）、内容安全检测延迟与拦截率（按 stage × category × scene）、滑窗送检漏出风险监控（截断发生轮次分布）、盲评 sync 成功率。
- 告警沿用基线分级：内容安全服务不可用 = P1；日报数据源（PG 只读账号 / Grafana）不可用 = P2；盲评 sync 连续失败 = P3。
- 内容安全拦截单独日志流（基线日志节既定），safety_blocks 为可查询留痕，二者经 trace_id 互相关联。

## 7. 安全与合规

- 盲评导出最小化：白名单字段（§5.2）不含任何身份字段；导出访问受控——Langfuse 邀请制账号（基线身份/安全节），样本数据落库可审计（exported_by）。字段白名单由测试强制（§9），防止后续迭代混入身份字段。
- safety_blocks 仅经 DB / 日志后台访问，无用户侧接口；申诉核查动作为人工查询，不留自动化数据出口。
- 未成年人：本特性不新增个人信息收集；events / safety_blocks 中的 owner_id 访客侧为指纹 hash，不可逆。
- 数据保留：events / safety_blocks / blind_eval_* 对齐 NFR-DATA-02（保留至 2027-01 考后复盘完成，之后按隐私政策执行）。
- 密钥：内容安全 / Langfuse API 凭据环境变量注入，不入仓（基线纪律）。

## 8. 失败行为矩阵

| 场景 | 行为 | 度量影响 |
|---|---|---|
| 内容安全 API 超时/不可用（输入侧） | 按拦截处理，提示稍后重试；P1 告警 | 记 safety_blocks（category=unavailable） |
| 内容安全 API 超时/不可用（输出侧） | 流截断 + `safety_truncated` 事件；P1 告警 | 同上 |
| 输入命中 | 422 safety_blocked + 申诉邮箱提示；不计数（FEAT-002 §8 既定） | safety_blocked 事件 |
| 输出命中 | 截断 + 提示 + 申诉邮箱；计数照计（FEAT-002 §8 既定） | safety_truncated 事件 |
| events 写失败 | 日志 + event_record_failures 计数，业务流继续 | 失败率入看板 |
| 抽样候选不足（某层 <6） | 全取 + shortfall 标记，导出清单可见 | 不阻塞批次 |
| Langfuse 不可用（sample push） | CLI 报错退出可重跑（幂等：同 iteration_tag 重跑跳过已入队会话） | — |
| Langfuse 评分 sync 失败 | 下次 sync 重试（按 synced_at 增量）；连续失败 P3 告警 | — |
| Grafana / PG 只读账号异常 | 看板不可用，日报 CLI 同样失败；P2 告警当日处理 | — |

## 9. 测试策略

- 单测（api，pytest）：
  - 事件信封校验：未登记类型拒绝；会话域事件缺 session_id 拒绝；level_band 派生（level_snapshot 1/4/5/8 边界）。
  - 滑窗送检器：窗口切分（句读边界、重叠）、命中截断时序、尾包终结送检、检测超时按截断处理。
  - 抽样分层：构造数据集验证四层各 ≥6、余量补齐至 30、shortfall 标记、同会话不重复入批次。
  - 仲裁与终值视图：分差 ≤1 取均值、>1 三人中位数、变式档位不一致取多数档的 SQL 视图用例。
  - 日报 SQL：fixture 数据集逐指标对拍（含触顶次日留存的对照组并置）。
- 集成：Langfuse push / sync 以 stub server 验证契约与幂等重跑；Grafana 看板 SQL 在联调库跑通（provisioning JSON 载入即冒烟）。
- 审计测试：盲评导出白名单强制——context 快照键集合与身份字段黑名单双向断言（防迭代混入邮箱/昵称/指纹）。
- 内容安全用例集：违规样例库（涉政/涉黄/暴力/欺凌各类别正反例）存 api 仓 `tests/fixtures/safety/`，联调环境对真实内容安全 API 回归（PBI-0021 AC1 拦截验证证据）。
- 前端：AiContent 组件测试（badge 存在、无关闭入口）；ESLint 约束生效验证；逐页检查单（讲题/诊断/变式，模考讲评 P1 补）作为 G4 证据。

## 10. 基线缺口与开放决策

无 GB/ADR 项：全部设计在基线稳定边界内——无新外部依赖（Langfuse / Grafana / 内容安全均为基线既定组件）、无部署形态变化；safety_blocks 为基线"主要实体"清单的字段级补全。

| 编号 | 事项 | 建议 | 路由 | 置信度 |
|---|---|---|---|---|
| D1 | BR-EVA-4 未定仲裁终值规则 | 终值取三人中位数（确定性、抗极端分）；变式档位不一致取多数档 | PO 确认（非阻塞，规则已按本建议写入 §3.3/§5.2） | 75 |
| D2 | 漏斗"体验完成"与注册归因窗口口径 | 体验完成 = 会话内出现 understood_marked 或 variant_answered 之一（质量信号明确）；注册归因窗口 7 日（同日注册为主，留跨日余量） | PO 确认（非阻塞；PBI-0012/0013 发射事件时按本口径） | 70 |
| D3 | 分享卡片角标与 EXIF/XMP 隐式标识（随 FEAT-004 恢复时落地） | 卡片图生成时写入 XMP 元数据 AIGC 标记（隐式）+ 图片右下角"AI 生成"角标（显式，FR-OPS-04 含分享卡片位）；由 FEAT-004 技术设计承接，本文不建 | 登记，FEAT-004 恢复时生效 | 85（与基线集成节既定方案一致） |
| D4 | 输出滑窗 W=200 初始值 | 联调期按误拦率与截断前上屏量实测校准，只改配置 | 任务分解定稿 | 70 |

## 11. G3 追踪

| PBI | 本文覆盖节 | AC → 证据映射 |
|---|---|---|
| PBI-0019 效果度量埋点与日报 | 3.1 / 4 / 5.1 / 5.4 / 6.1 | AC1 = 看板 + 日报 CLI 样例（§5.4 逐指标口径）；AC2 = §5.4 交叉查询 SQL；AC3 = §5.4 一致性抽查 SQL + §3.1 关键事件 session_id 强制 |
| PBI-0020 盲评抽样导出与结果录入 | 3.3 / 5.2 / 7 / 9 | AC1 = 分层抽样单测与导出清单（shortfall 可见）；AC2 = context 白名单字段（§5.2）；AC3 = 两维度评分模型 + 仲裁视图 + 日报 panel；AC4 = 白名单审计测试 + Langfuse 访问控制 |
| PBI-0021 AI 内容安全过滤 | 3.2 / 5.3 / 6.1 / 8 / 9 | AC1 = 安全用例集回归；AC2 = safety_blocks 字段（时间/账号/内容类型/命中类别）；AC3 = 拦截提示组件 mailto 申诉入口 |
| PBI-0022 AI 生成内容显式标识 | 3.4 / 6.2 / 9 | AC1/AC2 = 逐页检查单（讲题/诊断/变式；模考讲评 P1 接入时复查）+ 组件测试 + ESLint 约束；分享卡片位随 FEAT-004 恢复（§10-D3） |
