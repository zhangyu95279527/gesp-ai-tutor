# FEAT-002 AI 讲题 — 特性技术设计

Status: draft <!-- 文档生命周期: draft | in-review | approved | living | superseded -->
日期: 2026-10-23
覆盖 PBI: PBI-0006 / 0007 / 0008 / 0009 / 0010 / 0011
输入: Architecture Baseline（GA go 2026-10-23）、PRD 02/03/04/05、FEAT-002 各 PBI
受影响仓: gesp-tutor-api（主）、gesp-tutor-web（会话页/输入组件/SSE 消费）、gesp-ai-tutor（本文档）

> 本文是 G3 判据 tech-design-ready 的输入。设计约束全部继承架构基线；超出基线的项集中在文末"基线缺口与开放决策"，按纪律路由 GB/ADR 或 PO 决策，不在本文静默变更。

## 1. 范围与最小切片

本特性的最小技术切片 = 一条可跑的 J1 主链路：

```
统一输入 → 识别（OCR-first 管线）→ 回显确认 → L1 流式讲解 → 手动解锁 L2/L3
→ 会话内追问 → 听懂标记 → 变式题检验 → 历史回看/继续追问
```

横切贯穿：限额计数（BR-LMT）、内容安全双向过滤（NFR-SAFE-01）、LLM 全量观测（Langfuse）、埋点（FR-OPS-01 取数）。

明确不做（本期）：
- 分享卡片（FEAT-004 暂缓）；J1 第 7 步入口不建。
- 诊断入口（FEAT-003）与模考讲评入口（FEAT-007）：本设计把 AI 会话框架做成三入口共用，但仅落地 TUT 入口编排；DIA/EXA 的入口编排在各自特性技术设计中定稿。
- 邀请码/注册/体验模式编排（FEAT-001）；本文仅定义会话框架对"访客会话"的承载接口点（见 5.3、6.2）。

## 2. 组件落位与模块边界

```
web（Next.js）
 └─ 讲题会话页（CSR）+ 统一粘贴组件 + SSE 消费（fetch + ReadableStream，POST 流式）

api（FastAPI 单体）
 ├─ modules/tut/            TUT 入口编排：REST/SSE 路由、请求校验、调用框架层
 ├─ core/session/           AI 会话框架（本设计核心）：状态机、识别管线编排、
 │                          阶梯引擎、追问、变式题、历史回看；拥有会话域数据表
 ├─ core/llm/               LLM 网关：prompt 模板组装、流式输出、结构化校验、
 │                          token 计量、内容安全串联、Langfuse trace
 ├─ core/ocr_client/        ocr 服务内网 HTTP 客户端（含降级逻辑）
 ├─ core/safety/            内容安全薄接口封装（check_text / check_image）
 ├─ modules/lmt/            限额服务：计数判定与流水（进程内接口，见 6.2）
 └─ modules/ops/            埋点事件写入（events 表，进程内接口）

ocr 服务（自托管容器）       PP-OCRv4 / RapidOCR，POST /v1/recognize
```

数据表所有权（对齐基线"模块拥有各自数据表、跨模块只走进程内接口、不联表"）：

| 表 | 所有者 | 说明 |
|---|---|---|
| questions / ai_sessions / session_steps / session_messages / variant_attempts | core/session（AI 会话框架） | TUT/DIA/EXA 三入口共用，框架层持有；模块侧按 session_id 引用 |
| quota_usage（+ Redis 计数键） | modules/lmt | 框架层经进程内接口调用，不直连表 |
| events | modules/ops | 框架层经进程内接口写入 |

