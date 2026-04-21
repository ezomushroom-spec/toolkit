# empirical-prompt-tuning 初回 trial 準備

## 1. 初手対象

- Target: `project-scaffolder`
- Canonical file: `E:\codex\workspace\.agents\skills\project-scaffolder\SKILL.md`
- Priority: `Critical`

## 2. この対象を先に選ぶ理由

- `projects/<name>/` の正本構造を直接作るため、誤ると後続案件の導線が崩れる
- 生成物が明確で、pass / fail を比較的観測しやすい
- `衝突時に止まる` `作り込みすぎない` `標準文書が揃う` という判定軸がチェックしやすい
- `windows-batch-launcher` や `subagent-debug-review` より、初回 empirical 評価のノイズが少ない

## 3. Iteration 0 の静的レビュー結果

- `description` と body の大きな乖離は見当たらない
- 作成物の範囲は本文で十分に列挙されている
- `After scaffolding` にあった古い参照は修正済み
- まだ弱い点は、`どういう入力を subagent に渡せば過剰補完を防げるか` の実行面

## 4. 固定 scenario

### Scenario A: 中央値ケース

- Case type: `median`
- User-like request:

```text
新しい project を立ち上げたいです。
目的は「画像整理ツールの試作」です。
workspace の標準構成で作ってください。
```

Checklist:

- [critical] `projects/<slug>/` と標準 3 文書が作られる
- `docs/current-state-check.md` `docs/implementation-plan.md` `docs/pre-implementation-decision.md` が揃う
- summary は目的を外しすぎない
- 不明項目を勝手に詳細化しすぎない
- 既存 project と名前衝突した場合は止まる方針を保つ

### Scenario B: 日本語名ケース

- Case type: `edge`
- User-like request:

```text
「画像仕上げメモ整理」という名前で新しい project を作りたいです。
workspace の標準構成でお願いします。
```

Checklist:

- [critical] Windows で危険な文字を避けた folder 名になる
- 本来の project 名の意味が不自然に失われない
- 標準構成の文書が揃う
- 未確定事項を勝手に作り込みすぎない

## 5. fresh executor へ渡す prompt ひな形

以下は、委任許可がある回に fresh executor へそのまま渡す想定の prompt。
評価者向けの背景説明を混ぜず、task-local context だけ渡す。

### Prompt A

```text
Use the skill `project-scaffolder` at `E:\codex\workspace\.agents\skills\project-scaffolder` for this task.

Create a new project in this workspace for an image organization tool prototype.
Use the workspace standard structure.
Do not invent detailed specs for unknown items.
Stop if the target project name conflicts with an existing one.
```

### Prompt B

```text
Use the skill `project-scaffolder` at `E:\codex\workspace\.agents\skills\project-scaffolder` for this task.

Create a new project in this workspace with the intended name `画像仕上げメモ整理`.
Use the workspace standard structure.
Keep unknown details as placeholders instead of inventing full specs.
Avoid unsafe Windows path characters in the project folder name.
```

## 6. 結果記録テンプレート

### Trial Result: project-scaffolder / Scenario A

- Executor separation: `empirical` or `static-only`
- Success:
- Failed `[critical]` items:
- Precision:
- Tool usage:
- Duration:
- Retry count:
- Ambiguous points:
- Discretion completions by executor:
- Next revision theme:

### Trial Result: project-scaffolder / Scenario B

- Executor separation: `empirical` or `static-only`
- Success:
- Failed `[critical]` items:
- Precision:
- Tool usage:
- Duration:
- Retry count:
- Ambiguous points:
- Discretion completions by executor:
- Next revision theme:

## 7. 判定メモ

- この target では、`標準構成が揃うか` と `作り込みすぎないか` の両方を見ないと false positive になりやすい
- 生成物ができたことだけで成功扱いにせず、未知項目を埋めすぎていないかも確認する
- 委任未許可の回では empirical 実施済み扱いにしない
