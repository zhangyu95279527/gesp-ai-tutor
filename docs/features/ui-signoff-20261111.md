# MVP UI 精细稿定稿记录 — 2026-11-11

Status: approved

## 确认依据与范围

用户在获知现稿范围及未完成项后明确确认：「可以定稿了」。本记录批准现有 5 套静态高保真原型（共 76 帧）、共享设计样式与日限额组件设计，作为视觉与交互实现基线；P0/P1/P2 批次保持既有划分。

| 模块 | 批次 | 规格 | 精细稿 |
|---|---|---|---|
| FEAT-001 账号与合规 | P0 | [设计文档](feat-001-ux-ui-design.md) | [原型](feat-001-ux-ui/index.html)（14 帧） |
| FEAT-002 AI 讲题 | P0 | [设计文档](feat-002-ux-ui-design.md) | [原型](feat-002-ux-ui/index.html)（21 帧） |
| FEAT-003 错因诊断 | P0 | [设计文档](feat-003-ux-ui-design.md) | [原型](feat-003-ux-ui/index.html)（13 帧） |
| FEAT-005 日限额组件 | P0 | [设计文档](feat-005-ux-ui-design.md) | 复用讲题等原型中的用量/超限组件 |
| FEAT-007 真题模考 | P1 | [设计文档](feat-007-ux-ui-design.md) | [原型](feat-007-ux-ui/index.html)（15 帧） |
| FEAT-008 错题本 | P2 | [设计文档](feat-008-ux-ui-design.md) | [原型](feat-008-ux-ui/index.html)（13 帧） |

各设计文档已同步为 approved；文末定稿确认固定现稿选择，并区分后续技术或业务细化事项。HTML 与共享 CSS 保持本次确认时的内容，未以定稿为由重画页面。

## 交接边界与待办

- 分享卡片、获客落地页、产品邀请码不在本次现稿批准范围。现有设计记为暂缓，PRD 仍含 P0 要求；范围口径差异须由产品后续同步，本次未批准删除 PRD 要求，也未宣称这些页面已完成。
- 运营看板与盲评采用既有工具界面，参见 FEAT-006 技术设计；本次不新增自研运营界面。
- 人机验证供应商、正式示例题内容、模考重考成绩规则仍由技术设计/PBI 精炼落实；现稿占位不得被当作已实现功能。
- ADR-001/002 继续为 draft，等待 GB；真实变式运行与内测访问边界依赖保留。
- UI 批准不改变 PBI 执行状态，不等同于 G3、G4、GB 或发布通过。开发、QA 继续按原 AC 验证断线恢复、资源预算、删除副本、延迟及移动作答。
- 本次未执行浏览器视觉验收、交互端到端或性能测试；此前静态检查与风险见[设计评审记录](design-review-20261111.md)。

## 定稿源文件校验值

SHA-256 针对原型与共享样式的原始文件字节，供后续核对本次获批的静态源文件。设计规格以本记录链接及各文档的定稿确认段为准。

| 文件 | SHA-256 |
|---|---|
| [feat-001-ux-ui/index.html](feat-001-ux-ui/index.html) | `9a9762b2da93e03bc519712c256575216c7ab7d3698a434b2a11e022c144fb5e` |
| [feat-002-ux-ui/index.html](feat-002-ux-ui/index.html) | `d86139cb2c3ab6db96ed331bf60474e6233f10e0ef972c8c667a3d9974afaf8a` |
| [feat-003-ux-ui/index.html](feat-003-ux-ui/index.html) | `41b23d0484ed5c70063b602888df3b47c4ed557b621ec7a2522aa466f16b51e5` |
| [feat-007-ux-ui/index.html](feat-007-ux-ui/index.html) | `22d4083e86dcbf3e610725046efd7dd7fe340605ffc4a02556d41e4dddc342ac` |
| [feat-008-ux-ui/index.html](feat-008-ux-ui/index.html) | `9e8e45494a35ba245560fa46bc862e0360223f39ceb4f2545cadc66b017f976b` |
| [_shared/design-system.css](_shared/design-system.css) | `4170430e5e76b58bd0809608bdd04333a580102c1a5428672773c3bae08b6125` |
