# FEAT-001 账号与合规 — 特性技术设计

Status: draft <!-- 文档生命周期: draft | in-review | approved | living | superseded -->
日期: 2026-10-29
覆盖 PBI: PBI-0001 / 0002 / 0003 / 0012 / 0013
输入: Architecture Baseline（GA go 2026-10-23）、PRD 02/03/04/05、feat-001-ux-ui-design.md、feat-002-tech-design.md（5.3 访客会话接口点）、FEAT-001 各 PBI
受影响仓: gesp-tutor-api（主：acc/lmt 模块）、gesp-tutor-web（登录/onboarding/设置/体验态页面）、gesp-ai-tutor（本文档）

> 本文是 G3 判据 tech-design-ready 的输入。设计约束全部继承架构基线；超出基线的项集中在文末"基线缺口与开放决策"，按纪律路由 PO/GB，不在本文静默变更。

## 1. 范围与最小切片

本特性的最小技术切片 = 四条可跑通路：

```
F1 验证码认证：发码 → 校验 → 新邮箱自动注册 → 30 天登录态
F2 首次资料与合规：onboarding 强制收集 → <14 周岁分层 → 协议/监护人同意留痕
F3 设置与注销：资料/级别修改（次日生效）→ 协议版本展示 → 注销二次确认 → 延迟删除
F4 体验模式：访客标识 → 体验额度计数 → IP 防刷人机验证 → 注册墙 → 转注册归属迁移
```

明确不做（本期）：

- 邀请码门控（PBI-0004 暂缓）：不恢复邀请码功能；内测访问限制按 §10-D2 的部署层替代方案提案处理，须 GB 明确批准后才能代替基线的门控机制。
- 微信扫码等其他登录方式（FR-ACC-05 后置）。
- 会话页本体与阶梯引擎：FEAT-002 范畴；本文仅落地其 5.3 预留的访客承载与转注册归属迁移。
- 运营后台 UI（基线纪律）：体验配置与人机验证阈值经 Redis 配置键调整。

## 2. 组件落位与模块边界

```
web（Next.js）
 ├─ /login /onboarding /settings（CSR，无全局导航独立流页面）
 ├─ 会话页体验态槽位（guest-chip / 注册墙 / 注册引导卡，复用 FEAT-002 页面骨架）
 └─ 访客指纹采集组件（canvas/UA 等浏览器特征 hash，纯前端）

api（FastAPI 单体）
 ├─ modules/acc/     账号与合规（本设计核心）：认证、资料、同意留痕、注销、访客标识
 ├─ modules/lmt/     限额服务：guest 计数键与体验配置读取（FEAT-002 已定接口，本文扩展 guest 规则）
 └─ modules/ops/     埋点事件写入（漏斗事件，进程内接口）
```

数据表所有权（对齐基线"模块拥有各自数据表"纪律）：

| 表 | 所有者 | 说明 |
|---|---|---|
| users / user_consents | modules/acc | 本设计字段级定稿 |
| invite_codes | modules/acc | 基线已列实体；建表不建功能，见 D2 |
| quota_usage（+ Redis 计数键） | modules/lmt | FEAT-002 已定；本文新增 guest 键与 IP 键 |
| events | modules/ops | 漏斗事件写入 |

acc 对外只暴露进程内只读接口（见 3.3），core/session 不直连 users 表。

## 3. 接口契约

### 3.1 REST 接口（acc 模块对外）

统一约定：认证凭证为 HttpOnly Cookie `gt_token`（不透明 token，见 4.2）；所有写接口幂等键为客户端生成请求 ID 或天然幂等（重复提交不产生第二条留痕）。

