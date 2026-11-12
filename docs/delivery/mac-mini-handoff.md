# Mac mini 换机与Git续接

更新：2026-11-12。本次是保存代码与重建开发环境，不是发布。Mac上的安装、运行和完整回归需在新机执行；Windows测试结果不能代替Mac实测。

## 三仓与分支

| 仓库 | GitHub | 用途 |
|---|---|---|
| gesp-ai-tutor | https://github.com/zhangyu95279527/gesp-ai-tutor | 交付文档与环境配置；现有公开仓 |
| gesp-tutor-api | https://github.com/zhangyu95279527/gesp-tutor-api | 后端；私有仓 |
| gesp-tutor-web | https://github.com/zhangyu95279527/gesp-tutor-web | 前端；私有仓 |

本次换机准备分支统一为`chore-mac-mini-handoff`，基于`task-0023-ladder-recovery`，包含之前各开发增量与全部祖先提交。本地历史任务分支也一并推送，不做功能合并、不打发布标签。新机必须克隆此分支，默认main尚未合入完整开发增量。

TASK-0023基线：交付仓ba9a60f、APId87f315、Web9d0ec44。换机准备提交位于这些提交之后。最新业务检查点仍为[20261112-ladder-recovery](checkpoints/20261112-ladder-recovery.md)。

组件换机分支提交：API `4e98e79`，Web `c20356f`。交付仓取本文件所在分支最新提交；推送记录见[换机检查点](checkpoints/20261112-mac-mini-handoff.md)。

## 1. 安装工具并克隆

在Mac安装Git、Node.js 24、uv，以及提供`docker compose`的容器运行环境并启动它。前端CI使用Node24；Python版本由uv按项目3.12要求安装。Apple Silicon机器使用原生ARM工具，不复制Windows的.venv、node_modules或可执行文件。

私有仓需要先在Mac完成GitHub账号认证（例如gh auth login再gh auth setup-git，或配置SSH）。不得把旧电脑凭据文件/令牌提交进仓库。

```sh
mkdir -p ~/Developer
cd ~/Developer
git clone --branch chore-mac-mini-handoff https://github.com/zhangyu95279527/gesp-ai-tutor.git
git clone --branch chore-mac-mini-handoff https://github.com/zhangyu95279527/gesp-tutor-api.git
git clone --branch chore-mac-mini-handoff https://github.com/zhangyu95279527/gesp-tutor-web.git
```

三个目录保持同级，位置可以不是`~/Developer`。组件AGENTS使用相邻交付仓相对路径；旧制品中的E:/AIworkspacke是历史证据位置，不要求Mac建立E盘。

## 2. 启动开发数据库与缓存

```sh
cd ~/Developer/gesp-ai-tutor
docker compose -f dev/compose.yaml up -d --wait
docker compose -f dev/compose.yaml ps
```

Compose只暴露回环5432/6379，用具名卷保存本机PG数据。密码为明确开发值，不适用于公开部署。已占用端口时先处理本机冲突或同步修改端口和连接串；不要删除卷解决端口问题。

此环境是新建开发库，不包含Windows测试账号、邮箱或会话。无需旧数据即可继续开发；需保留旧数据时另做数据库一致性导出/导入，不复制运行中的`.cache/dev-services/pgdata`。旧缓存中的PGlite/fakeredis启动脚本不是新机必需依赖。

## 3. 后端安装与验证

```sh
cd ~/Developer/gesp-tutor-api
uv python install 3.12
uv sync --locked
cp .env.example .env
set -a
source .env
set +a
export DATABASE_URL='postgresql://postgres:gesp-local-only@127.0.0.1:5432/gesp_dev'
export INTEGRATION_DATABASE_URL="$DATABASE_URL"
export AUTH_SECRET="$(uv run python -c 'import secrets; print(secrets.token_hex(32))')"
uv run alembic upgrade head
uv run alembic current
uv run ruff check src tests migrations
uv run mypy src
uv run pytest -q
```

预期迁移`0008_ladder_deadline (head)`；TASK-0023 Windows基线227项后端测试无skip。Mac结果需重新记录，出现skip不能当完整集成验证通过。AUTH_SECRET为本地独立生成，若需要重启后保留登录可保存在本机未跟踪.env中；不要写入Git。测试夹具法律文本仅限local，生产生成仍关闭。

在当前已导出环境变量的终端启动API：

```sh
uv run uvicorn gesp_api.app:create_app --factory --app-dir src --host 127.0.0.1 --port 8000 --no-access-log
```

新开终端启动本地SMTP收件端；仅用于开发验证码，邮件打印在该终端：

```sh
cd ~/Developer/gesp-tutor-api
uv run python -m aiosmtpd -n -l 127.0.0.1:1025 -c aiosmtpd.handlers.Debugging
```

项目当前从进程环境读取设置，不会自动加载.env；每次新开API终端需重新source并应用本页的数据库/AUTH_SECRET覆盖。Redis/SMTP默认配置与本地服务相符。

## 4. 前端安装与验证

```sh
cd ~/Developer/gesp-tutor-web
npm ci
npm run check
npm run dev
```

TASK-0023基线109项Web测试、生产build通过。默认API_ORIGIN为http://127.0.0.1:8000，浏览器使用http://127.0.0.1:3000/login，避免与localhost混用造成Origin不匹配。

当前真实模型、对象存储、OCR、正式安全尚未配置，confirm/unlock/retry-l1仍返回503且不扣新次数。开发演示不是真实讲解，不能把换机启动成功记成MVP验收通过。

## 5. Codex续接提示词

在Codex本地项目中添加三个同级目录，交付仓设为主目录。新聊天发送：

```text
在Mac mini继续开发GESP AI Tutor。
三个仓库位于同一个父目录，当前从chore-mac-mini-handoff分支恢复。
先读交付仓AGENTS.md、docs/delivery/status.md、
docs/delivery/mac-mini-handoff.md和
docs/delivery/checkpoints/20261112-ladder-recovery.md。
核对三个仓库的分支/提交，检查并重建本机依赖，执行Mac回归后再继续下一项任务。
仅按需读取任务输入，不重复已完成开发。后续工作创建符合AGENTS的新任务分支。
保持PC浏览器优先，真实模型/对象存储/OCR/正式安全稍后配置，未配置不造成功结果。
```

续接依赖仓库制品，无需搬运旧聊天、本机凭据或Windows缓存。暂停旧电脑上的编辑，避免两台机器各自产生未经协调的提交。
