# Mac mini M4：从 Git 下载到继续开发

更新：2026-11-18。适用：Apple Silicon Mac mini M4、macOS 默认 zsh 终端；目录放在 `~/Developer`。按顺序执行代码块，每一步成功后再继续。

完成标准：三仓版本一致、依赖重建、数据库迁移成功、Mac 回归通过、浏览器能登录，并能按当前检查点继续任务。Mac 安装与回归仍需新机实测，Windows 历史结果不能代替 Mac 结果。

## 0. 确认要搬什么

项目是三个独立 Git 仓库，必须保持同级：

```text
~/Developer/
├── gesp-ai-tutor/     # 交付仓：需求、设计、任务、检查点、Compose
├── gesp-tutor-api/    # 后端：FastAPI + Python 3.12
└── gesp-tutor-web/    # 前端：Next.js + TypeScript + Node.js 24
```

| 仓库 | GitHub | 获取权限 |
|---|---|---|
| 交付仓 | [gesp-ai-tutor](https://github.com/zhangyu95279527/gesp-ai-tutor) | 当前公开 |
| 后端 | [gesp-tutor-api](https://github.com/zhangyu95279527/gesp-tutor-api) | 私有，登录有权限的账号 |
| 前端 | [gesp-tutor-web](https://github.com/zhangyu95279527/gesp-tutor-web) | 私有，登录有权限的账号 |

**三仓都从 `chore-mac-mini-handoff` 克隆。当前 `main` 尚未包含全部开发增量。** 换机分支持续快进，不代表合入 main 或发布；实际任务分支与组件提交以 [current-work.json](current-work.json) 为准。

- Git 带走：已提交并推送的源码、锁文件、任务、验证记录、检查点。
- 新机重建：`.venv`、`node_modules`、`.next`、Docker 数据库、缓存。
- 单独配置：GitHub 登录、开发工具账号、本机 `.env`、API 密钥，不提交旧凭据。
- Windows 测试账号和会话不会随 clone 恢复；新建开发库即可继续。需要旧数据时另做一致性导出/导入，不复制运行中的数据库目录。

旧机收尾：让 agent 确认三仓工作区已提交、检查点已保存，再运行 `python scripts/workspace-sync.py --push`；三仓均输出 `remote_verified: true` 才确认同步完成。之后暂停旧机编辑。

本次整理已核对本机组件 SHA 与 current-work.json 一致；远端同步状态以实际同步命令输出为准。

## 1. 新 Mac 安装基础工具（只做一次）

打开「终端」，检查架构并安装 Apple 命令行工具：

```sh
uname -m
xcode-select --install
```

预期 `arm64`。若提示工具已安装，继续；否则完成弹窗安装再往下执行。若是 `x86_64`，先退出通过 Rosetta 运行的终端，改用原生终端。

按 [Homebrew 官网](https://brew.sh/) 安装：

```sh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

安装后按安装器的 Next steps 配置 PATH。Apple Silicon 默认前缀是 `/opt/homebrew`，默认 zsh 可用以下命令；已有同一行时不必重复追加：

```sh
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
brew install git gh uv node@24
echo 'export PATH="/opt/homebrew/opt/node@24/bin:$PATH"' >> ~/.zprofile
export PATH="/opt/homebrew/opt/node@24/bin:$PATH"
git --version
gh --version
uv --version
node --version
npm --version
node -p 'process.arch'
```

预期 Node 为 `v24.x`、架构为 `arm64`。Node 24 与前端 CI 对齐；Python 由 uv 安装，无需另装系统 Python。依据：[Homebrew 安装](https://docs.brew.sh/Installation)、[node@24](https://formulae.brew.sh/formula/node@24)、[uv 安装](https://docs.astral.sh/uv/getting-started/installation/)。

从 [Docker 官方 Mac 安装页](https://docs.docker.com/desktop/setup/install/mac-install/) 下载 **Mac with Apple silicon** 版本，安装并启动 Docker Desktop，完成首次初始化，再验证：

```sh
docker info
docker compose version
```

两条都成功再继续。数据库与 Redis 放在 Docker 内，无需再用 Homebrew 安装同名服务。编辑器使用你习惯的 Mac 版本即可。

## 2. 登录 GitHub 并配置提交身份

```sh
gh auth login --hostname github.com --git-protocol https --web
gh auth setup-git
gh auth status
```

按提示用浏览器登录拥有两个私有组件仓权限的账号。这里使用 HTTPS 与 GitHub CLI 凭据助手，无需再配 SSH 或复制旧令牌。依据：[登录](https://cli.github.com/manual/gh_auth_login)、[凭据助手](https://cli.github.com/manual/gh_auth_setup-git)。

将下面姓名、邮箱改成自己的；邮箱可用 GitHub 设置提供的 noreply 邮箱：

```sh
git config --global user.name "你的提交姓名"
git config --global user.email "你的GitHub提交邮箱"
git config --global core.autocrlf input
```

## 3. 下载三个仓库并核对接续点

首次执行；若目录已存在，不要重复 clone，先查看分支和未提交修改：

```sh
mkdir -p ~/Developer
cd ~/Developer
git clone --branch chore-mac-mini-handoff https://github.com/zhangyu95279527/gesp-ai-tutor.git
git clone --branch chore-mac-mini-handoff https://github.com/zhangyu95279527/gesp-tutor-api.git
git clone --branch chore-mac-mini-handoff https://github.com/zhangyu95279527/gesp-tutor-web.git
```

组件 AGENTS 用 `../gesp-ai-tutor/AGENTS.md` 找交付协议，不要把组件放进交付仓内部。历史文档里的 `E:/AIworkspacke` 无需在 Mac 复现。

确认每仓都是换机分支且无未提交修改，再拉取；报错就停止处理，不强推、不用 reset 覆盖：

```sh
cd ~/Developer
for repo in gesp-ai-tutor gesp-tutor-api gesp-tutor-web; do
  git -C "$repo" status --short --branch
  git -C "$repo" pull --ff-only || break
done
cat gesp-ai-tutor/docs/delivery/current-work.json
```

核验命令会由 uv 自动准备 Python 3.12，无需系统 python3：

```sh
cd ~/Developer/gesp-ai-tutor
uv run --python 3.12 python scripts/workspace-sync.py
```

脚本核对组件 SHA 与清单、检查点存在、工作区干净，并 fetch/检查远端。恢复到换机分支时三仓应显示 `task_synced: true`、`snapshot_synced: true`；这里 task_synced 指当前分支，不是清单内的历史任务分支。默认不推送、不自动修复分叉。

本说明更新时清单为 TASK-0032、迁移 `0013_guidance`，最新检查点为 [20261116-diagnosis-guidance.md](checkpoints/20261116-diagnosis-guidance.md)。以后拉到更新清单时，以更新后的清单为准。

## 4. 启动 PostgreSQL 与 Redis

```sh
cd ~/Developer/gesp-ai-tutor
docker compose -f dev/compose.yaml up -d --wait
docker compose -f dev/compose.yaml ps
```

预期 postgres、redis 均 healthy。当前 Compose 配置：

| 服务 | 本机地址 | 开发配置 |
|---|---|---|
| PostgreSQL 17 | `127.0.0.1:5432` | 用户 postgres；密码 gesp-local-only；库 gesp_dev |
| Redis 7 | `127.0.0.1:6379` | 数据库 0 |

这些是仅绑定本机回环的开发值。PostgreSQL 数据保存在 Docker 具名卷，不含 Windows 数据。镜像拉取失败先处理网络，不添加强制 `linux/amd64` 来掩盖架构问题。

## 5. 安装后端并写好本机配置

```sh
cd ~/Developer/gesp-tutor-api
uv python install 3.12
uv sync --locked
uv run python --version
```

预期 Python 3.12.x。保留 `uv.lock`，不要复制 Windows `.venv`。

**下面仅在首次、尚无 `.env` 时执行。** 若已有配置，保留原密钥并核对数据库等值，不覆盖。以下从示例生成配置，将随机密钥保存到未跟踪的 `.env`：

```sh
uv run python - <<'PY'
from pathlib import Path
import secrets

target = Path('.env')
if target.exists():
    raise SystemExit('.env 已存在：请核对现有配置，不覆盖')
text = Path('.env.example').read_text(encoding='utf-8')
text = text.replace(
    'postgresql://postgres:postgres@127.0.0.1:5432/postgres?sslmode=disable',
    'postgresql://postgres:gesp-local-only@127.0.0.1:5432/gesp_dev',
)
text = text.replace('replace-with-at-least-32-random-characters', secrets.token_hex(32))
text += '\nINTEGRATION_DATABASE_URL=postgresql://postgres:gesp-local-only@127.0.0.1:5432/gesp_dev\n'
target.write_text(text, encoding='utf-8')
target.chmod(0o600)
print('已生成本机 .env（未输出密钥）')
PY
git check-ignore .env
set -a
source .env
set +a
uv run alembic upgrade head
uv run alembic current
```

`git check-ignore` 应输出 `.env`；迁移当前为 `0013_guidance (head)`，后续以清单为准。法律文本指向 `tests/fixtures/legal`，仅供 local 开发。**后端不会自动读取 `.env`，新终端都要执行 `set -a / source .env / set +a`。** 保存的 AUTH_SECRET 可避免每次重启换密钥使已有登录失效。

## 6. 执行 Mac 首次回归

在刚才已加载 `.env` 的后端终端执行：

```sh
uv run ruff check src tests migrations
uv run mypy src
uv run pytest -q
```

`INTEGRATION_DATABASE_URL` 必须指向已迁移的本机开发库，不用生产库。历史 Windows 基线为 API 421 项测试、mypy 55 个源文件；出现 skip 或失败要排查，不能当作完整集成验证通过。

再安装、验证前端（先完成 check 再启动 dev，避免同时改写构建目录）：

```sh
cd ~/Developer/gesp-tutor-web
npm ci
npm run check
```

`check` 包括 lint、类型检查、测试和生产构建；历史 Windows 基线为 Web 271 项测试。保留 `package-lock.json`，不用 `npm install` 重解依赖。这些数字仅为参照，最终以当前提交的 Mac 实际结果为准。

## 7. 开三个终端启动项目

Docker Desktop 保持运行，第 4 节服务已 healthy。以下三个进程保持运行，不要等它们退出再开下一个终端。

**终端 A：本地收件服务器。** 验证码邮件打印在这个终端，不会发送到真实邮箱，不需要打开 8025 网页收件箱：

```sh
cd ~/Developer/gesp-tutor-api
uv run python -m aiosmtpd -n -l 127.0.0.1:1025 -c aiosmtpd.handlers.Debugging
```

**终端 B：后端。** 加载第 5 节保存的配置：

```sh
cd ~/Developer/gesp-tutor-api
set -a
source .env
set +a
uv run uvicorn gesp_api.app:create_app --factory --app-dir src --host 127.0.0.1 --port 8000 --no-access-log
```

**终端 C：前端。** 默认 API_ORIGIN 是 `http://127.0.0.1:8000`，先显式指定以避免继承旧环境：

```sh
cd ~/Developer/gesp-tutor-web
API_ORIGIN=http://127.0.0.1:8000 npm run dev
```

浏览器访问 [登录页](http://127.0.0.1:3000/login)。验证顺序：

1. [后端健康接口](http://127.0.0.1:8000/health) 返回 `{"status":"ok"}`。
2. 登录页输入自己控制的邮箱、请求验证码，从终端 A 读取验证码后登录。
3. 新账号进入 `/onboarding`，完成本地测试协议与资料填写后查看 `/settings`。
4. 检查登录状态、资料与额度展示；新开发库没有旧会话，历史列表为空是正常的。

全程使用 `127.0.0.1`，避免与 `localhost` 混用造成 Origin/Cookie 问题。API 文档入口当前关闭，不以 `/docs` 的 404 判断服务故障。

真实模型、对象存储、OCR、正式内容安全尚未装配，confirm/unlock/retry-l1 等生成入口仍可能返回 503 且不扣新次数。启动成功只代表能继续开发，不能据此认定 MVP 或 G4 验收完成，也无需为换机先部署本地大模型。

## 8. 接上当前开发任务

用 Mac 上的编码工具打开 `~/Developer/gesp-ai-tutor`，并让当前工作区能访问同级的两个组件仓。工具账号需要在新机单独登录。源码与交付制品已在 Git 中，不依赖复制旧聊天。

在新聊天粘贴以下提示词：

```text
在 Mac mini M4 继续开发 GESP AI Tutor。
三个仓库位于 ~/Developer 下，均从 chore-mac-mini-handoff 恢复。
先读交付仓 AGENTS.md、.agent/local/project-context.md、
docs/delivery/current-work.json、docs/delivery/status.md、
docs/delivery/mac-mini-handoff.md，再读清单所指的最新检查点。
核对三仓干净状态、分支、组件 SHA 与远端，检查 Mac 环境与回归结果。
先补齐尚未执行的换机验证；按检查点选下一任务，不重复已完成实现。
实现前读取对应阶段提示词及其列出的 skill、Task/PBI/AC；
确认 Task 追溯关系，在受影响仓库创建符合 AGENTS 的任务分支。
PC 浏览器优先；真实模型/对象存储/OCR/正式安全稍后配置，未配置不伪造成功。
每个完成增量更新检查点与 current-work，验证后提交并同步三仓。
```

当前检查点建议继续诊断追问、材料回看和真实创建确认闭环；具体选择应结合最新清单与 Task 就绪情况。不要直接把 TASK-0032 重新做一遍，也不要假定下一编号未被占用。

新任务在已核对的快照基础上创建 `task-<编号>-<描述>` 分支；纯文档/维护用 `chore-...` 或 `fix-...`。换机分支只作为恢复快照。main 仍按门与评审约定合入，换机不等于合并或发布。

## 9. 以后每天怎么开工、收工

**开工：** 确认另一台机器停止编辑，三仓先 `git fetch origin`、查看 `git status --short --branch`，读取 current-work 与检查点。当前分支有对应 upstream 时用 `git pull --ff-only`；远端领先/分叉时先处理，不强推覆盖。

若是再次从另一台电脑恢复：三仓在干净状态下切到 `chore-mac-mini-handoff`，各自 `git pull --ff-only`，再执行第 3 节同步核验。不要把旧任务分支当成最新快照。

**启动：** 启动 Docker Desktop，执行第 4 节 `up -d --wait`，按第 7 节开 SMTP/API/Web 三个终端。无需每天重新 clone 或生成密钥。锁文件变化后才重新 `uv sync --locked` / `npm ci`；新增迁移时先加载 `.env` 再 `uv run alembic upgrade head`。

**收工：** 验证 → 提交组件 → 更新 current-work 与最新检查点 → 提交交付仓 → 运行：

```sh
cd ~/Developer/gesp-ai-tutor
uv run --python 3.12 python scripts/workspace-sync.py
uv run --python 3.12 python scripts/workspace-sync.py --push
```

脚本按 API、Web、交付仓顺序推送当前分支及换机快照，核对远端 SHA；不自动提交，不强推。三仓有脏树、清单过期、远端新提交/分叉时停止；网络造成部分推送时先重新核对，不能当作全部同步完成。Mac 通常无需旧 Windows 的 `--proxy http://127.0.0.1:7890`。

结束调试时各终端按 `Ctrl+C`。可以停止数据库/缓存，保留 PostgreSQL 卷：

```sh
cd ~/Developer/gesp-ai-tutor
docker compose -f dev/compose.yaml stop
```

不要用 `down -v` 作为日常停止命令，它会删除数据库卷。

## 10. 常见问题

| 现象 | 检查与处理 |
|---|---|
| `brew` / `node` 找不到或 Node 版本不对 | 核对第 1 节 PATH；新开登录终端，检查 `which brew`、`which node`、`node --version`。 |
| 私有仓 `Repository not found` | `gh auth status` 检查账号；确认该账号有仓库权限，再执行 `gh auth setup-git`。 |
| 提示换机分支不存在 | 确认仓库 URL 和旧机同步结果，不回退到 main 冒充最新进度。 |
| 连不上 Docker daemon | 打开 Docker Desktop，等初始化完成，先让 `docker info` 成功。 |
| 5432 / 6379 / 1025 / 8000 / 3000 被占用 | 用 `lsof -nP -iTCP:端口号 -sTCP:LISTEN` 找进程；确认用途后处理，不随意杀进程或删卷。若改端口，同步改连接串/代理/Origin。 |
| 数据库认证失败 | 核对 `.env` 与 Compose 用户、密码、库名，重新 source；已有卷不会因改 Compose 密码自动重置账号。 |
| API 缺环境变量或启动失败 | 必须在 API 根目录加载 `.env`；检查 PG/Redis healthy、迁移成功与协议夹具路径。 |
| `pytest` 有 skip | 核对 `INTEGRATION_DATABASE_URL` 已导出且开发库迁移到 head；按 skip 原因处理。 |
| 收不到登录验证码 | 当前邮件只打印在 SMTP 终端 A；确认它先启动，API 配置 SMTP 1025、TLS=false。 |
| 登录 403 或 Cookie 不保持 | 浏览器、WEB_ORIGIN 都用 `http://127.0.0.1:3000`，检查是否意外使用 localhost/自动切到其他端口。 |
| Next.js 尝试使用 3001 | 先处理 3000 冲突再启动，避免与后端 WEB_ORIGIN 不一致。 |
| 原生依赖架构报错 | 确认终端与 Node 是 arm64、Python 是新机 uv 安装；重新安装新机依赖，不搬 Windows 缓存。 |
| Git 拉取/推送网络失败 | 核对新机网络与认证；需要代理时用新机实际地址，不沿用 Windows 代理或关闭 TLS 验证。 |

## 11. 换机完成检查表

- [ ] 三仓同级、从换机分支恢复，同步核验通过。
- [ ] Node 24/arm64、uv 管理的 Python 3.12 可用，锁文件未被意外修改。
- [ ] PG/Redis healthy，本机 `.env` 正确且被 Git 忽略，迁移与清单一致。
- [ ] API 检查与无意外 skip 的回归、Web check 在 Mac 上通过。
- [ ] SMTP/API/Web 可启动，PC 浏览器能完成验证码登录、资料与额度查看。
- [ ] Mac 实测结果与未通过项已写入交付验证记录/检查点，未将启动成功记成 G4 完成。
- [ ] 编码工具已读取最新检查点，下一任务与 PBI/AC 对齐并使用任务分支。
- [ ] 完成增量已提交并核验三仓远端同步，旧机暂停编辑。