| 接口 | 说明 | 计数/限制 |
|---|---|---|
| POST /api/auth/email-code | `{email}` 发送 6 位验证码；重发间隔 60s；同邮箱当日发码上限 20 次（防邮件轰炸，超限 429） | Redis 限频 |
| POST /api/auth/verify | `{email, code}` 校验；通过：新邮箱自动创建 users 行（status=active）并登录；响应 Set-Cookie 30 天 | 连续错 5 次锁定 10 分钟 |
| POST /api/auth/logout | 删除 token 键，清 Cookie | — |
| GET /api/auth/me | 返回 `{user: {nickname, level, is_minor, profile_complete} \| null, guest: bool}`；未登录返回 guest 态 | — |
| POST /api/users/onboarding | `{nickname, birth_month(YYYY-MM), level(1-8), agreement_version, guardian_consent?}`；缺项 422 逐字段返回；<14 周岁缺 guardian_consent 422 | 仅首次，重复提交 409 |
| PATCH /api/users/level | `{level}` 修改级别；写入次日生效队列（见 4.1 惰性滚动） | — |
| GET /api/users/consents | 协议同意留痕列表（doc 名称、版本、同意时间） | — |
| POST /api/users/deletion | 注销申请；立即禁用登录（status=deactivated + 删除全部 token），排定延迟删除（见 4.3） | — |
| POST /api/guest/captcha | 人机验证校验（组件见 D1）；通过签发绑定 guest/IP/动作的单次凭据，不签发当日白名单 | 见 5.2 |
| GET /api/guest/experience-config | 体验入口配置（开关、当日额度）；未登录首页/注册墙读取 | — |

错误码约定：`code_expired` / `code_mismatch {attempts_left}` / `code_locked {unlock_at}` / `send_too_frequent {retry_after}` / `onboarding_incomplete {missing[]}` / `guardian_consent_required`。

### 3.2 验证码生命周期（FR-ACC-01 口径的技术落点）

```
发送：code = 6 位数字（CSPRNG）→ Redis email_code:{email} = {code_hash, attempts=0}，TTL 5 分钟
     重发间隔：email_code_cd:{email} SET NX EX 60，存在则拒绝并返回剩余秒数
校验：比对 code_hash；失败 attempts+1（行内返回剩余次数）
     attempts ≥ 5 → 删除 code 键，写 email_lock:{email} TTL 10 分钟，锁定期内 verify/send 均拒绝
成功：删除 code/lock 键 → upsert users（email 唯一）→ 签发 token
```

- code 仅存 SHA-256 hash，不明文落 Redis（Redis 为共享托管实例，缩小泄露面）。
- 邮件发送走基线 send_mail 薄接口（首期阿里云 DirectMail）；发送失败返回 502 `mail_send_failed`，不写 code 键（避免"发了键但邮件没到"的锁定占用）。
- 发码上限 20 次/邮箱/日为本文新增防护（基线未列），键 `email_code_daily:{email}:{yyyymmdd}`。

### 3.3 acc 进程内只读接口（供 core/session 等模块）

```python
class AccountService(Protocol):
    def get_level_snapshot(self, uid: str) -> int | None: ...   # 惰性滚动后返回当前生效级别
    def requires_guardian_consent(self, uid: str) -> bool: ... # 按出生年月保守判定，不推断精确生日
    def is_active(self, uid: str) -> bool: ...                  # deactivated 用户的在途请求拦截
```

- 出生年月不含日，不能推断精确生日：达到出生月份 +14 年后的下一个月首日，才解除监护同意要求；此前（含14岁生日所在月）保守要求同意。API 的 is_minor 兼容字段仅表示 requires_guardian_consent，不对外宣称精确周岁或成年状态；get_age_band 不再提供伪精确的 adult/minor 分类。界面说明该按月判定规则，记录规则版本；监护同意留痕仍为注册时点事实。
- 级别惰性滚动：读取时若 `level_next_effective <= today` 则滚动 level_next → level 并清除，再返回。不建每日定时任务（基线无 MQ/worker，见 4.1）。

## 4. 数据设计（字段级）

### 4.1 PostgreSQL（modules/acc 所有）

**users**
| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid PK | |
| email | citext unique | 登录标识；日志不落盘（脱敏纪律） |
| nickname | text? | onboarding 前为 null |
| birth_month | date? | 存当月 1 日（YYYY-MM 粒度，最小化） |
| level | smallint? | 当前生效级别（1-8） |
| level_next | smallint? | 待生效级别（BR-LVL-4） |
| level_next_effective | date? | 生效日 = 修改次日 0 点 |
| status | enum(active, deactivated) | 注销即 deactivated，不可登录 |
| deletion_due_at | timestamptz? | 注销后 15 个工作日截止，按 Asia/Shanghai 业务日历计算；不以固定日历天近似 |
| created_at / last_login_at | timestamptz | |

