# empirical-prompt-tuning Important rollout

## 1. 目的

初回 5 件の trial 完了後に、`Important` 判定の workspace skill をどの順で広げるかを固定する。

## 2. 次の対象順

1. `implementation-planner`
2. `pre-implementation-diagnosis`
3. `code-review`
4. `ui-audit`
5. `ui-design-direction`
6. `ui-remake-safe`
7. `desktop-dnd-path-resolution`

## 3. この順にする理由

### 1. `implementation-planner`

- 実装順、戻し方、確認点の質に直結する
- scenario 化しやすく、結果も比較しやすい

### 2. `pre-implementation-diagnosis`

- 実装前判断の質に影響が大きい
- `比較してから実装する` という workspace 原則との整合を見やすい

### 3. `code-review`

- 頻度が高い
- findings の質と優先度付けを評価しやすい

### 4-7. UI / D&D 系

- 価値は高いが、fixture や評価観点がやや重い
- 前段の planning / review 系より後回しでよい

## 4. 実施単位

- 1 回に 1 skill
- 1 skill につき 2 scenario を基本
- `[critical]` 失敗が出ない限り、横に広げる

## 5. 現在地

- `implementation-planner` の trial は完了
- `pre-implementation-diagnosis` の trial は完了
- `code-review` の trial は完了
- `ui-audit` の trial は完了
- `ui-design-direction` の trial は完了
- `ui-remake-safe` の trial は完了
- `desktop-dnd-path-resolution` の trial は完了
- この順で並べた `Important` 群の初回横展開は完了
- 次に進めるなら `Opportunistic` 群への展開か、既存 result の 2nd iteration 候補選定
