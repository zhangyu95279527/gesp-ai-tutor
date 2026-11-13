# 整体开发进度表

更新：2026-11-13。范围：现有26个PBI；邀请码/分享/获客落地页3项暂缓，单独列出，不混入已交付数量。

## 当前结论

- 产品/PRD/架构基线已批准；现有5套76帧UI及限额组件已定稿。
- 已开始编码11/26个PBI：邮箱登录、首次资料与级别、AI显式标识、日限额、题目统一输入基础、识别回显持久化基础、PC阶梯与流式客户端、历史回看与听懂、会话内追问、诊断三件套输入基础、六类错因输出基础。年龄分层/测试协议留痕有共用支撑代码，PBI-0003整体仍为draft。
- G3覆盖11个PBI（历史/标记/追问均为独立切片）（输入/回显/阶梯仅放行独立切片，真实服务与完整业务仍待实现）；G4完整验收通过0项；尚未发布。编码增量可本机运行，不等于MVP完成。
- 最新API ruff/mypy46源文件、324项回归通过；Web lint/typecheck、183项测试与生产build通过。迁移仍0010_followup；六类错因输出/引用核对/安全语义双检查与PC卡片已编码，开发占位PC实测及生产404通过。真实确认/计次/持久化与模型质量未验，公开诊断继续关闭。
- PC浏览器为主开发与完整验收端；手机通过同页自适应查看及基础操作，不单独开发移动流程，移动专项不阻塞PC主线。

## 模块总览

| 模块 | 批次 | 设计 | 编码与验证 | 下一步 |
|---|---|---|---|---|
| 账号与资料 | P0 | UI已定稿 | 邮箱登录、本机资料/级别已编码；年龄/测试留痕有支撑 | 正式文本/内容安全/注销与真实服务验收 |
| AI讲题与历史 | P0 | 阶梯/历史/追问切片就绪 | 追问持久受理/计次/已检发布与会话/历史面板、草稿及GET恢复已编码；历史/听懂沿用 | 真实模型/安全/预算与实时SSE、真实新追问及变式结果接入 |
| 变式题与体验转注册 | P0 | UI已定稿 | 尚未开始编码 | ADR-001决定、校验能力及讲题闭环 |
| 错因诊断 | P0 | UI及输入/输出切片就绪 | 三件套输入与六类输出合同、原文定位检查/PC结果卡已编码 | 共享确认/计次/持久化 → 真实上传/OCR/诊断 → 引导修正 |
| 日限额 | P0 | 组件及本轮实现设计已就绪 | 账本/原子判定/预留结算与PC用量已编码 | 真实会话、访客策略及生产Redis/PG集成 |
| 运营与内容安全 | P0 | 技术设计草案 | AI标识共用组件已编码；其余未开始 | 内容安全与事件目录随首批真实会话接入 |
| 真题模考与评测 | P1 | UI已定稿 | 尚未开始编码 | 题库/数据校准、Judge0及PC限时作答 |
| 错题本 | P2 | UI已定稿 | 尚未开始编码 | 待模考和会话数据就绪，可按既定方案降级 |
| 分享/获客/邀请码 | 暂缓 | 不计入本轮定稿交付 | 暂缓 | 按Backlog与后续产品决策恢复 |

## PBI明细