**user_consents**（同意留痕，PBI-0003 AC 数据源）
| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid PK | |
| user_id | uuid FK→users | |
| doc_type | enum(user_agreement, privacy_policy, minor_protection) | |
| doc_version | text | 同意时版本号（协议文本与版本号为 api 仓内置配置，见 6.2） |
| guardian_consent | bool | 仅 minor_protection 行有意义：已征得监护人同意 |
| consented_at | timestamptz | |

唯一约束 `(user_id, doc_type, doc_version)`：同一版本重复同意不产生新行；协议更新后重新同意产生新版本行（PBI-0003"协议更新后版本号随之更新"取数路径）。

**invite_codes**：按基线实体建表（code、来源、次数上限、作废标记），本特性不写功能代码，见 D2。

索引：`users(email)` 唯一、`user_consents(user_id)`、`users(status, deletion_due_at)`（删除任务扫描）。

### 4.2 登录态（30 天，FR-ACC-01）

- 凭证：不透明 token（256bit CSPRNG，URL-safe），Redis `auth:{token}` = uid，**固定 TTL 30 天**（不滑动续期——AC 口径为"30 天内免登录，第 31 天重新验证"，滑动续期会使口径漂移）。
- Cookie：`gt_token`，HttpOnly + Secure + SameSite=Lax，30 天 Max-Age；多端登录各自独立 token 共存（不互踢，无单点登录需求）。
- 注销/删除时按 uid 索引键 `auth_idx:{uid}`（set）批量删除该用户全部 token。
- 不选 JWT 的理由：30 天有效期内注销需即时生效，不透明 token 删除即失效；JWT 需额外黑名单机制，无收益。

### 4.3 注销与延迟删除（BR-CMP-5）

```
POST /users/deletion → status=deactivated + 删 token + 终止在途生成/禁止新写入
                     → 同事务创建 deletion_jobs，request_at 与 deadline 固化
每日低峰任务从申请后首次窗口即开始，不能等截止日才执行：
  按 job 逐项清理所属模块、对象存储与外部副本，成功一项即持久化进度
  全项通过核验后，最后删除 users/user_consents 与可关联的 job 标识
  仅保留无 owner/session/对象/trace 标识的计数审计摘要
```

- 删除清单：core/session 的会话/题目/消息/变式/操作/预算；lmt 的额度流水与缓存；ops 的盲评 context/评分/导出文件与 events 关联；safety 的命中片段/对象引用；Langfuse 的 trace、metadata、评分与队列副本；OSS 原图及缩略图；Redis 流缓存与 token。P2 上线时 wrong_book/提醒等纳入同一清单，否则不得通过该特性验收。
- events 经 ops.purge_owner(uid) 将 owner_type 改为 anonymous、owner_id/session_id 置空并删除 props 中指纹、归因、引用和文本字段，仅允许保留日期/事件类型/模块/级别段等不可关联聚合属性。不能仅清空不存在的 user_id 列；盲评样本与 Langfuse 副本不以“已去邮箱”为由跳过删除。
- 跨模块只调用各 owner 的 purge_owner 接口；先收集待删 session/对象/trace 标识再删除源记录，防止丢失定位信息。注销后全部写入口和执行任务重新校验 active，避免清理期间生成新副本。
- 任务为持久化 deletion_jobs（阶段、尝试次数、下次重试、截止时间）；FastAPI 03:30 Asia/Shanghai 任务 + 启动补跑，PG 锁防重入。单项失败独立重试，接近截止前 3 个工作日仍未完成则升级告警与人工处置；无成功证据不能标 completed。
- RDS/PITR、云盘快照、对象版本与导出备份亦登记保留期限：本特性部署验收必须证明含该用户数据的副本在 deletion_due_at 前过期或销毁。恢复演练须先重放未完成删除清单再开放服务，防止已删用户复活；若现有保留配置做不到，注销 AC 不通过，不得以“仅删除在线数据”代替。
- 业务日历版本固化进 job；验收覆盖周末、节假日、任务停机与失败重试。是否存在必须保留的数据由政策评审明确，本设计不自行断言无保留例外；任何例外须记录范围、依据与期限。

## 5. 体验模式（PBI-0012/0013）

### 5.1 访客标识与计数

```
guest_key = sha256(device_fp + ":" + browser_id)
  device_fp：前端指纹组件（canvas/UA/屏幕等特征 hash），同源可复现
  browser_id：服务端签发的 HttpOnly Cookie gt_guest（1 年），每浏览器一份
```

