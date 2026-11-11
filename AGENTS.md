# AI Product Delivery Project Instructions

This system exists for one purpose: agents help each role do its own job and deliver. Every mechanism here serves that purpose; anything that does not is removed.

## Core model
This repository uses a universal delivery model. Scrum is a selectable delivery method, not the universal process. Coding agents are executors, not the methodology.

Canonical core flow:
`Product → PRD → Feature/PBI → Task → Verification → Release`

Do not introduce artificial workflow layers merely to organize people.

## Architecture
Architecture Discovery reduces material uncertainty. Architecture Baseline defines stable current boundaries. Feature Technical Design applies that baseline to a current Feature/PBI. Architecture Evolution changes stable architecture explicitly through review/ADR.

Component/Service/Repository are engineering references, not mandatory workflow stages.

## Agile
The model is iterative. Discovery, PRD, design and architecture may be revisited when evidence changes the product or technical understanding.

If Scrum is selected, use `.agent/scrum/` for Product Goal, Product Backlog, PBI/User Story, Sprint Goal, Sprint Backlog, Daily Scrum, Review, Retrospective and Definition of Done.

## Agent behavior
Before acting: identify stage/artifact/task; read only required context; separate confirmed facts, assumptions, options and open questions; state intended outputs and stop conditions.

During work: ask only material blocking questions; keep assumptions explicit; avoid unrelated refactors; keep changes reviewable.

Before completion: report changed artifacts/files, verification evidence, unmet acceptance criteria, unresolved risks/questions, and checkpoint state for long-running work.

Context discipline:
- One prompt scopes one session; do not carry one stage's chat into another stage.
- Read in layers. Fixed: this file, the stage prompt and its listed skill. On demand: only the paths in the prompt's Context block. Locate project state via `docs/delivery/status.md`; search to find anything not listed, never sweep `docs/` wholesale. `EXAMPLE.md` and `OPERATING-GUIDE.md` are human onboarding material; do not read them in stage sessions.
- Artifacts, not chat history, are project memory: read only the artifacts named by the prompt and the task at hand.
- When work outgrows one session, write a checkpoint from `.agent/templates/checkpoint.md`; resume from the checkpoint plus the artifacts, never by re-reading chat scrollback.

## Traceability
Every implementation Task must trace to a Feature/PBI and Acceptance Criteria. A Feature may affect multiple repositories/components and one repository/component may support many Features. Record affected repositories/components on the Task when known.

## Git
Trunk-based development: `main` stays releasable; work reaches it through short-lived branches, except rolling-gate artifact updates (G3/G4) which agents push directly. Instantiation, upgrade commands and commit cadence live in `OPERATING-GUIDE.md`; this section is the naming and merging contract.

Branch naming: `<type>-<id>[-<slug>]`, lowercase letters, digits and hyphens only.
- Gate branch (delivery repo): `<gate>-<artifact>` such as `g1-product-brief`, `g2-prd`, `ga-baseline`; carries one human-gate decision (G1/G2/G5/GA/GB); the PR review is the gate decision, artifacts and gate record land with the merge. Gate-recycle rework continues on the same branch.
- Task branch (code repo): `task-0001-short-desc`; implementation at Task granularity; merges back with G4 evidence attached; recycle rework continues on the same branch.
- `fix-...` / `chore-...`: changes tied to neither a gate nor a Task, including all template-repo work.
- `hotfix-v1.2.1-desc`: cut from the affected release tag; merge the fix back to `main` (and to the release branch when one exists) before tagging the patch. The back-merge to `main` is mandatory.
- `release-x.y.z`: cut on demand from a release tag when a shipped line needs patches; never pre-created.
- `template-upgrade-v0.5`: template upgrade in an instance; the PR carries the pre-merge diff review.

Tags:
- Instance product release: semver tag on `main` (e.g. `v1.2.0`) when the release gate passes; multi-repo products pin component tags/commits in the release record under `docs/delivery/releases/`.
- Template release: semver tag equal to `TEMPLATE-VERSION`, with migration notes in commit messages.

Commit messages: `<anchor> <content>`, one line; the anchor makes `git log --grep` traceable across commit, Task, PBI and gate record. Anchors: `TASK-0001` implementation, `PBI-0001` PBI artifacts, `G1 go` / `G3 recycle` gate events (gate record and regenerated `status.md` ride in the same commit), `Release v1.2.0`, `chore`.

House rules:
- Commit durable artifacts and completed increments.
- Never commit secrets or private data.
- Instance naming overrides live in `.agent/local/project-context.md`; platform-side git policy (branch protection, reviewer mapping, direct-push exceptions) lives in `.agent/local/git-policy.yaml`. `.agent/local/` and `docs/` belong to the product instance and are never overwritten by template updates.

## Large file chunked writing
A single reply has a hard output-length limit. To avoid truncation ("output too long, type continue"):
- Never write more than ~300 lines (or ~50KB) of content in one tool call. Write the first chunk, then append the rest with multiple Edit calls; keep each chunk under ~300 lines.
- Chain the chunks continuously within the same turn. Do not pause between chunks and do not ask the user to confirm or type "continue".
- Prefer extracting shared assets (common CSS, components, constants, SVG sprites) so individual files stay small.
- Keep prose to the user minimal during long writes; spend the output budget on file content.