| 批次 | PBI / 功能 | 执行状态 | 设计 | 编码 | 验证与剩余依赖 |
|---|---|---|---|---|---|
| P0 | [PBI-0001 邮箱验证码注册/登录](../features/PBI-0001.yaml) | in-progress | UI已定稿 | 本机登录链路已编码 | PC已验证；真实邮件/PG/Redis与正式协议集成待验收 |
| P0 | [PBI-0002 首次注册资料收集与级别管理](../features/PBI-0002.yaml) | in-progress | UI及本轮实现设计已就绪 | 本机资料/级别已编码 | 47个后端、32个前端回归通过；PC首次资料→设置→级别修改→刷新保持已验证；真会话历史集成待补 |
| P0 | [PBI-0003 未成年人年龄分层与协议同意留痕](../features/PBI-0003.yaml) | draft | UI已定稿，特性技术设计草案 | 年龄规则与测试留痕支撑已编码；整体未启动 | 正式文本/内容安全/注销及副本删除未完成 |
| P0 | [PBI-0005 日限额计数、用量展示与超限引导](../features/PBI-0005.yaml) | in-progress | 组件及实现设计就绪 | 幂等账本、原子额度、预留结算、PC用量和内部确认/重识别联动已编码 | 后端178项回归；前端沿用56项证据；真实会话/历史导航/访客和生产依赖待验收 |
| P0 | [PBI-0006 题目统一输入（文本/截图粘贴与上传）](../features/PBI-0006.yaml) | in-progress | UI及输入基础切片设计就绪 | PC图文粘贴/本地预览、服务端合同与图片字节解码已编码 | 后端122项回归通过；前端沿用56项证据；即贴即传、存储/安全/真实识别及完整AC待TASK-0013 |
| P0 | [PBI-0007 题目识别与回显确认](../features/PBI-0007.yaml) | in-progress | UI及PC回显切片设计就绪 | 本人读取/纠正HTTP、PC三字段表单/考纲外提示和失败保留输入已编码；原内部计次基础保留 | API183/Web71测试及PC样例通过；成功HTTP为ASGI+PG证据，真实浏览器识别→保存→L1、安全/预算与性能待TASK-0016 |
| P0 | [PBI-0008 阶梯式引导引擎（L1/L2/L3 手动解锁）](../features/PBI-0008.yaml) | in-progress | PC/持久化/恢复及原子受理切片就绪 | 原阶梯基础、确认扣次/L1同事务、过期旧孤立确认恢复已编码；公开生成关闭 | API237及同步7测试通过；Web本轮未改。真实模型/安全/预算、新入口接入/供应商取消/实时SSE及PC端到端待TASK-0021，完整17项AC未通过 |
| P0 | [PBI-0009 会话内追问与级别适配](../features/PBI-0009.yaml) | in-progress | 追问切片就绪 | 冻结级别/当前阶梯、共享活动互斥/计次/期限、问答持久化和面板已编码 | API269/Web141与PC保存问答/草稿通过；真实新回答/安全/预算和输出盲评未验，公开发送关闭 |
| P0 | [PBI-0010 变式题检验](../features/PBI-0010.yaml) | draft | UI已定稿，技术设计草案 | 未开始 | 真实运行校验依赖ADR-001的GB决定 |
| P0 | [PBI-0011 听懂标记与历史会话](../features/PBI-0011.yaml) | in-progress | 历史/标记/追问面板就绪 | 本人历史/标记与已保存追问回看已编码 | 当前API269/Web141通过；真实继续追问、完整变式结果/更早追问分页仍待后续，未通过G4 |
| P0 | [PBI-0012 未登录体验模式（每日 1 次完整讲题）](../features/PBI-0012.yaml) | draft | UI已定稿，技术设计草案 | 未开始 | 依赖讲题/变式/限额；人机验证选型待定 |
| P0 | [PBI-0013 体验转注册引导](../features/PBI-0013.yaml) | draft | UI已定稿 | 未开始 | 依赖体验闭环及账号归属迁移 |
| P0 | [PBI-0014 错因诊断三件套上传](../features/PBI-0014.yaml) | in-progress | UI及本地输入设计就绪 | PC三材料区/预览、UTF8代码导入与5001保留、服务端严格合同已编码 | API287/Web156与PC输入验证通过；即贴即传/真实存储与OCR未验，完整AC/G4未通过 |
| P0 | [PBI-0015 六类错因定位输出](../features/PBI-0015.yaml) | in-progress | UI及输出基础设计就绪 | 六分类/候选排序/原文引用与安全语义检查器、PC只读卡片已编码 | API324/Web183、PC占位及生产404通过；真实一致性/盲评、确认计次/持久化未验 |
| P0 | [PBI-0016 引导式修正与解决状态回填](../features/PBI-0016.yaml) | draft | UI已定稿 | 未开始 | 依赖诊断与引导引擎 |
| P0 | [PBI-0019 效果度量埋点与日报](../features/PBI-0019.yaml) | draft | 技术设计草案；复用工具UI | 限额拒绝事件最小支撑已编码；整体未启动 | 完整事件目录/维度、日报及看板待实现 |
| P0 | [PBI-0020 盲评抽样导出与结果录入](../features/PBI-0020.yaml) | draft | 技术设计草案；复用工具UI | 未开始 | 抽样、导出、评分及仲裁待实现 |
| P0 | [PBI-0021 AI 内容安全过滤](../features/PBI-0021.yaml) | draft | 技术设计草案 | 未开始 | 尚未接入真实check_text/check_image |
| P0 | [PBI-0022 AI 生成内容显式标识](../features/PBI-0022.yaml) | in-progress | 共用标识设计已定稿 | AiContent/AiBadge及导入约束已编码 | 基础组件测试通过；真实讲题/诊断/变式展示位尚未交付 |
| P1 | [PBI-0023 真题题库建设与测试数据校准（首批级别段）](../features/PBI-0023.yaml) | draft | 范围已定义，无独立业务UI | 未开始 | 真题素材/授权与测试数据校准待落实 |
| P1 | [PBI-0024 真题套卷列表与限时模考](../features/PBI-0024.yaml) | draft | UI已定稿 | 未开始 | 依赖题库与限时作答实现；PC优先 |
| P1 | [PBI-0025 自建评测机判分](../features/PBI-0025.yaml) | draft | 架构已有Judge0方案 | 未开始 | 评测部署、隔离与性能验证待实现 |
| P1 | [PBI-0026 逐题讲评入口](../features/PBI-0026.yaml) | draft | UI已定稿 | 未开始 | 依赖模考判分与讲题引擎 |
| P2 | [PBI-0027 错题自动归集与筛选列表](../features/PBI-0027.yaml) | draft | UI已定稿 | 未开始 | 依赖模考/诊断/讲题数据 |
| P2 | [PBI-0028 错题重练与进步对比](../features/PBI-0028.yaml) | draft | UI已定稿 | 未开始 | 依赖归集与评测能力 |
| P2 | [PBI-0029 重练提醒（站内通知 + 每周邮件）](../features/PBI-0029.yaml) | draft | UI已定稿 | 未开始 | 依赖错题归集；P2可降级项 |

