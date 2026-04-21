# empirical-prompt-tuning 採用判断

## 1. 何を決める文書か

- `empirical-prompt-tuning` を workspace にどう導入するかを決める
- 既存 skill 群を一律置換するか、評価プロトコルとして併設するかを固定する

## 2. 候補比較

### 候補 A: 上位規約として全面正規化する

- 概要: 既存 skill を同じ構造や文体へ寄せながら改訂する
- 要件適合性: 低い
- 実装の確実性: 低い
- 保守性 / 拡張性: 中
- UI / 運用面の評価: 低い
- 既存資産の再利用: 低い
- 主な弱点:
  - 既存 skill の専門性を壊しやすい
  - 実績のある workflow まで巻き込んでしまう
  - 文体統一が目的化しやすい

### 候補 B: 評価・改訂プロトコルとして併設する

- 概要: 既存 skill / 入口文書を対象に、静的レビューと empirical evaluation の手順を追加する
- 要件適合性: 高い
- 実装の確実性: 高い
- 保守性 / 拡張性: 高い
- UI / 運用面の評価: 高い
- 既存資産の再利用: 高い
- 主な弱点:
  - すぐには全体品質が上がらず、優先順位付けが必要
  - empirical evaluation には fresh executor と記録運用が必要

## 3. 採用判断

- 採用案: 候補 B
- 採用理由:
  - workspace の既存 skill 群はすでに役割分担があり、全面テンプレ化よりも品質保証レイヤーの追加が合う
  - 問題は主に trigger の曖昧さ、古い参照、done criteria の弱さであり、専門性そのものではない
  - `Critical` から段階導入でき、運用コストを制御しやすい
- 見送る案と理由:
  - 候補 A は uniformity を得やすいが、既存資産の価値を削りやすく、今回の目的に対して過剰

## 4. keep / fix / 後送り

### keep

- 既存 skill の目的と専門領域
- 既存の入口文書と段階的な使い分け
- 特化 skill を無理に一般化しない方針

### fix

- `description` と body の乖離
- trigger と適用条件の曖昧さ
- done criteria や output contract の不足
- 古い skill 名や古い参照の残存

### 今回やらないもの

- 全 skill の一括 empirical evaluation
- 文体や章立ての機械的統一
- 一回限りの軽い prompt まで含めた全面評価

## 5. 実装前に守る運用ルール

- empirical evaluation は fresh executor があるときだけ実施する
- dispatch 不可または未許可の環境では「静的レビューのみ」と明記する
- 改訂は `1 iteration = 1 theme` を守る
- success rate や tool count だけで打ち切らない

## 6. 次の一手

1. `empirical-prompt-tuning` skill を workspace skill として追加する
2. `Critical` 3 件の scenario / checklist / result template を固定する
3. 委任許可がある回で empirical evaluation を実施する
