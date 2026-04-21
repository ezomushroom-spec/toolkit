# empirical-prompt-tuning 初回 trial 準備

## 1. 対象

- Target: `implementation-planner`
- Canonical file: `E:\codex\workspace\.agents\skills\implementation-planner\SKILL.md`
- Priority: `Important`

## 2. この対象を選ぶ理由

- 実装順、戻し方、確認点の質に直結する
- plan 品質は比較しやすく、fixture 化も軽い
- `Important` 群の先頭として妥当

## 3. trial fixture

### Fixture A: multi-file safe change

- Path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\implementation-planner-multi`
- 想定: 複数ファイル変更が必要だが、段階分けしやすい UI 改善案件

### Fixture B: small patch

- Path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\implementation-planner-small`
- 想定: 小規模修正で、過剰な計画に広げないかを見る

## 4. 固定 scenario

### Scenario A: 中規模改修計画

- Case type: `median`
- User-like request:

```text
既存挙動を壊さずに、一覧画面のフィルタ領域整理、保存エラー表示の改善、確認手順まで含めて実装計画を作ってください。
```

Checklist:

- [critical] 変更順と戻し方が入る
- target files / impact areas が出る
- 確認点が正常系だけで終わらない
- scope を広げすぎない

### Scenario B: 小規模修正

- Case type: `edge`
- User-like request:

```text
ボタン文言の修正だけしたいです。必要なら最小限の実装計画をください。
```

Checklist:

- [critical] 小規模修正として過剰に膨らませない
- 必要最小限の計画にとどめる
- 確認方法は残す

## 5. fresh executor へ渡す prompt ひな形

### Prompt A

```text
Use the skill `implementation-planner` at `E:\codex\workspace\.agents\skills\implementation-planner` for this task.

Work from the artifacts inside `E:\codex\workspace\projects\workspace-operations\trial-fixtures\implementation-planner-multi`.
Create a safe implementation plan without writing code.
```

### Prompt B

```text
Use the skill `implementation-planner` at `E:\codex\workspace\.agents\skills\implementation-planner` for this task.

Work from the artifacts inside `E:\codex\workspace\projects\workspace-operations\trial-fixtures\implementation-planner-small`.
Create only the minimum implementation plan needed, without writing code.
```
