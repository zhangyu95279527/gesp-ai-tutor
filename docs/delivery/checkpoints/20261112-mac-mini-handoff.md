# Checkpoint — GitHub保存与Mac mini续接

## Completed

- 三仓业务增量已本地提交；新增API/Web私有GitHub仓，保存任务分支与main。交付仓沿用公开远端。
- 统一换机分支chore-mac-mini-handoff，组件提交API4e98e79、Webc20356f。交付仓以本检查点所在分支最新提交为准。
- 组件AGENTS使用相对交付仓路径，后端执行命令使用uv；新增可重建的PG/Redis Compose与Mac操作手册。

## Verified

- GitHub账号/仓库权限核对通过；两个新组件仓均private。
- 已用git ls-remote逐条核对全部本地分支：交付仓5个、API13个、Web11个，远端SHA均一致；三仓工作区干净，default_branch均为main，Mac克隆需显式选择换机分支。
- GitHub API读取时，三仓换机分支均未返回工作流运行记录；没有将远端CI标为通过。
- 受跟踪文件的常见令牌/私钥模式与.env文件检查未发现命中（不等于完整安全审计），忽略目录未加入提交。
- API ruff包含src/tests/migrations通过；SMTP启动参数按本机已安装aiosmtpd帮助确认。前一轮业务基线API227/Web109，不将其标成Mac运行证据。

## Current state

- 最新功能任务仍为TASK-0023，业务检查点见20261112-ladder-recovery.md。没有生成新业务完成/G4/发布记录。
- GitHub保存与Mac续接说明见docs/delivery/mac-mini-handoff.md；不要从默认main继续，否则会缺少未合入的业务代码。
- 初次组件Git推送直连失败；最终命令临时使用交付仓已有回环代理127.0.0.1:7890后成功。不复制此Windows代理配置到Mac。

## Next actions

- Mac登录GitHub，三仓同级克隆chore-mac-mini-handoff；Codex主项目为交付仓并附加API/Web目录。
- 安装Git、Node24、uv和容器运行环境，按手册重建服务、安装依赖、迁移到0008并执行新机回归。
- 完成新机验证后，按业务检查点创建下一任务分支继续；保持PC优先与真实服务后配约定。

## Blockers

当前Windows没有Docker，Compose未启动验证；Mac/Apple Silicon实测与新机认证由新机环境完成。真实模型/存储/OCR/正式安全仍未配置。

## Open questions

不要求搬迁旧开发测试数据；如用户另需旧会话/账号，需要单独设计一致性导出/导入。

## Changed artifacts/files

- API/Web AGENTS；交付仓.agent/local上下文/远端登记、dev/compose.yaml、Mac手册、组件登记和本检查点。

## Last commit

API4e98e79、Webc20356f；交付仓提交号从远端chore-mac-mini-handoff分支读取。未发布。