框架层（core/*）在基线组件表中即"AI 会话框架 / LLM 网关"两个子组件，不是新业务模块；未来拆服务时按"tut/dia/exa 各自带框架副本或框架独立成服务"在阶段 4 评审，当前进程内调用。

## 3. 接口契约（Arch-1 移交项）

### 3.1 引导引擎 ↔ LLM 网关（进程内契约，本特性最核心的契约）

```python
class LlmGateway(Protocol):
    def stream_chat(self, req: StreamChatRequest) -> Iterator[ChatChunk]: ...
    def structured_chat(self, req: StructuredChatRequest) -> StructuredResult: ...
```

- `StreamChatRequest`：`template_id`（prompt 模板标识）、`template_vars`（见下）、`session_ctx`（会话上下文引用）、`safety`（输入送检结果句柄）、`observer`（Langfuse trace / OTel span 上下文）。
- `ChatChunk`：`delta`（文本分片）、`meta`（prompt_version、首 chunk 标记）、终态携带 `usage`（input/output tokens、缓存命中）。
- `StructuredChatRequest`：额外携带 `json_schema` 与 `max_retries=1`；`StructuredResult` 为校验通过的结构化对象或 `SchemaError`（重试耗尽后抛出）。
- 模板版本管理：prompt 模板以文件存于 api 仓 `core/llm/prompts/`，版本号 = 模板文件 git sha + 模板内声明的 `version`；每次调用将 `template_id + version` 写入 Langfuse trace 与 session_messages.prompt_version，支撑盲评回溯与 A/B 对比。

提示词组装规则（阶梯状态注入）：

| 槽位 | 内容 | 来源 |
|---|---|---|
| system | 角色设定 + BR-GUD 阶梯定义 + BR-LVL 级别约束 + 语气规则（BR-GUD-5） | 模板固定 |
| level_syllabus | 本会话确认级别的考纲摘要；0 表示考纲外，不套用 1–8 级考纲 | questions.final_level（确认后冻结） |
| ladder_state | 当前阶梯与"允许输出边界"（L1 禁步骤禁代码；L2 禁完整代码；L3 全量） | 状态机当前态 |
| question_context | 识别后题目文本 + 考点 + 代码片段/疑问点（如有） | questions + 会话创建输入 |
| history | 会话内逐轮消息（图片首轮已转文本，后续轮次不带图，NFR-COST-03） | session_messages，超窗口截断策略见 3.4 |
| user_input | 本轮用户输入（追问文本/解锁指令上下文） | 当次请求 |

输出结构化校验（网关层强制）：

1. **识别结果**（structured_chat）：schema = `{question_text, knowledge_points[], judged_level(1-8 | "out_of_syllabus"), confidence(0-1), completeness("complete"|"partial"|"failed")}`。校验失败重试 1 次 → 仍失败触发 VL 升级（截图路径）或判定识别失败（文本路径/VL 已失败）。
2. **变式题**（structured_chat）：schema = `{stem, ref_answer, ref_solution_code, test_data[{input, expected_output}], judge_mode("ai_read"|"exact_match")}`。校验失败重试 1 次 → 仍失败则本次变式生成失败（不计数，见 6.2）。
3. **L1/L2 用户可见前校验**：L1/L2 正文及同阶梯追问先完整缓冲候选，不向 SSE、续传缓存或历史消息发布未经校验的候选。校验 L1 无实现步骤、L1/L2 无完整可提交代码；代码特征规则只作为防线，须用答案泄露评测集验证，不能宣称启发式可证明语义正确。违规丢弃候选并重生成 1 次；仍违规时只返回预置的无答案提示，写质量事件 `ladder_compliance_violation`，不放行截断的违规候选。L3 可含代码，仍须内容安全检测。
4. L1/L2 校验通过后按片段 SSE 交付；每个片段须内容安全检查通过才发布。L3 可以边生成边检查片段，检查通过再发布。候选重试和缓冲时间均计入用户首个可见正文字延迟，不以 meta/占位事件代替 TTFT；NFR-PERF-01 的 P75 ≤5s 不变，若实测不达标须优化或提交显式变更，不以内部模型首 token 冒充达标。

### 3.2 识别管线编排（OCR-first + VL 升级）

```
文本输入 → 直接 structured_chat 结构化（不走 OCR）
截图输入 → ocr_client.recognize(oss_key) → {text, confidence}
          → 路由判定：
            ├ confidence ≥ TH_OCR（初始 0.85，A-Q6 评测集定稿）→ GLM 文本结构化
            │   └ 结构化校验失败 / completeness=partial 且含公式图表特征 → 升 VL
            └ confidence < TH_OCR → GLM-5.3-Flash 多模态直读原图（base64 内联）
用户纠正后重识别 → 一律走 VL 通道（基线管线既定）
ocr 服务不可用/超时（10s）→ 降级 VL 通道 + 记录 ocr_fallback 指标
```

- ocr 客户端契约：`POST {ocr_endpoint}/v1/recognize`，请求 `{image_ref}`（内网可访问的对象引用或字节流），响应 `{text, confidence, blocks[]}`；超时 10s，无重试（降级 VL 即其失败行为）。
- VL 通道图片传递：api 从 OSS 私有桶内网 GET 原图 → base64 data URI 内联进 GLM 请求；不向 GLM 签发外部可访问 URL（缩小泄露面）。
- 识别产物落 questions 表（含 route 标记 text/ocr/vl、ocr_confidence），供 A-Q6 命中率回归统计。

### 3.3 会话状态机

```
                 ┌────────────────────────────┐
 创建(识别) ─→ pending_confirm ─确认─→ l1_active ─解锁─→ l2_active ─解锁─→ l3_active
                 │  纠正重识别(不限次数)    ▲                                  │
                 └──────────┘            └── 追问(followup, 任意阶梯, 不改变状态) ┘
  l1/l2/l3_active ─听懂标记/主动发起─→ variant_pending ─作答判读─→ variant_done
  任意态 ─用户30天无操作或显式关闭─→ closed（历史可回看，可继续追问→回到对应阶梯态）
```

规则：
- 解锁仅允许相邻逐级（l1→l2→l3），禁止跳级（BR-GUD-3 与计数口径"L1→L2、L2→L3 各计 1 次"一致）；重复解锁同级拒绝。
- 纠正重识别不限次数：同会话第 1 次免费，由会话持久化计数原子认领；第 2 次起各计 1 次。Redis 仅缓存，跨日/重启不恢复免费次数（BR-LMT-3，2026-10-24 PO 裁决细化）。
- 追问不改变阶梯状态；讲解与追问按冻结的 questions.final_level 适配（BR-LVL-1/3），仍遵守当前阶梯输出边界。
- `out_of_syllabus=true` 的会话走同一状态机，system 槽位注入"通用讲解，不针对考级"标注要求（BR-LVL-5）。
- 变式题每会话限 1 道（BR-VAR-3）；variant_pending 由"听懂标记"或用户主动 CTA 触发，未触发不推送。
- 状态持久化在 ai_sessions.state；session_steps 记录每次解锁留痕（时间、解锁后级别、操作者），session_messages 记录逐轮内容。
- `level_snapshot` 仅是创建时账号所报级别的审计快照。confirm 原子保存用户确认的 final_level 与 out_of_syllabus，之后该会话不可再改级别；生成、追问、变式与 level_band 统计均取 final_level，历史界面分别标明“创建时所报级别”和“本次讲解级别”。

### 3.4 上下文窗口与成本纪律

- history 组装上限：优先保留 question_context + 最近 N 轮（初始 N=10），超出丢弃最早追问轮；GLM 上下文缓存命中以"前缀稳定"为原则组装（system + 题目上下文前置不变）。
- 追问轮次不带图（基线 NFR-COST-03 落实点）：图片仅识别轮使用，识别结果文本化后进 history。
- token 计量：每次调用 usage 写 session_messages.token_in/token_out，阶梯级聚合写 session_steps，Langfuse 按 trace 聚合成本（对照 NFR-COST-02 基线）。
- 用户额度之外独立执行资源保护（包括不计次的识别、内部重试和访客追问）：单会话同一时刻仅 1 个生成操作，单调用输入 ≤16000 tokens、输出 ≤4096 tokens、执行 ≤120s；访客会话累计最多 40 次模型调用（含识别/重试）及 64000 输出 tokens。均为初始可配置保护值，联调须证明正常完整体验可完成；保护值不等于新增收费次数。
- 每次真实模型调用前原子预留该调用最大 token 预算，结束后按 usage 结算、释放未用预留；异常无法取得 usage 时保守结算预留，不因失败回滚而无限重试。预算状态持久化到 session_resource_usage；Redis 缓存丢失不重置预算。识别尚无 session_id 时先创建内部会话与预算记录，失败不消耗产品日额度。
- 所有生成入口执行 owner/IP 频率保护：初始 owner 每分钟 6 次、IP 每分钟 30 次、全局模型并发上限由部署配置明确；不计次入口同样受控。超频返回 429 resource_rate_limited + retry_after，不扣日额度；会话预算耗尽返回 409 session_resource_exhausted，不再调用模型，已生成内容可回看。

## 4. REST / SSE 接口（tut 模块对外契约）

统一约定：
- 认证：登录态（FEAT-001 交付的会话凭证）；访客会话接口同一组，以 `owner_type` 区分（见 5.3）。
- 流式接口一律 POST + SSE（`text/event-stream`），前端 fetch + ReadableStream 消费（EventSource 不支持 POST）。
- SSE 事件类型：`meta`（operation_id、prompt_version、ladder_level、message_id）→ `chunk* {delta}` → 唯一终态：`done {usage}` / `safety_truncated {reason}` / `error {code, message}`。每事件有单调 event_id，只有已通过两类检查的用户可见内容才能进入续传缓存。
- 业务 POST 必带 Idempotency-Key，键作用域为 owner + session + action；同键同请求返回原 operation_id/流，不再次扣次、生成或推进状态，同键不同请求体返回 409。终态失败需用户显式“重新生成”使用新键，按既有失败不退次规则计次；网络自动重连禁止换键。
- 断连续传使用 `GET /api/tut/operations/{operation_id}/events?after={event_id}`，校验当前 owner 后补发再跟随；不重发业务 POST。断开连接不取消已受理操作，由 FastAPI 生命周期管理的执行任务在超时内继续；进程退出后持久化的未完操作标为 interrupted，不自动重放计费动作。缓存过期：完成态从消息正文恢复，未完成/失败态显示明确终态，禁止把半条内容当完成。
- 每会话通过 PG 行锁 + 唯一活动操作约束认领，状态校验、操作记录及额度决策可恢复；成功发布正文后才提交阶梯升级。Redis 日额度扣减用 operation_id 幂等账本与原子脚本，PG quota_usage 以 operation_id 唯一补记；崩溃重试先核对账本，避免双扣。阶梯失败维持原级别，日额度仍按已放行扣减。
- 超限响应：`429 {code:"quota_exhausted", reset_at}`（次日 0 点）；进行中的流不中断（BR-LMT-5）。

| 接口 | 说明 | 计数 |
|---|---|---|
| POST /api/uploads | 签发 OSS 私有桶签名 PUT URL（类型白名单 image/*，≤10MB） | 不计 |
| POST /api/tut/sessions | 创建会话并同步执行识别管线；入参 `{text? \| image_oss_key?, code_snippet?(≤5000), question_note?}`；返回 `{session_id, echo}` 或 422（无效输入/识别失败） | 不计 |
| POST /api/tut/sessions/{id}/reidentify | 仅 pending_confirm 可用；持久化计数原子认领首次免费，第 2 次起走 consume；走 VL 通道，受独立资源预算保护 | 第 1 次不计，第 2 次起各计 1 次 |
| POST /api/tut/sessions/{id}/confirm | 提交确认/纠正（question_text/knowledge_points/level）→ 记录纠正 → SSE 流式输出 L1 | **计 1 次**（发起讲题口径） |
| POST /api/tut/sessions/{id}/unlock | `{target:2\|3}`，校验相邻逐级 → SSE 流式输出 L2/L3 | 各计 1 次 |
| POST /api/tut/sessions/{id}/followups | `{question}` → SSE 流式回答 | 计 1 次 |
| POST /api/tut/sessions/{id}/understood | 听懂标记（幂等） | 不计 |
| POST /api/tut/sessions/{id}/variant | 预留日额度 → 生成并真实运行校验 → 返回 `{stem}`；超时 60s；同会话单操作，校验器未就绪返回 503 validation_unavailable | 成功发布题面时将预留转为扣减，失败释放预留，不下发未校验题 |
| POST /api/tut/sessions/{id}/variant/answer | `{answer}` → 判读 `{correct, feedback}`；首份合法作答原子写入，重复请求返回原判读，不覆盖 first_answer/first_correct | 不另计（已含于生成动作）；判读失败保留原作答、幂等重试同一任务 |
| GET /api/tut/sessions?cursor= | 历史列表，按最后活跃倒序，分页 | 不计 |
| GET /api/tut/sessions/{id} | 完整回看：echo + messages + steps + variant + understood | 不计 |

说明：
- 创建会话时不计数、确认后首轮 L1 生成才计数——这是"识别失败/无效输入不计数"（PBI-0006/0007 AC）与"发起=识别+首轮讲解计 1 次"（BR-LMT-2）两条规则的相容解：计数点落在 confirm 触发的 L1 生成动作上；生成失败（LLM 错误）已计次数不退还、重试按新请求计次（2026-10-24 PO 裁决：先计后调防失败重试绕过，故障损失由运营个案兜底）。
- 计数判定前置：一般计费动作先 `consume()` 放行并扣减；变式题例外，先 `reserve()` 保证额度再生成，成功发布时 `commit()`，生成/校验失败 `release()`。同 owner 的所有放行都检查 used + reserved，防并发绕过；预留按 operation_id 幂等，失联由操作终态恢复任务结算，不能在任务仍运行时仅靠 TTL 自动释放。内部资源消耗仍计入资源预算。

## 5. 数据设计（字段级）

### 5.1 PostgreSQL（core/session 所有）

**questions**
| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid PK | |
| session_id | uuid FK→ai_sessions | 识别来源会话 |
| source_type | enum(text,image) | |
| raw_text | text? | 文本输入原文（≤10000） |
| image_oss_key | text? | 截图对象键（uploads/ 前缀） |
| route | enum(text,ocr,vl) | 识别路径 |
| ocr_text / ocr_confidence | text? / numeric? | OCR 产物与置信度 |
| recognized_text | text | 识别题目文本（确认前为 AI 判定值） |
| knowledge_points | jsonb text[] | 判定考点 |
| judged_level | smallint \| 0 | 判定级别；0 = out_of_syllabus |
| final_level | smallint \| 0 | 用户确认级别（BR-LVL-3 以此为准）；0 = 考纲外 |
| corrections | jsonb | `[{field, old, new, at}]` 纠正留痕（PBI-0007 AC） |
| code_snippet / question_note | text? | FR-TUT-03 补充输入 |
| created_at | timestamptz | |

**ai_sessions**
| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid PK | |
| owner_type | enum(user,guest) | guest 承载体验模式（5.3） |
| owner_id | text | user_id 或 guest 指纹 hash |
| type | enum(tut,dia,exa_review) | 本特性仅 tut；枚举为框架共用预留 |
| state | enum | 见 3.3 状态机 |
| level_snapshot | smallint? | 创建时所报级别审计快照（BR-LVL-4）；未提供则null，不因判定考纲外覆写 |
| reidentify_count | int default 0 | 会话生命周期内已放行的重识别次数，事务内递增；跨日不重置 |
| out_of_syllabus | bool | 通用讲解模式标注 |
| question_id | uuid FK→questions | |
| understood_at | timestamptz? | 听懂标记（幂等，重复标记不更新） |
| last_active_at / created_at | timestamptz | 列表排序依据 / 创建时间 |

**session_steps**（解锁留痕 + 阶梯级 token 聚合）
| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid PK | |
| session_id | uuid FK | |
| ladder_level | smallint(1,2,3) | 解锁后级别；L1 行在 confirm 时写入 |
| unlocked_at | timestamptz | |
| token_in / token_out | int | 该阶梯生成累计用量 |

**session_messages**（逐轮内容，回看与续问的在线数据源）
| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid PK | |
| session_id | uuid FK | |
| seq | int | 会话内单调序号 |
| role | enum(user,assistant,system) | |
| kind | enum(recognition_echo, ladder_l1, ladder_l2, ladder_l3, followup_q, followup_a, variant_stem, variant_answer, variant_judge, system_notice) | 结构化区分内容类型，回看页按 kind 渲染；通用讲解标注经 system_notice 与 UI 角标双落实 |
| content | text | 正文（阶梯讲解全文、追问问答、变式题面/作答/判读结论） |
| ladder_level | smallint? | 产生该消息时的阶梯 |
| token_in / token_out | int? | |
| prompt_version | text? | 模板版本（盲评回溯） |
| llm_trace_id | text? | Langfuse trace 关联（观测用，不作在线查询） |
| safety | jsonb? | `{input_check, output_check, truncated}` 安全记录 |
| created_at | timestamptz | |

> 本表字段口径即 backlog 待精炼确认项 #5 的定稿：满足 PBI-0011「回看完整内容（含阶梯解锁状态与变式题结果）」——回看 = messages(kind 全类) + session_steps + variant_attempts；PBI-0016 解决状态回填所需诊断类 kind（diagnosis_*）在 FEAT-003 技术设计中扩展同一枚举，不另建表。

**variant_attempts**
| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid PK | |
| session_id | uuid FK（唯一约束） | 每会话 1 道 |
| stem | text | 题面 |
| ref_answer / ref_solution_code | text | 参考答案与参考解 |
| test_data | jsonb | 构造测试数据 [{input, expected_output}] |
| judge_mode | enum(ai_read,exact_match) | 判读方式 |
| validated | bool | 下发前校验是否通过（BR-VAR-3；P0 校验方式见文末开放决策 D1） |
| validation_detail | jsonb? | 校验过程记录 |
| first_answer / first_correct | text? / bool? | 首次作答与判读（金标准数据源） |
| answered_at | timestamptz? | |

索引：`ai_sessions(owner_type, owner_id, last_active_at desc)`、`session_messages(session_id, seq)`、`session_steps(session_id, ladder_level)`、`variant_attempts(first_correct)`（金标准聚合）、`questions(created_at)`（A-Q6 抽样）。

**generation_operations / session_resource_usage**（core/session 所有）：前者记录 id、session_id、owner、action、idempotency_key、request_hash、message_id、status（accepted/running/succeeded/failed/interrupted）、前后阶梯、终态错误及开始/结束时间；唯一约束 `(owner, session_id, action, idempotency_key)`，同会话仅一个活动生成操作。后者记录 session_id、model_calls_used/reserved、output_tokens_used/reserved；预算结算以 operation_id + 内部调用序号唯一，重试不能重复结算。

用户删除时一并清除操作、预算、消息和变式记录；quota_usage 通过所属模块清理。operation 状态是恢复事实源，连接状态不代表业务终态。首次作答以 session_id 唯一行 + 条件写入锁定，判读失败为 pending/error，不能写 first_correct=false。

### 5.2 Redis 键（在基线已列键之外的新增项）

| 键 | 结构/TTL | 用途 |
|---|---|---|
| quota:user:{uid}:{yyyymmdd} | counter，至次日 0 点 | 基线已列，判定源 |
| quota:guest:{fp}:{yyyymmdd} | counter，至次日 0 点 | 基线已列，体验额度 |
| reidentify:{session_id} | 可淘汰缓存，非判定源 | 免费次数以 ai_sessions.reidentify_count 为准，缓存跨日失效不影响权益 |
| stream:{message_id} | list，TTL=轮次结束+10min | SSE 分片缓冲与断连续传 |

计数口径：Redis 脚本原子检查 used+reserved 并以 operation_id 幂等放行，quota_usage 以 operation_id 唯一补记流水。一般扣减后 LLM 失败不退还；变式未发布仅释放预留（见§4）。额度日固定于受理时的 Asia/Shanghai 日期，跨日恢复不向新日期重复扣次；操作与结算账本保留至本次恢复完成，不能随日计数零点清理。

### 5.3 访客会话承载（FEAT-001 接口点，本特性仅预留）

- `owner_type=guest` 时 owner_id = 设备指纹+浏览器标识的 hash；体验额度判定走 quota:guest 键。
- BR-LMT-4 口径：guest 在 confirm/L1 生成点扣减 1 次体验；仅该已确认会话内 unlock/followup/variant 跳过产品日额度计次。服务端验证 owner、该 session 的体验放行记录及资源预算；仅有同 owner 其他体验记录不能放行新会话。
- 体验转注册（PBI-0013）时的会话归属迁移在 FEAT-001 技术设计中定稿；本设计保证 owner 字段可更新即可。

## 6. 横切集成

### 6.1 内容安全（NFR-SAFE-01，core/safety）

- 输入：所有用户文本（题目文本/疑问点/代码片段/追问/变式作答）同步 check_text 前置；截图经 check_image 前置。命中 → 422 `safety_blocked`，不计数，写拦截日志流（独立日志，FR-OPS-03 申诉核查上下文）。
- 输出：LLM 网关对待发布片段送检，检测通过才写 SSE/续传缓存；命中或超时不发布待检片段，终结为 safety_truncated。已通过检测的早先片段可保留，该次计数照计。语义漏检仍是需真实样例回归验证的残余风险，不能用事后撤回补救提前上屏。

### 6.2 限额服务（modules/lmt 进程内接口）

```python
class QuotaService(Protocol):
    def consume(self, owner: OwnerRef, action: QuotaAction, session_id: str, operation_id: str) -> ConsumeResult: ...
    def reserve(self, owner: OwnerRef, session_id: str, operation_id: str) -> ConsumeResult: ...
    def commit(self, operation_id: str) -> None: ...
    def release(self, operation_id: str) -> None: ...  # 仅释放未提交预留，不是失败退款
    def remaining(self, owner: OwnerRef) -> int: ...
```

`QuotaAction = session_create | unlock | followup | variant | reidentify`（dia/exa 动作由对应特性扩展）。ConsumeResult 含 allowed / remaining / reset_at，其中 remaining 扣除有效预留。guest 免费内部动作仍校验会话所属与首次 confirm 已放行记录，再检查资源预算，不能仅凭“当日有任意体验记录”放行其他未确认会话。无 refund 路径：一般动作放行后 LLM 失败/中断不退还；变式失败仅释放尚未提交的预留。GET /api/lmt/usage 展示可用额度并区分短暂处理中预留。

### 6.3 埋点（modules/ops 进程内接口）

本特性产生的事件类型（写 events 表，供 FR-OPS-01 日报取数）：

`session_started, recognition_succeeded(route), recognition_failed(reason), echo_confirmed, echo_corrected, reidentify_used, ladder_unlocked(level), ladder_compliance_violation(level), followup_asked, understood_marked, variant_pushed, variant_answered(correct), quota_rejected(action), safety_blocked(stage), ocr_fallback`

成功学习另发 learning_response_completed：仅在 confirm/unlock/followup 的有效正文发布成功，或 variant/answer 判读成功后按 operation_id 幂等发射。echo_confirmed/followup_asked 是动作事件，不能用来代替成功学习活跃；失败/只有占位/安全终止无有效结果不发成功事件。

金标准指标取数路径：变式题首次做对率 = variant_attempts.first_correct 聚合；听懂标记率 = ai_sessions.understood_at 聚合；解锁深度分布 = session_steps 聚合。

### 6.4 可观测性

- OTel span 树：`tut.session.confirm → session_core.ladder → llm_gateway.stream → glm.api`；识别链路 `tut.session.create → ocr.recognize | llm.structured`；变式 `variant.generate → variant.validate → variant.judge`。span 属性带 model、prompt_version、token、TTFT。
- 指标新增（承接基线指标体系）：TTFT P50/P75/P95 按路由（NFR-PERF-01 验证源）；OCR 命中率与置信度分布、VL 升级率、ocr_fallback 次数（A-Q6 数据源）；L1/L2 合规校验失败率；变式校验一次通过率；限额拒绝率。
- Langfuse：LLM 请求/响应全量 trace（prompt 版本、输入、输出、token、耗时），盲评抽样即按 session_id 回捞。
- 日志脱敏：不落邮箱；用户图片仅落 oss_key 引用（基线纪律）。

## 7. 安全与合规

- uploads/ 私有桶 + 签名 URL：签发 PUT（≤10MB、image/* 白名单）；识别经 api 内网 GET；历史回看展示经短时效签名 GET URL，仅本人会话（NFR-SAFE-03）。
- 图片不出境：VL 通道 base64 内联直发 GLM（境内 API），不签发外部 URL。
- AI 生成标识：会话页所有 AI 内容位强制"AI 生成"角标（前端组件级，PBI-0022 的统一组件在 FEAT-006 定稿；本特性会话页直接采用该组件，接口无依赖）。
- 未成年人：level_snapshot 与年龄分层数据来自 acc 模块进程内只读接口；本特性不写 users 表。
- 密钥：GLM/内容安全/OSS 凭据环境变量注入，不入仓（基线纪律）。

## 8. 失败行为矩阵

| 场景 | 行为 | 计数影响 |
|---|---|---|
| 无效输入（文本过短/非题目/图片模糊） | 422 + 重新输入提示 | 不计 |
| OCR 失败/超时 | 自动升 VL 通道 + ocr_fallback 指标 | 不计 |
| 识别结构化校验失败（重试 1 次后） | 文本路径→识别失败提示；截图路径→升 VL，VL 再失败→识别失败提示 | 不计 |
| GLM 429/5xx/超时 | 网关内重试 1 次（指数退避）；仍失败 → SSE error 事件 | 已扣额度不退还，流水标 `failed`（2026-10-24 PO 裁决） |
| 输入安全命中 | 422 safety_blocked + 申诉入口提示 | 不计 |
| 输出安全命中 | 流截断 + safety_truncated 事件 + 提示 | 照计（记录支撑申诉） |
| L1/L2 合规校验违规 | 候选不上屏，重生成 1 次；再违规 → 预置无答案提示 + 质量事件，状态不升级 | 照计 |
| 变式生成/校验失败（最多2次候选，含首次） | 失败提示、校验记录留痕，不下发题面 | 释放未提交预留；内部调用消耗资源预算 |
| 限额超限 | 429 quota_exhausted + 次日恢复提示 + 非 AI 功能引导；进行中流不中断 | — |
| SSE 断连 | GET 操作流游标续传，不重执行 POST；缓存过期按操作终态恢复，进程中断显式 interrupted | 同操作不再扣次 |

## 9. 测试策略

- 单测（api，pytest）：
  - 状态机：合法/非法转移全枚举（跳级解锁拒绝、重复解锁拒绝、closed 续问回到对应阶梯）。
  - 计数矩阵（BR-LMT 逐条一个用例）：session_create/unlock/followup/variant 各计 1；重识别第 1 次免费、第 2 次起计次；识别失败不计；生成失败不退还、重试另计；guest 整体计 1 且内部动作跳过。
  - prompt 组装快照：级别注入、阶梯边界、history 截断（N=10）、考纲外标注注入。
  - L1/L2 合规校验器：含代码块/不含代码块样例表驱动。
  - 识别/变式 JSON schema 校验：合法、缺字段、类型错误、重试耗尽路径。
  - OCR 路由判定：置信度阈值边界、结构化失败升 VL、ocr 超时降级。
  - Redis 计数并发：INCR 原子性、超限竞态（并发 2 请求仅 1 放行）。
- 接口测试：J1 全旅程 API 级（LLM 网关注入 fake，确定性输出）；SSE 事件序列断言（meta→chunk*→done）；429/422 分支；断连续传。
- 评测集（A-Q6 承接）：开发期收集真实 OJ 题面/评测截图建回归集，统计 OCR 命中率、VL 升级率、识别准确率；阈值 TH_OCR 据实测定稿。
- 性能：TTFT 埋点在联调环境对 GLM 实测，验证 NFR-PERF-01（P75 ≤ 5s）；结果入 A-Q 跟踪。
- 评审回归：捕获 SSE/续传/历史三条用户可见路径，注入首轮与重试均含完整代码的 L1/L2 候选，均不得泄露；TTFT 包含全候选校验时间。确认级别与账号快照不同时，prompt/追问/变式/日报均取 final_level。
- 故障与并发：双击同键、同键不同体、不同键并发解锁、断连续传、扣额度后进程退出、变式预留后崩溃恢复、首答并发与判读重试；同操作最多一次扣次/升级/首答写入，错误不能被误记为答错。
- 资源保护：访客无限追问、仅创建不 confirm、免费重识别跨日、Redis 缓存丢失、内部重试超预算；保护生效不消耗额外产品次数，正常完整体验仍可完成。
- Mock 边界：LLM 网关可注入 fake（契约级 mock）；ocr/内容安全/OSS 以本地容器或 stub。

## 10. 基线缺口与开放决策

### D1（阻塞 PBI-0010，路由 GB）：保留运行校验，申请 judge0 校验能力前置

PBI-0010 AC 要求参考解在构造测试数据上真实运行通过。2026-11-11 评审修订保留该要求，不采用双 LLM 代替运行的过渡实现；基线仍将 judge0 排在 P1，故提出 [ADR-001](../architecture/adr/ADR-001-p0-variant-validation.md) 申请仅将变式题校验所需 judge0 能力前置，模考产品范围与 P1 节奏不变。该 ADR 为 draft，未获 GB 人工 go 前不得改写已批准基线或放行依赖该能力的 PBI-0010。

| 方案 | 内容 | 代价/风险 | 推荐度 |
|---|---|---|---|
| A（待 GB） | judge0 最小部署提前到 P0，仅用于变式题校验 | 提前完成 A-Q1 隔离验证与 A-Q2 容量验证，不能在 api 进程直接执行生成代码 | 保留既定 AC；可行性待验证 |
| B（不采用） | 双 LLM 交叉判断替代真实运行 | 不满足已定“运行通过”AC，不得置 validated=true | 不作为当前实现 |
| C | PBI-0010 整体延后至 P1 | 金标准"变式题首次做对率"在 P0 内测期无数据源，"效果闭环前置"决议（2026-10-22）落空 | 置信度 20，不推荐 |

运行校验契约：独立沙箱中参考解对全部构造数据编译/执行成功且输出匹配才置 validated=true；记录验证器版本、代码/测试数据摘要及逐用例结果。编译错误、超时、输出不匹配或校验器不可用均不下发、不提交日额度预留。运行通过只能证明这些用例一致，不能代替教练对题意与难度的抽检。

### D2（非阻塞，随任务分解定稿）：TH_OCR 初始阈值

OCR 置信度路由阈值初始取 0.85（经验值），A-Q6 真实截图评测集回归后定稿；仅影响路由指标，不影响接口与数据结构。

## 11. G3 追踪

| PBI | 本文覆盖节 | 备注 |
|---|---|---|
| PBI-0006 统一输入 | 4（uploads、sessions）、5.1、7 | 文本/图片上限校验在 web 与 api 双侧 |
| PBI-0007 识别与回显 | 3.1/3.2/4、5.1、8 | 纠正留痕 corrections；重识别首次免费 reidentify 键 |
| PBI-0008 阶梯引导引擎 | 3.1/3.3/4、5.1、6.2 | Arch-1 契约即 3.1 |
| PBI-0009 追问与级别适配 | 3.1/3.4/4 | history 组装与级别快照 |
| PBI-0010 变式题检验 | 3.1/4、5.1、8、10-D1 | **D1 未决前不可进 G3** |
| PBI-0011 听懂标记与历史 | 4、5.1 | 回看数据口径 = messages + steps + variant_attempts |
