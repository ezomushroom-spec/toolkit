# empirical-prompt-tuning Opportunistic rollout

## 1. 目的

`Critical` と `Important` の初回 trial 完了後に、workspace skill のうち低頻度または限定用途だが、改訂時に empirical review をかける価値がある対象を固定する。

## 2. 対象分類

### Opportunistic

1. `plan-review`
2. `ui-overlap-guard`
3. `image-finishing-tool-design`
4. `empirical-prompt-tuning`

### 初回 rollout 済み

- `request-translate`
- `pre-implementation-diagnosis`
- `implementation-planner`
- `code-review`
- `subagent-debug-review`
- `project-safety-snapshot`
- `project-scaffolder`
- `windows-batch-launcher`
- `ui-audit`
- `ui-design-direction`
- `ui-remake-safe`
- `desktop-dnd-path-resolution`

## 3. Opportunistic に置く理由

### 1. `plan-review`

- 価値は高いが、毎回必ず呼ばれる入口ではない
- remake / refactor 計画が立ったときにだけ scenario を作れば十分

### 2. `ui-overlap-guard`

- UI 事故防止には有用だが、重なりや scroll 干渉が論点のときだけ使う
- 単独 trial より、実際の layout 修正や `ui-remake-safe` 改訂時の再評価が向く

### 3. `image-finishing-tool-design`

- 明確に domain-specific で、一般導線より project 文脈依存が強い
- 画像仕上げ系案件が動いた時点で scenario を作る方が現実的

### 4. `empirical-prompt-tuning`

- protocol skill 自身なので、頻繁な forward run より節目での自己点検が向く
- 新しい artifact type や result 運用が増えた時点で 2nd pass を考える

## 4. 実施順

1. `plan-review`
2. `ui-overlap-guard`
3. `image-finishing-tool-design`
4. `empirical-prompt-tuning`

## 4.1 現在地

- `plan-review` の trial は完了
- `ui-overlap-guard` の trial は完了
- `image-finishing-tool-design` の trial は完了
- `empirical-prompt-tuning` の trial は完了
- `Opportunistic` 群の初回横展開は完了

## 5. 発火条件

- `plan-review`: 大きめの remake / migration plan が実際に出たとき
- `ui-overlap-guard`: overlap, crushed control, scroll collision を伴う UI 修正が入ったとき
- `image-finishing-tool-design`: 画像仕上げツールの新規設計や再構築案件が出たとき
- `empirical-prompt-tuning`: artifact type 拡張、記録方式変更、または評価運用の常用化を決めるとき

## 6. 運用メモ

- `Opportunistic` は今すぐ全件 trial しない
- 新規改訂や実案件トリガーが発生した時だけ scenario を切る
- 結果は `Critical` / `Important` と同じ result log 形式で残す
