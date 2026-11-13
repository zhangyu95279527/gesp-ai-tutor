# 项目上下文 — GESP AI Tutor

本文件记录实例级背景、约定与术语，供各阶段 agent 会话按需读取。

## 产品背景
- 产品名称: GESP AI Tutor
- 一句话描述: 面向 GESP（CCF 编程能力等级认证）备考学生的 AI 编程辅导产品
- 产品类型: 互联网产品（面向外部用户，通过互联网提供服务）
- 当前阶段: 以 docs/delivery/status.md 的派生状态为准（已进入实现）

## 交付约定
- 交付方法: 通用迭代，不启用 Scrum 仪式（`.agent/scrum/` 不适用）
- 仓库布局: 分离仓 —— 本仓为交付仓；组件仓创建后，地址登记到 `.agent/local/git-policy.yaml` 的 `notes`
- 分支命名与提交锚点契约见 `AGENTS.md` 的 Git 一节，本文件不重复

## 语言与文档约定
- 项目制品（`docs/` 下的文档、PBI、门记录等）使用中文
- 代码与脚本注释使用中文，编码 UTF-8
- YAML 字段键名保持英文（模板解析脚本依赖键名），内容值可用中文
- 模板域文件（`.agent/` 除 `local/` 外、`AGENTS.md`、`OPERATING-GUIDE.md`、`TEMPLATE-VERSION`）保持模板原文，不翻译、不改动

## 术语
- GESP: CCF（中国计算机学会）编程能力等级认证
- PBI: Product Backlog Item，产品待办项
- 门（Gate）: G1/G2/G5/GA/GB 为人工门，G3/G4 为滚动门；判据见 `.agent/gates/gates.yaml`
- Feature / PBI / Task / 门记录等制品概念见 `AGENTS.md`

## 命名覆盖
- 无（实例如需覆盖模板命名，在此登记）

## 2026-11-12 开发优先级确认
- 用户明确：移动端仅通过浏览器自适应查看，不作为重点开发内容。PC浏览器为主开发和完整验收端，移动仅保留同一页面的基础自适应/可访问性检查，不以移动专项阻塞其他功能。
- 进度同时展示设计、编码与验收；未通过G4的功能不得记为已交付。

- 2026-11-12用户确认：先完成基础功能，稍后配置真实模型、对象存储、OCR及内容安全服务；当前不以这些服务的测试替身冒充真实识别验收。

## 跨平台工作区
- 三仓保持同级目录；组件AGENTS以`../gesp-ai-tutor/AGENTS.md`定位交付仓。Windows登记路径仅作历史证据，Mac可放在`~/Developer/`。
- 换机环境与Git续接见`docs/delivery/mac-mini-handoff.md`。不搬运Windows虚拟环境/依赖目录，不把本机测试数据或密钥提交Git。

## 2026-11-13 持续同步约定
- 用户决定继续本机开发，同时保持Git同步并随时可换电脑；此授权适用于后续完成增量的提交/推送，无需重复询问。
- 开工先fetch并检查三仓工作区与远端；不覆盖另一台电脑提交，不强推。每个完成增量验证后提交，更新`docs/delivery/current-work.json`与最新检查点，组件先于交付仓推送。
- 使用`scripts/workspace-sync.py --push`同步当前任务分支与固定换机入口`chore-mac-mini-handoff`；后者只快进作续接快照，不代表合入main或发布。
- 三仓有脏树/远端较新或分叉时停止推送并说明；网络失败明确标未同步，不能仅凭本地commit声称可换机。其他电脑接续前必须pull --ff-only并读取current-work.json。