## 暂缓项与已知依赖

- PBI-0004邀请码、PBI-0017分享卡片、PBI-0018获客落地页：按[Backlog](../product/backlog.md)暂缓；PRD部分旧口径仍须后续统一，本表不把暂缓等同于完成。
- ADR-001（P0变式真实运行）及ADR-002（内测访问边界）仍待GB；本表没有替代人工决定。
- 正式协议正文、真实check_text、生产PG/Redis/DirectMail及跨存储删除证据未齐；测试文本/本机替身不算正式上线验收。
- 当前users字段和级别快照合同已实现，真实学习会话/历史页面尚未实现，不能声称历史级别验收已通过。

## 接下来开发顺序

1. 日限额、输入、回显、PC阶梯、持久编排/恢复与原子确认基础已编码；下一步TASK-0021装配模型/安全/预算，接入新LadderAdmissionService与公开重试、供应商取消和实时SSE，接通PC完整链路。真实依赖未配置时保持网关关闭；重识别失败不扣次。
2. PBI-0009追问基础已编码；诊断输入基础已编码，错因结果基础已编码；下一步补诊断共享确认/计次/持久化及变式检验，并按真实服务就绪情况补上传/OCR与生成联调。历史只回看已发布正文，不用测试夹具替代真实输出验收。
3. 变式/体验/诊断按依赖推进；P1/P2继续保持后续批次，不提前扩展移动专项。

本表是本次制品核对快照；执行状态以[派生状态](status.md)、PBI、Task及验证证据为准。设计完成、代码存在、测试通过和完整验收分别统计，不用没有权重依据的百分比估算总完成度。


## 本轮代码与证据

- API资料/级别：87f81b4；Web资料/设置：851bfc2。均为本地任务分支提交，未合main，组件仓尚无远端。
- [本轮资料与级别验证](../verification/PBI-0002-local-profile.md)；[此前登录验证](../verification/PBI-0001-local-login.md)；[AI标识组件验证](../verification/TASK-0001.md)。
- 交付仓另存本轮进度及PC优先约定；不将文档推送与组件代码发布混为一谈。

- 日限额API：4e971d4；Web：90878ad（本地任务分支，未合main/未推送）。[本轮限额验证](../verification/PBI-0005-local-quota.md)；[继续开发检查点](checkpoints/20261112-quota.md)。

- 统一输入Web：8d4ce81，task-0012-unified-input（本地任务分支，未合main/未推送）。[输入验证](../verification/PBI-0006-local-input.md)；[最新检查点](checkpoints/20261112-input.md)。

