# empirical-prompt-tuning trial result

## Target

- Target: `plan-review`
- Canonical file: `E:\codex\workspace\.agents\skills\plan-review\SKILL.md`
- Evaluation date: 2026-04-22
- Executor separation: empirical

## Scenario A: broad remake plan

- Request summary: 広すぎる remake plan を実装前に厳しめレビューする
- Fixture path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\plan-review-broad-remake`
- Success: ○
- Failed `[critical]` items: なし
- Precision: 4 / 4 = 100%
- Tool usage: 利用メタデータはこの subagent surface では取得できず未記録
- Duration: 利用メタデータはこの subagent surface では取得できず未記録
- Retry count: 自己申告なし

Checklist review:

- [critical] scope too broad なら `split into phases first` が出る: ○
- 挙動保全や戻し方の弱さを拾う: ○
- 5 観点に沿ってレビューする: ○
- severity を伴って具体的に指摘する: ○

Observed ambiguity:

- なし

Discretion completion by executor:

- `UI 再構成` `内部処理と互換` `旧 UI 撤去` の 3 段階へ自然に分割提案した

Next revision theme:

- 目立った failure はなく、必須改訂なし

## Scenario B: safe but incomplete plan

- Request summary: 小さく安全寄りだが条件不足の UI 改善 plan を実装前レビューする
- Fixture path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\plan-review-safe-but-incomplete`
- Success: ○
- Failed `[critical]` items: なし
- Precision: 4 / 4 = 100%
- Tool usage: 利用メタデータはこの subagent surface では取得できず未記録
- Duration: 利用メタデータはこの subagent surface では取得できず未記録
- Retry count: 自己申告なし

Checklist review:

- [critical] vague な安心判定で流さない: ○
- missing conditions を拾う: ○
- 過剰に `split into phases first` へ寄せない: ○
- `revise first` か `ready to implement` を根拠つきで出す: ○

Observed ambiguity:

- 小さめ plan でも `revise first` を選ぶ閾値は plan 入力の粗さに依存するが、今回は理由づけが十分具体的だった

Discretion completion by executor:

- `危険操作` 定義、loading 中再実行境界、失敗分岐、回帰確認の不足を主要 missing conditions として整理した

Next revision theme:

- 目立った failure はなく、必須改訂なし

## Overall result

- broad plan と safe-but-incomplete plan の両方で厳しめの判定が安定して出た
- `split into phases first` と `revise first` の使い分けも自然
- 初回 `Opportunistic` 対象として通過してよい
