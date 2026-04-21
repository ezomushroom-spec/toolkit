# empirical-prompt-tuning staging manifest

## 1. 目的

今回の `empirical-prompt-tuning` 導入差分を、実際の staging 単位へ落とす。

この文書は、unrelated diff を巻き込まずに commit 境界を保つための作業用正本である。

## 2. staging unit A: protocol 導入本体

この unit には次を含める。

- `.agents/skills/empirical-prompt-tuning/SKILL.md`
- `.agents/skills/empirical-prompt-tuning/references/templates.md`
- `.agents/skills/project-scaffolder/SKILL.md`
- `.agents/skills/desktop-dnd-path-resolution/SKILL.md`
- `.agents/skills/windows-batch-launcher/SKILL.md`
- `.agents/skills/subagent-debug-review/SKILL.md`
- `AGENTS.md`
- `docs/skill-inventory.md`
- `docs/subagent-prompts.md`

この unit には次を含めない。

- `docs/README.md`
- `docs/quality-gates.md`
- `docs/workflow.md`
- `.codex/config.toml`
- archive / migration 系差分
- 別件 project 追加

## 3. staging unit B: workspace-operations 文書群

この unit には次を含める。

- `projects/workspace-operations/PROJECT_SUMMARY.md`
- `projects/workspace-operations/START_HERE.md`
- `projects/workspace-operations/docs/empirical-prompt-tuning-*.md`
- `projects/workspace-operations/docs/skill-validator-policy-gap_20260422.md`
- `projects/workspace-operations/docs/validator-recording-rule_20260422.md`
- `projects/workspace-operations/docs/snapshot-trial-artifact-policy_20260422.md`

必要に応じて snapshot 証跡を参照してよいが、zip 自体は commit 対象にしない。

## 4. 現時点で保留するもの

次は今回の 2 unit staging には入れない。

- `docs/projects-index.md`
- `projects/attendance-manager/`
- `projects/agents-governance-audit/` の今回と無関係な差分
- `projects/adult-ai-monetization-loop/`
- `projects/mosaic-remake-tk/`
- `projects/sd-prompt-helper/`
- `.codex/agents/python-web-electron-shell-migrator.toml` の移動関連
- `archive/docs/python-web-electron-shell-migrator.toml.archived`

## 5. 実行順

1. branch を切る
2. staging unit A だけを add する
3. diff を確認して 1 本目の commit を作る
4. staging unit B だけを add する
5. diff を確認して 2 本目の commit を作る
6. 最後に push / PR を判断する