- 输入API：05370ed，task-0014-input-contracts（本地任务分支，未合main/未推送）。[服务端输入验证](../verification/PBI-0006-api-input.md)；[当前检查点](checkpoints/20261112-api-input.md)。8000运行服务未重启，新增HTTP入口通过ASGI实例验证。

- 会话API基础：02603a2，task-0015-session-foundation（本地任务分支，未合main/未推送）。[会话验证](../verification/PBI-0007-session-foundation.md)；[最新检查点](checkpoints/20261112-session-foundation.md)。本轮仅内部仓储，公开入口未接入。

- 确认受理API基础：2e009fa，task-0017-confirmation-admission（本地任务分支，未合main/未推送）。[确认验证](../verification/PBI-0007-confirmation.md)；[当前检查点](checkpoints/20261112-confirmation.md)。内部readiness默认关闭，没有公开confirm或真实L1输出。

- 重识别API基础：450a06b，task-0018-reidentify-lifecycle（本地任务分支，未合main/未推送）。[重识别验证](../verification/PBI-0007-reidentify.md)；[最新检查点](checkpoints/20261112-reidentify.md)。已按用户决定实现失败不扣次；无真实模型/UI接入。

- PC回显切片：API169b50f、Web6ca6442（主体ad8c1cf），均task-0019-session-review，未合main/推送。[PC回显验证](../verification/PBI-0007-pc-review.md)；[当前检查点](checkpoints/20261112-pc-review.md)。开发合成样例与真实页面分开，生产样例404；真实完整讲题仍未交付。

- PC阶梯切片：APIf59aa7e、Web312d9e1，均task-0020-pc-ladder-stream，未合main/推送。[PC阶梯验证与截图](../verification/PBI-0008-pc-ladder.md)；[最新检查点](checkpoints/20261112-pc-ladder.md)。开发演示为协议占位，生产实际404；安全/答案边界声明不是实际内容评估，真实SSE服务和持久steps尚未交付。

- 持久阶梯切片：API20bf1aa、Web5370b26，均task-0022-ladder-persistence，未合main/推送。[持久阶梯验证](../verification/PBI-0008-persistent-ladder.md)；[当前检查点](checkpoints/20261112-persistent-ladder.md)。完成态SSE从已检持久正文回放，运行态409，新生成仍503；真实内容/实时流/预算及退出恢复未交付。

- 恢复切片：APId87f315、Web9d0ec44，均task-0023-ladder-recovery，未合main/推送。[恢复验证](../verification/PBI-0008-recovery.md)；[最新检查点](checkpoints/20261112-ladder-recovery.md)。期限扫描/读取回收、旧执行拒发、L1内部新计次重试和PC状态提示已编码；供应商取消、孤立确认与真实服务端到端仍待接入。

- 原子受理切片：APIc65dccb，task-0024-atomic-admission；Web仍c20356f。[原子受理与同步验证](../verification/PBI-0008-atomic-admission.md)；[最新检查点](checkpoints/20261113-atomic-admission.md)。每轮以[current-work.json](current-work.json)记录组件版本，使用workspace-sync同步当前任务与固定换机快照；不将本地提交等同于远端保存。

- 历史/听懂切片：API151f471、Webaac2957，task-0025-history-understood；[验证与截图](../verification/PBI-0011-history.md)、[最新检查点](checkpoints/20261113-history-understood.md)。本机3000/8000可查看，代码/当前清单与固定换机快照按workspace-sync核验。

- 追问切片：API4d5f979、Web128ae59，task-0026-session-followup；[验证与截图](../verification/PBI-0009-followup.md)、[最新检查点](checkpoints/20261113-session-followup.md)。固定换机快照与current-work随本轮提交推送，公开发送仍关闭。

- 诊断输入切片：API80d3798、Webdbcec3e，task-0027-diagnosis-input；[验证与截图](../verification/PBI-0014-input.md)、[最新检查点](checkpoints/20261113-diagnosis-input.md)。API287/Web156通过，三件套本地预览不冒充真实OCR/诊断；三仓按workspace-sync同步固定换机快照。

- 错因输出基础：APIf07ffe3、Web19c19b0，task-0028-diagnosis-output；[验证与截图](../verification/PBI-0015-output.md)、[最新检查点](checkpoints/20261113-diagnosis-output.md)。API324/Web183通过，内部检查器与PC只读卡片未接真实诊断；三仓按workspace-sync同步固定换机快照。
