# PBI-0007 会话与回显持久化基础

Status: approved
日期：2026-11-12；FEAT-002 / PBI-0007；仅放行TASK-0015独立服务端基础，真实识别及UI仍待后续任务。

## 确认事实与范围

- 继承FastAPI/PG、core/session拥有questions与ai_sessions的边界；跨账号模块不联表，创建方经ProfileService.get_level_snapshot获取级别再传入。
- 将原“创建(识别)”细化为内部pending_recognition，识别产物原子写入后才pending_confirm。当前不装配任何真实识别器，也不推进至l1_active。
- 新建会话保存原文或图片key、代码、疑问、owner、创建级别；PG唯一键保证owner内创建幂等。同键不同输入409，同键重放保持首个级别快照。API输入合同沿用TASK-0014。
- 所有读取与变更均显式owner过滤；非法UUID与非本人/不存在会话统一404。owner只由可信身份层传入，不接受客户端指定归属。
- 识别结果保存原判定题干/考点/级别、route、ocr_confidence和可编辑draft_echo。内部写入契约仅供已通过安全/资源预算的识别编排调用；没有公网写入或假识别兜底。
- 待确认状态下使用expected_revision乐观版本号编辑三字段；questions.corrections逐字段追加field/old/new/at/session_id，时间取数据库。final_level保持NULL，编辑不算正式confirm，不扣次、不生成讲解。
- publish/edit各持久操作键及payload摘要，锁会话行后认领；同键同payload返回原session_id/revision/replayed，不重复写纠正；同键不同payload409。重放先于版本判断，不因后续版本增长误冲突；新请求旧版本409。
- 初次识别只允许pending_recognition；同会话重识别序号保留在PG且不按日期重置，本轮不实现免费资格认领。用户账户快照不可被编辑级别覆盖。
- 题干10000、代码5000；考点最多20项、每项1～100字符，识别题干去空白至少10字符，级别0～8，OCR置信度0～1且仅ocr路径允许提供。考点数量/单项上限为可调整的结构保护假设。
- 本轮无HTTP或前端变更；先实现内部repository及PG迁移，原入口503保持。刷新/重启恢复证据来自重新构造repository读取同一PG数据，不等于实际进程中断演练。

## 任务DAG与验收映射

- TASK-0015：PG迁移、会话创建/读取、内部识别发布、待确认纠正、持久幂等/版本控制。覆盖AC1/2/3/7/8/9/10的基础合同。
- TASK-0016：依赖TASK-0015及TASK-0013；真实识别与回显UI、纠正提交、级别冻结、重识别持久资格及计次、confirm原子额度和L1、故障重试/性能；覆盖全部11条完整AC。未配置真实依赖前draft，不产生G4。

停止条件：迁移在本机PG协议环境成功，隔离/重放/冲突/版本/恢复/纠正测试通过，全回归通过并保存证据。基础合同通过不等于完整AC、生产并发或G4通过。

## 确认基础续作

TASK-0017新增内部确认/额度共享PG事务及执行认领，契约见[pbi-0007-confirmation.md](pbi-0007-confirmation.md)。仅正式受理时冻结final_level并进入l1_pending；edit仍不等于confirm。该基础已编码，但真实生成readiness默认关闭，未开放HTTP或真实L1。TASK-0016继续承担完整真实集成责任。

TASK-0018新增重识别PG资格/活动互斥及预留结算，见[pbi-0007-reidentify.md](pbi-0007-reidentify.md)。用户确认失败不扣次；首次免费，后续成功发布有效回显才扣、失败/中断释放。内部新识别值替换当前回显，之前AI判定与用户候选保存在操作快照，创建级别和corrections保留；真实服务仍未接入。

TASK-0019新增本人会话读取/纠正HTTP及PC回显表单，见[pbi-0007-pc-review.md](pbi-0007-pc-review.md)。开发local可验证持久纠正，生产缺正式安全时拒绝写入；确认/重识别未配置503不扣次。独立开发样例显式合成，生产404，不作为真实识别验收。
