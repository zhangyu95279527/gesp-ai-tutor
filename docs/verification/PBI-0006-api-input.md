# PBI-0006 服务端输入基础验证 — 2026-11-12

状态：TASK-0014 in-verification；完整PBI仍in-progress，TASK-0013 draft。无G4或发布。

## 代码与环境

- API：E:/AIworkspacke/gesp-tutor-api，task-0014-input-contracts / 05370ed，承接此前登录/资料/限额分支。
- CPython3.12.16；新增Pillow12.3.0，uv.lock已锁定。`uv sync --locked --offline`通过，49项解析、48个已安装包检查。
- 全回归使用INTEGRATION_DATABASE_URL指向本机5432 PG协议代理→PGlite5433；Redis用fakeredis，邮件适配器使用临时本机收件服务。这些不等于真实PG/Redis或线上邮件验证。
- 本轮Web无变更、未重跑前端；原本机8000服务未重启，HTTP证据来自当前代码的ASGI应用工厂测试实例，不声称已部署。

## 命令与捕获输出

在API仓执行：

```powershell
.venv/Scripts/ruff.exe check src tests
.venv/Scripts/mypy.exe src
$env:INTEGRATION_DATABASE_URL='postgresql://postgres:postgres@127.0.0.1:5432/postgres?sslmode=disable'
.venv/Scripts/python.exe -m pytest -q
```

最终输出：

```text
All checks passed!
Success: no issues found in 23 source files
........................................................................ [ 59%]
..................................................                       [100%]
122 passed in 3.16s
```

首次专项43项通过但ruff有一处旧式TypeVar规范问题；已改Python3.12泛型语法，并增加3项IO失败/解压炸弹测试，再执行上述全回归。最终122项全部执行，无skip；新增输入测试46项，既有76项仍通过。未运行远程CI。

## 可复核合同证据

来源：API仓tests/test_input.py；全部合成题干、账号、图片与适配器，未调用真实外部识别或内容安全。

- SessionInput严格拒绝多来源、空来源、过短题干、10001字符、5001字符代码、错误JSON类型、额外owner、外部URL与路径穿越。10000/5000个Unicode补充平面字符可保留，疑问点和代码不裁剪。
- UploadInput校验PNG/JPEG/WebP、正整数size_bytes及10MiB上限，布尔值和字符串数值不隐式转换。
- Pillow实际编码的PNG/JPEG/WebP可解码；伪装HTML、MIME不符、截断、空文件、超字节上限拒绝。恰好10MiB、超2000万像素、极大解压尺寸及多帧APNG均有测试。
- 存储按当前owner和key读取，模拟非本人对象返回image_not_found；损坏图片在安全/识别调用前被拒绝。真实适配器的归属授权仍未实现。
- 安全接口逐项检查题干、代码、疑问及图片；模拟拒绝阻断识别。存储和安全IO错误转503，不反射提供方细节。生产默认未装配这些适配器，测试mock不算内容安全有效性验收。
- 所有HTTP测试注入禁止任何属性访问的NoQuota对象，拒绝路径若触及额度服务即失败；实际均通过。未执行任何会话写入或模型调用。

## HTTP断言

认证写保护为既有X-Requested-With/同源Origin，且必须携带1～128位ASCII幂等键。此阶段只校验键格式，未实现成功操作的持久幂等/重放。

| 输入（均已登录并携带合法写保护/键，特殊说明除外） | 实际断言 |
|---|---|
| POST /api/uploads，PNG/100字节合法元数据 | 503 {code:storage_unavailable} |
| POST /api/tut/sessions，合法题干 | 503 {code:safety_unavailable} |
| POST /api/tut/sessions，合法图片key | 503 {code:storage_unavailable} |
| 同键重复上述请求 | 同样503，无session_id/echo，no-store，不访问额度 |
| 无写保护/跨域Origin | 403 |
| 无登录态 | 401 |
| 空/超长/带空格幂等键 | 422 invalid_idempotency_key |
| 非法来源、超长代码、额外字段 | 422 invalid_input，仅白名单fields，不返回题干或额外字段名 |
| 非JSON/损坏JSON | 415 json_required / 422 invalid_input |
| 声明Content-Length超256KiB / 分块传输实测超过256KiB | 413 request_too_large |

## AC与DoD差距

| AC | 本轮服务端部分证据 | 完整AC状态 |
|---|---|---|
| 1 同区图文即贴即传 | 输入请求合同已校验；上一轮有PC粘贴证据 | blocked：私有存储和前端真实提交未接入 |
| 2 文本/图片上限 | Unicode长度、元数据、真实字节/解码及传输边界测试通过 | blocked：真实上传路径尚未调用字节校验函数 |
| 3 选择图片/无直拍 | 服务端支持三种截图格式，上一轮选择器证据保留 | blocked：真实上传与移动相册链路未验 |
| 4 无效提示不计次 | 短文本/坏图/假类型拒绝；NoQuota证明基础拒绝路径不扣次 | blocked：非题目语义、模糊、安全模型与真实额度集成未验 |
| 5 代码及疑问 | 服务端合同与原文保留测试通过 | blocked：持久会话/识别回显未集成 |

DoD：规范/类型/本机全回归、依赖锁与文档通过；完整AC、真实服务E2E、安全有效性、AI评估与发布部署未完成，不能标done。

## 保留边界

上传签名、对象归属账本、资源预算/频率保护、持久会话与幂等认领必须在TASK-0013齐备后才允许真实识别。IntakeService即使注入识别适配器，也会在会话持久化未交付时返回session_unavailable且不调用模型。图片20MP/单帧与题干10字符阈值是显式实现假设，不是完整模糊/语义判断。存储适配器须限制读取字节量，不能先无界下载再做10MiB检查。
