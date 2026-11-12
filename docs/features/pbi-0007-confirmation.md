# PBI-0007 确认与额度受理基础

Status: approved
日期：2026-11-12；TASK-0017；沿用core/session与lmt所有权，不跨模块直写账本。

## 事务与状态

- PG在同一数据库内，增加QuotaService.consume_in_transaction内部接口，由调用方提供已开启的非autocommit连接。限额模块仍拥有账本/Lua/流水写入；只返回事务内决定，不提交调用方事务，调用方须外层commit后才返回放行或认领生成。
- 固定锁顺序：当前session行→限额owner行。所有确认只锁一个session，限额内部不反向访问session；普通限额调用只锁owner。不得在同一事务内再锁其他session。
- 新ConfirmationService.confirm锁本人session，校验键/请求/expected_revision/待确认状态及考纲外继续确认，再检查生成可用性（默认False）。未配置生成能力返回503，无扣次或状态变化。
- 同键同请求先重放持久确认结果，换payload409；结果包含operation_id、当时revision、额度决定和当前执行状态。跨日/额度配置改变不重新消费。
- 通过lmt内部接口，以服务端生成operation_id执行session_create计次；拒绝保存quota_rejected确认记录及额度拒绝日志，会话/纠正/final_level/revision不变。新键可在之后重新申请。
- 放行时同一PG事务保存确认纠正、冻结final_level、out_of_syllabus、revision+1以及admitted确认记录，会话进入内部l1_pending，绝不冒充l1_active或已有输出。
- PG回滚会同时撤销确认和额度账本；Lua可能先执行，下一次限额调用从已提交账本重建Redis，沿用TASK-0009恢复契约。PG提交响应丢失则同键读回原记录；不会新operation_id再扣。
- 受理后执行者必须claim_start，admitted→running仅一方成功。重复确认或重复认领不允许再次推理；running不能因重启自动重领，明确标interrupted，已消费不退。本轮没有模型执行、输出发布和自动恢复扫描器。
- 内部生成readiness回调默认False；后续必须由真实编排核验模型、安全、频率/预算与持久worker，不以手填True替代生产就绪。测试显式放行只用于合同。
- 考纲外level0必须显式continue_out_of_syllabus=True；拒绝继续不扣次。确认可同时带三字段纠正，原判定/创建级别快照不覆盖。正式受理后编辑/再次新键confirm均被状态检查拒绝。

## 边界与证据计划

仅内部类与迁移，无HTTP/UI变化。通过真实PG协议与fakeredis合同测试AC1/2/3/8/10的基础：原子级别冻结、超限不推进、同键重放与冲突、跨日及丢ack模拟、回滚重建、单次执行认领。完整AC仍待TASK-0016的真实识别/安全/生成、SSE及PC端到端/性能验证。生产PG/Redis并行与kill进程测试不在本机替身证据中冒认。