- 计数键：`quota:guest:{guest_key}:{yyyymmdd}`（TTL 至次日 0 点），当日 ≥1 即额度用尽 → 注册墙。
- AC 口径核对：同一设备换浏览器 → browser_id 缺失重新签发 → 新 guest_key → 分别计数（允许，反刷由 IP 层兜底）；同浏览器当日重复访问 → browser_id 不变 → 不重复发放。
- 计次点：guest 会话 confirm（L1 生成）点扣减；仅该已确认且属于当前 guest 的会话内 unlock/followup/variant 跳过产品计次，每个真实模型调用仍受 FEAT-002 §3.4 资源预算保护。跨日继续原会话不重新赠送调用预算，新体验按当日额度独立认领。

### 5.2 IP 防刷与人机验证

- IP 计数键 guest_ip:{ip}:{yyyymmdd} 在会话创建受理前原子检查并递增，用于昂贵识别前的保护；第4次及以后需先通过验证，再执行识别。日报完整体验发起以 confirm 放行为准，两者是不同统计用途，不能混算漏斗。
- 验证通过：签发绑定 guest_key、IP、动作的 5 分钟单次 challenge 凭据，服务端原子消费；仅放行当前一次创建，后续达到阈值的发起仍需验证。验证不能绕过单访客额度、资源预算和 IP/owner 限流；验证失败不可发起。
- 人机验证选型为开放决策 D1。

### 5.3 体验配置开关（PBI-0012 AC：运营可临时下调）

- Redis 键 `guest_experience:config`（hash）：`{enabled: true, daily_quota: 1}`；键不存在时取 api 配置默认值（enabled=true, daily_quota=1）。
- lmt.consume 读取该配置判定 guest 放行；enabled=false 时体验入口关闭（前端经 GET /api/guest/experience-config 隐藏入口，发起接口同步拒绝）。
- 调整为每周 1 次：`daily_quota` 语义保持"次/周期"，周期键后缀由 `{yyyymmdd}` 切为 ISO 周 `{yyyy}W{ww}` 由配置项 `period: day|week` 控制。
- 调整路径：运维直连 Redis 改键（无后台 UI，基线纪律）；对注册用户正式额度零影响（quota:user 键独立）。

### 5.4 转注册归属迁移（PBI-0013，承接 FEAT-002 5.3 预留）

```
体验结果页注册引导卡 → F1 注册流（新邮箱）→ onboarding 完成
  → 迁移：ai_sessions 中 owner_type=guest AND owner_id=guest_key 且当日活跃的会话
    更新为 owner_type=user, owner_id=uid（仅当日，不迁移历史访客会话）
  → 计数：quota:user:{uid}:{date} 从 0 起计 15 次口径；guest 计数不抵扣（独立键，天然隔离）
  → 回流：结果页顶栏切换 C1 正式额度指示器 + 成功条
```

- 迁移在 onboarding 完成点执行（资料未补齐前会话仍挂 guest，避免半迁移态）；迁移动作写 events `guest_session_migrated {count}`。
- guest 转注册后 gt_guest Cookie 保留：该浏览器再以访客身份访问仍按原 guest_key 计数（防"注册后再刷体验"）。

### 5.5 示例题

- 内置示例题（1-8 级各 1 道）为 api 仓内置静态配置（JSON：级别、考点标签、题干文本），GET /api/guest/sample-questions 返回；选用后等价于文本输入创建 guest 会话，计 1 次体验额度。
- 选题内容随 PBI-0012 refinement 定稿（UX 开放决策 3），接口与计数设计不受影响。

## 6. 横切集成

### 6.1 埋点（modules/ops，PBI-0013 漏斗取数路径）

本特性产生的事件（写 events 表）：

`auth_code_sent, auth_code_send_failed, auth_verify_failed(attempts_left), auth_locked, user_registered, onboarding_completed(requires_guardian_consent), level_changed, account_deactivated, guest_experience_started, guest_experience_completed, guest_captcha_shown, guest_captcha_passed, guest_captcha_failed, guest_wall_shown, signup_card_shown, signup_card_clicked, guest_session_migrated(count)`

唯一事件目录为 FEAT-006 §3.1，以上类型全部须登记后发射；不使用 signup_completed/variant_done 作为事件别名。体验发起 = guest 首次 confirm 放行时发一次 guest_experience_started；体验完成 = understood_marked 或首次 variant_answered 首次出现时，额外幂等发一次 guest_experience_completed。完成仅为行为信号，不代表验证学会。

