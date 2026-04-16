---
name: project-safety-snapshot
description: Create a lightweight safety snapshot before high-risk changes. Use when a project is about to undergo architecture changes, broad UI remakes, destructive refactors, or other risky edits and a quick rollback archive should be created under `archive/snapshots/` without copying heavy generated folders.
---

# Purpose

高リスクな変更の直前に、軽量な安全退避を作る。
Git を前提にせず、重い生成物を除外した zip を `archive/snapshots/` に残す。

# Use this skill for

- 大きな UI 改修
- アーキテクチャ変更
- project 全体に及ぶ refactor
- 既存挙動を壊す可能性が高い変更

# Do not use this skill for

- 軽微な 1 ファイル修正
- docs だけの更新
- 毎回の通常作業

# Script

この skill には `scripts/snapshot.py` がある。
高リスク変更の前には、まずこの script を実行する。

基本実行:

```powershell
python .agents/skills/project-safety-snapshot/scripts/snapshot.py --project "E:\codex\workspace\projects\<name>"
```

# Snapshot rules

- 対象は原則として project 単位
- 出力先は `archive/snapshots/<project_name>/<YYYYMMDD_HHMMSS>.zip`
- 次を除外する
  - `venv`
  - `node_modules`
  - `__pycache__`
  - `build`
  - `dist`
  - `*.log`
  - `*_profile`
- 作成後は、保存先を短く報告してから実作業へ入る

# Style

- snapshot は常時運用ではなく、危ない変更前だけに使う
- 戻し方の説明までは求めないが、保存先は必ず明示する
