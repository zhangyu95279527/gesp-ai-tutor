# 项目上下文 — GESP AI Tutor

本文件记录实例级背景、约定与术语，供各阶段 agent 会话按需读取。

## 产品背景
- 产品名称: GESP AI Tutor
- 一句话描述: 面向 GESP（CCF 编程能力等级认证）备考学生的 AI 编程辅导产品
- 产品类型: 互联网产品（面向外部用户，通过互联网提供服务）
- 当前阶段: discovery（尚未开始）

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