注册 = 首次创建账号时的 user_registered（owner_type=user, owner_id=uid），props.attribution_guest_id 取服务端 gt_guest 关联的 guest_key，不接受客户端任意指定。7 日归因窗口从每次合格体验 cohort 的开始时间计算，注册只归因最近一次尚在窗口内的体验 cohort，每账号最多一次；同日/跨日统一，events 不新增 guest_key 列。重复登录不发注册事件。

### 6.2 协议文本与版本管理

- 用户协议 / 隐私政策 / 未成年人保护条款正文为 api 仓 `modules/acc/legal/` 内置 Markdown 文件 + 版本号常量（法务产物入库，版本号随内容更新手动递增）；web 经 GET /api/legal/{doc_type} 取当前版本正文与版本号渲染展示页。
- 同意时记录当前版本号入 user_consents（4.1）；协议更新 → 版本号递增 → 设置页"协议与隐私"区展示已同意版本与当前版本差异提示（UX B3 帧口径）。本期不做强制重新同意拦截（协议内容首版上线，更新场景未发生，发生时可基于 consents 表加拦截，数据已具备）。

### 6.3 可观测性

- 指标新增：发码成功率（DirectMail 质量）、verify 失败率、锁定触发次数、guest 发起量 / 注册墙展示量 / captcha 通过率（反刷有效性）、体验→注册转化率（日报核心行）、延迟删除任务执行计数与失败。
- 日志脱敏：不落邮箱明文与验证码（含 hash 不落）；登录/注册日志只落 uid 与结果码（基线纪律）。
- 告警接入：发码失败率 > 10% 持续 30 分钟 → P2（注册链路中断等同产品不可用）。

### 6.4 内容安全

昵称字段经 check_text 前置过滤（唯一用户生成文本输入点）；命中 422 `safety_blocked`。协议文本与系统文案为静态内容不走检测。

## 7. 安全与合规

- 最小集落实（BR-CMP-2）：users 仅邮箱/昵称/出生年月/级别；birth_month 按月粒度存储（不取日），进一步压缩可识别性。
- 验证码防爆破：hash 存储 + 5 次锁定 + 单邮箱日发码上限（3.2）；verify 接口加 IP 限频（同 IP 分钟级 30 次）。
- 访客指纹仅计数用途：guest_key 为不可逆 hash，不回推设备特征原文（基线"仅用于体验额度计数"）。
- 未成年人：is_minor 动态计算（3.3）；<14 拦截在 onboarding 接口服务端强制（不只前端拦截）。
- 传输与密钥：全站 HTTPS；DirectMail 凭据环境变量注入（基线纪律）。
- Cookie 安全：HttpOnly/Secure/SameSite=Lax（4.2）；CSRF：写接口要求自定义头 `X-Requested-With`（SameSite=Lax + 自定义头双保险，不引入 token 方案）。

## 8. 失败行为矩阵

| 场景 | 行为 |
|---|---|
| DirectMail 发送失败/超时 | 502 mail_send_failed；不写 code 键、不占用重发间隔与发码上限 |
| Redis 不可用 | auth/验证码/计数全部不可用 → 503 + 告警（Redis 为基线单点依赖，托管实例可用性由云厂商承担）；登录态校验失败按未登录处理（降级为访客，不 500） |
| 验证码连续错误 | attempts 递增 → 5 次锁定 10 分钟；锁定期 verify/send 均拒绝 |
| onboarding 重复提交 | 409（幂等：已有完整资料则拒绝） |
| 注销任务执行失败 | 次日任务自然重试（删除幂等）；连续失败经指标告警发现 |
| 人机验证服务内部错误 | 失败关闭：拒绝发起 + 提示稍后重试（防刷场景不放行） |
| 体验配置键损坏 | 读取失败回退 api 配置默认值（enabled=true, quota=1），记告警日志 |
| guest 会话迁移中途失败 | onboarding 已提交则迁移标记幂等重试于下次登录；迁移失败不阻塞注册完成 |

## 9. 测试策略

