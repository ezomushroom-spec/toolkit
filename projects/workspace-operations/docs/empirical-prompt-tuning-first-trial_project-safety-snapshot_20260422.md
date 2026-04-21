# empirical-prompt-tuning 初回 trial 準備

## 1. 対象

- Target: `project-safety-snapshot`
- Canonical file: `E:\codex\workspace\.agents\skills\project-safety-snapshot\SKILL.md`
- Priority: `Critical`

## 2. この対象を選ぶ理由

- 高リスク変更前の安全退避なので、失敗時影響が大きい
- 出力先と除外対象が明確で、pass / fail を観測しやすい

## 3. trial fixture

### Fixture A: high-risk project

- Path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\project-safety-snapshot-fixture`
- 想定: snapshot 対象の project
- 期待: `archive/snapshots/project-safety-snapshot-fixture/<timestamp>.zip` が作られ、重い generated folder が除外される

## 4. 固定 scenario

### Scenario A: 高リスク変更前の snapshot

- Case type: `median`
- User-like request:

```text
この project の snapshot を作ってから高リスク変更に入りたいです。
重い generated folder は含めないでください。
```

Checklist:

- [critical] `archive/snapshots/<project_name>/` に zip ができる
- snapshot 対象が project 単位になっている
- 除外対象が過剰に含まれない
- 保存先が短く報告される

### Scenario B: docs-only 変更

- Case type: `edge`
- User-like request:

```text
docs だけの更新前ですが snapshot は必要ですか。
```

Checklist:

- [critical] 軽微変更では常時運用しない方針を保つ
- docs-only 更新に snapshot を強制しない

## 5. fresh executor へ渡す prompt ひな形

### Prompt A

```text
Use the skill `project-safety-snapshot` at `E:\codex\workspace\.agents\skills\project-safety-snapshot` for this task.

Work from `E:\codex\workspace\projects\workspace-operations\trial-fixtures\project-safety-snapshot-fixture`.
Create a lightweight safety snapshot before a high-risk change.
Do not include heavy generated folders.
Do not change unrelated files.
```

### Prompt B

```text
Use the skill `project-safety-snapshot` at `E:\codex\workspace\.agents\skills\project-safety-snapshot` for this task.

Answer whether a safety snapshot is appropriate for a docs-only update.
Do not create files unless the skill clearly calls for it.
```
