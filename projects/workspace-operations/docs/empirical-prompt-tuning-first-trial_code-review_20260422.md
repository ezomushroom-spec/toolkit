# empirical-prompt-tuning 初回 trial 準備

## 1. 対象

- Target: `code-review`
- Canonical file: `E:\codex\workspace\.agents\skills\code-review\SKILL.md`
- Priority: `Important`

## 2. この対象を選ぶ理由

- 使用頻度が高い
- findings の質、優先度、抑制度合いを見やすい
- `問題を見つけるべきケース` と `無理に粗探ししないケース` の両方を試せる

## 3. trial fixture

### Fixture A: issue-present

- Path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\code-review-issue`
- 想定: 明確な不具合と運用リスクを含む変更断片

### Fixture B: mostly-safe

- Path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\code-review-safe`
- 想定: 小さくて比較的安全な変更断片

## 4. 固定 scenario

### Scenario A: findings を出すべきケース

- Case type: `median`
- User-like request:

```text
この変更をレビューして、主要なリスクを優先順で挙げてください。
```

Checklist:

- [critical] findings が優先度順になる
- file / line 参照がある
- bug / risk が主で、単なる style 指摘に寄らない
- 主要な未確認リスクに触れる

### Scenario B: 問題なしを言えるケース

- Case type: `edge`
- User-like request:

```text
この変更をレビューして、問題があるか見てください。
```

Checklist:

- [critical] 無理に findings を捏造しない
- 問題なしなら明示する
- residual risk や testing gap があれば短く触れる

## 5. fresh executor へ渡す prompt ひな形

### Prompt A

```text
Use the skill `code-review` at `E:\codex\workspace\.agents\skills\code-review` for this task.

Review the change artifacts inside `E:\codex\workspace\projects\workspace-operations\trial-fixtures\code-review-issue`.
Focus on bugs, regressions, safety risks, and missing verification.
Do not edit files.
```

### Prompt B

```text
Use the skill `code-review` at `E:\codex\workspace\.agents\skills\code-review` for this task.

Review the change artifacts inside `E:\codex\workspace\projects\workspace-operations\trial-fixtures\code-review-safe`.
Focus on whether there are meaningful findings.
Do not edit files.
```