- 单测（api，pytest）：
  - 验证码生命周期：发送/重发间隔 60s/5 分钟过期/5 次锁定/锁定拒绝 send 与 verify/发码日上限。
  - 登录态：token TTL 30 天断言（不滑动）；注销后 token 全失效；多端 token 共存。
  - 年龄分层边界：14 岁生日月之前、生日月首日/末日、次月首日及跨年/闰年；只用出生年月，不构造不存在的精确生日。
  - 级别惰性滚动：修改当日快照旧级别、次日新会话快照新级别、历史会话 level_snapshot 不变（BR-LVL-4）。
  - 留痕唯一约束：同版本重复同意不新增行；版本更新产生新行。
  - guest 计数：同 browser_id 不重复发放；IP 第 4 次起需验证；challenge 仅当前 guest/IP 单次可用、过期/重放失败；验证成功仍不能绕过资源预算与日额度。
  - 体验配置：enabled=false 拒绝发起；period=week 键滚动。
  - 迁移：当日 guest 会话归属更新；quota:user 独立不抵扣；重复迁移幂等。
- 接口测试：F1 全流程（fake send_mail）；onboarding 缺项 422 逐字段；<14 缺 guardian_consent 422；注销端到端（deactivated → 定时任务触发 → 关联数据清除与 events 匿名化断言）；漏斗事件序列。
- Mock 边界：send_mail 契约级 fake；check_text stub；Redis 用 fakeredis。
- 时间依赖一律注入时钟，不用 sleep。

## 10. 基线缺口与开放决策

### D1（阻塞 PBI-0012，路由技术决策）：人机验证选型

UX 开放决策 1 移交项。候选：

| 方案 | 内容 | 判断 |
|---|---|---|
| A（推荐） | 自研滑块：服务端生成缺口位置与校验容差，前端 canvas 拼图；零外部依赖 | 防刷目标为脚本级批量（内测期 ≤50 设备/日），自研滑块足够；云厂商中立纪律下不引入新厂商 API；工作量约 1 个任务粒度。置信度 70 |
| B | 第三方人机验证 API（如阿里云验证码 2.0）薄接口隔离 | 抗专业打码更强，但内测期无此威胁面；新增厂商依赖与按量费用，与规模不匹配 |

推荐 A；公开运营放量前（A-Q4 压测同期）按实际攻击面复核是否升级 B。

### D2（内测发布前阻塞，路由 GB）：以部署访问边界替代邀请码功能

保持 backlog 已决的邀请码功能暂缓，不能把“仅向受邀者曝光入口”当作访问控制。提议复用既有 nginx，为受邀测试者配置独立可撤销的 HTTPS Basic Auth 凭证；覆盖 web、api、beacon、静态资源及签名 URL 签发入口，阻断绕过代理访问容器，禁止公开 CDN 缓存内测内容。产品登录仍为邮箱验证码，已获准测试者可在边界内匿名体验，不增加产品邀请码流程。

该方案改变基线明确写定的邀请码门控机制，见 [ADR-002](../architecture/adr/ADR-002-private-beta-access.md)。GB 人工 go 前不宣称替代方案已批准，不放行内测发布；批准后同步 PRD/基线的具体机制表述，O9“不面向公众”目标不变。DevOps 须提供直连/转发/撤销访问的拒绝证据，不能仅靠 robots/noindex 或隐藏 URL。

### D3（非阻塞，随任务分解定稿）：guest_key 指纹组件来源

自研轻量指纹（canvas+UA+语言+时区+屏幕，约 100 行）vs 引入 FingerprintJS OSS。倾向自研：指纹仅用于计数、无需高熵准确率，避免引入依赖。随 PBI-0012 任务分解定稿。

## 11. G3 追踪

| PBI | 本文覆盖节 | 备注 |
|---|---|---|
| PBI-0001 验证码登录 | 3.1/3.2、4.1/4.2、8 | 30 天登录态固定 TTL；锁定/重发/过期全口径 |
| PBI-0002 资料与级别 | 3.1/3.3、4.1 | 级别惰性滚动落实 BR-LVL-4 次日生效 |
| PBI-0003 未成年合规 | 3.1/3.3、4.1/4.3、6.2、7 | user_consents 留痕；注销延迟删除；最小集字段审计 |
| PBI-0012 体验模式 | 5.1/5.2/5.3/5.5、8 | **D1 未决前人机验证部分不可进实现**；配置开关满足运营调整 AC |
| PBI-0013 转注册 | 5.4、6.1 | 归属迁移承接 FEAT-002 5.3 预留；漏斗事件口径定稿 |
