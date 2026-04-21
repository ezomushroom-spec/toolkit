# empirical-prompt-tuning 初回 trial 準備

## 1. 対象

- Target: `plan-review`
- Canonical file: `E:\codex\workspace\.agents\skills\plan-review\SKILL.md`
- Priority: `Opportunistic`

## 2. この対象を選ぶ理由

- 実装前に scope 過大や phase 分割不足を見抜けるかは workspace の安全性に直結する
- code ではなく plan 入力をどう厳しく読むかを評価しやすい
- `implementation-planner` と違い、欠陥発見が主目的なので、過度に甘い review にならないかを見たい

## 3. Iteration 0

- description と body の整合は取れている
- five perspectives、severity、go/revise 判定が明示されている
- 追加で見たい曖昧さは「scope が広すぎる計画を本当に split 判定できるか」と「だいたい安全だが未記載の確認観点を拾えるか」

## 4. trial fixture

### Fixture A: broad-remake

- Path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\plan-review-broad-remake`
- 想定: scope が広く、phase 分割も戻し方も弱い remake plan

### Fixture B: safe-but-incomplete

- Path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\plan-review-safe-but-incomplete`
- 想定: 小さく安全寄りだが、確認観点や missing conditions が少し抜けている

## 5. 固定 scenario

### Scenario A: broad remake plan

- Case type: `median`
- User-like request:

```text
このリメイク計画で問題ないか見てください。実装前に穴があれば厳しめに指摘してください。
```

Checklist:

- [critical] scope too broad なら `split into phases first` が出る
- 挙動保全や戻し方の弱さを拾う
- 5 観点に沿ってレビューする
- severity を伴って具体的に指摘する

### Scenario B: safe but incomplete plan

- Case type: `edge`
- User-like request:

```text
この小さめの UI 改善計画を実装前にチェックしてください。足りない確認観点があれば知りたいです。
```

Checklist:

- [critical] vague な安心判定で流さない
- missing conditions を拾う
- 過剰に `split into phases first` へ寄せない
- `revise first` か `ready to implement` を根拠つきで出す

## 6. fresh executor へ渡す prompt ひな形

### Prompt A

```text
日本語で回答してください。
Use the skill `plan-review` at `E:\codex\workspace\.agents\skills\plan-review\SKILL.md`.

Read `E:\codex\workspace\projects\workspace-operations\trial-fixtures\plan-review-broad-remake\plan.md`.
Review the plan before implementation and report risks and revisions only.
Do not write code.
```

### Prompt B

```text
日本語で回答してください。
Use the skill `plan-review` at `E:\codex\workspace\.agents\skills\plan-review\SKILL.md`.

Read `E:\codex\workspace\projects\workspace-operations\trial-fixtures\plan-review-safe-but-incomplete\plan.md`.
Review the plan before implementation and report risks and revisions only.
Do not write code.
```
