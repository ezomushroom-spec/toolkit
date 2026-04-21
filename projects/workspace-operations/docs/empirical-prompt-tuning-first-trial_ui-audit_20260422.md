# empirical-prompt-tuning 初回 trial 準備

## 1. 対象

- Target: `ui-audit`
- Canonical file: `E:\codex\workspace\.agents\skills\ui-audit\SKILL.md`
- Priority: `Important`

## 2. この対象を選ぶ理由

- 既存 UI の問題抽出力を見やすい
- findings を構造・安全性・状態表示へ寄せられるか確認したい
- 問題が少ないケースで無理に過剰診断しないかも見たい

## 3. trial fixture

### Fixture A: cluttered-screen

- Path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\ui-audit-cluttered`
- 想定: 主操作が埋もれ、危険操作と通常操作が近く、状態表示も弱い画面

### Fixture B: mostly-clear-screen

- Path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\ui-audit-safe`
- 想定: 比較的素直で、重大問題は少ない画面

## 4. 固定 scenario

### Scenario A: 問題を拾うべき画面

- Case type: `median`
- User-like request:

```text
この画面の UI を監査して、使いにくさや危ない点を整理してください。
```

Checklist:

- [critical] 主操作 / 危険操作 / エラー表示 / 状態表示の問題に触れる
- findings が具体的である
- 単なる見た目の好みだけに寄らない
- project-specific rule 候補があれば触れる

### Scenario B: 問題が少ない画面

- Case type: `edge`
- User-like request:

```text
この画面に大きな問題があるか見てください。
```

Checklist:

- [critical] 無理に大きな問題を作らない
- 問題が軽微なら軽微と伝える
- residual risk があれば短く触れる

## 5. fresh executor へ渡す prompt ひな形

### Prompt A

```text
Use the skill `ui-audit` at `E:\codex\workspace\.agents\skills\ui-audit` for this task.

Audit the screen described in `E:\codex\workspace\projects\workspace-operations\trial-fixtures\ui-audit-cluttered\screen.md`.
Do not write code.
```

### Prompt B

```text
Use the skill `ui-audit` at `E:\codex\workspace\.agents\skills\ui-audit` for this task.

Audit the screen described in `E:\codex\workspace\projects\workspace-operations\trial-fixtures\ui-audit-safe\screen.md`.
Do not write code.
```
