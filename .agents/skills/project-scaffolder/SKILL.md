---
name: project-scaffolder
description: Scaffold a new project under this workspace using the standard project templates. Use when a new project should be created under `projects/{name}/` with `AGENTS.md`, `START_HERE.md`, `PROJECT_SUMMARY.md`, and initial docs copied from `docs/templates/`, while keeping placeholders for unknown details instead of inventing full specs.
---

# Purpose

新しい project を、この workspace の標準構成で素早く立ち上げる。
フォルダ作成、template コピー、最小限の初期穴埋めを安定して行う。

# Core rules

- 既存 project 名と衝突したら止まる。
- project 名は安全な folder 名へ正規化して使う。
- project 名が明示されない場合は、目的や summary から短く識別しやすい名前を作り、その名前を folder 名に使う。
- 分からない項目は埋めすぎず、未確定欄を残す。
- AI が project の詳細を勝手に作り込まない。
- まず標準構成を作り、その後に brief や計画で中身を詰める。
- 日本語 project 名も使える。Windows で危険な文字だけ除外する。

# Script

この skill には `scripts/scaffold.py` がある。
新規 project 作成では、まずこの script を使う。

基本実行:

```powershell
python .agents/skills/project-scaffolder/scripts/scaffold.py --name "<project-name>" --summary "<one-line-purpose>"
```

# What this skill creates

- `projects/<slug>/`
- `projects/<slug>/docs/`
- `AGENTS.md`
- `START_HERE.md`
- `PROJECT_SUMMARY.md`
- `docs/current-state-check.md`
- `docs/implementation-plan.md`
- `docs/pre-implementation-decision.md`

# After scaffolding

script 実行後は、必要に応じて次を行う。

1. `START_HERE.md` の最初の一手を整える
2. `PROJECT_SUMMARY.md` の正本候補を追記する
3. 実装前なら `pre-implementation-diagnosis` や `implementation-planner` へつなぐ

# Do not use this skill for

- 既存 project の大規模 rename
- project 移設
- archive からの復元
- project 構造を大きく変える再編
