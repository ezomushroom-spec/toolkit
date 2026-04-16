# Docs 更新ルール

この文書は、workspace 内で「どんな変更のときに、どの文書を更新するか」を揃えるための共通ルール。
実装だけ先に進み、入口文書や判断メモが古くなる状態を減らすことを目的とする。

## 1. 基本方針

- docs 更新は実装の後工程ではなく、変更の一部として扱う
- 実コード、実データ、現用設定とズレる文書は正本扱いしない
- 変更の規模に応じて、更新対象を必要最小限に絞る
- project 固有の更新先は `projects/<name>/AGENTS.md` に寄せて明示してよい

## 2. 文書の役割

### root `AGENTS.md`

- workspace 共通ルール
- active / backup / archive の境界
- 実装前診断、進行フロー、サブエージェント利用条件

### `projects/<name>/AGENTS.md`

- project 固有の制約
- build / run / test の入口
- 壊してはいけない挙動
- 変更時の必須セット作業

### `projects/<name>/START_HERE.md`

- 初見の読み順
- 正本境界
- 触る前に注意するもの

### `projects/<name>/PROJECT_SUMMARY.md`

- project の要約
- 正本コード / 設定 / データ / 文書
- 主な入口
- 危険領域と rollback の見通し

### `projects/<name>/docs/*.md`

- 現状確認
- 採用判断
- 実装計画
- 引き継ぎ
- 未決事項

### docs-only / audit-only project の例外

- 実装コードを持たない project では、監査メモや判断文書を project 直下に置いてよい
- その場合でも `AGENTS.md`、`START_HERE.md`、`PROJECT_SUMMARY.md` から読む順番と正本文書を明示する

## 3. 更新が必要な代表ケース

### A. 正本や境界が変わるとき

更新候補:

- root `AGENTS.md` または関連 root docs
- project `AGENTS.md`
- `START_HERE.md`
- `PROJECT_SUMMARY.md`
- 必要なら境界判断メモ

例:

- active / backup / archive の移動
- 正本コードや正本文書の変更
- shell と backend の責務変更

### B. build / run / test 手順が変わるとき

更新候補:

- project `AGENTS.md`
- `PROJECT_SUMMARY.md`
- 必要なら `README.md`

例:

- 起動バッチの変更
- 新しい確認コマンド追加
- 依存導入手順の変更

### C. UI の主操作や危険操作が変わるとき

更新候補:

- project `AGENTS.md`
- `START_HERE.md`
- 必要なら案件 docs

例:

- 主操作ボタンの意味変更
- 停止、削除、送信の導線変更
- エラー表示や二重実行防止の挙動変更

### D. 実装計画や現在地が変わるとき

更新候補:

- `projects/<name>/docs/implementation-plan.md`
- 現状確認メモ
- 採用判断メモ
- `START_HERE.md` や `PROJECT_SUMMARY.md` の読み順

例:

- Phase の現在地変更
- 主要未決事項の解消
- 次の主対象の変更

### E. template や scaffolder の元が変わるとき

更新候補:

- `docs/templates/*`
- `project-scaffolder` の script や skill 本文
- `docs/README.md`
- 必要なら `workspace-template/` 側の対応文書

例:

- project 雛形の見出しや項目変更
- scaffold 時に作るファイルの追加や削除
- template 側の役割や読み順変更

## 4. 小規模変更で更新を省略してよい条件

次をすべて満たすなら、docs 更新を省略してよい。

- 既存構成内の局所修正
- 正本境界が変わらない
- build / run / test 手順が変わらない
- 主操作や危険操作の意味が変わらない
- 既存 docs の記述を誤りにしない

ただし、既存 docs を読み手が誤解するなら小規模でも更新する。

## 5. 変更時の最小確認

docs を更新したら、少なくとも次を確認する。

- 読み順が崩れていないか
- 正本コード / 設定 / データ / 文書の表現がズレていないか
- backup や生成物を active 扱いしていないか
- 実行コマンドや入口が古くなっていないか
- `docs/templates/*` を変えた場合、scaffolder の生成対象と食い違っていないか

## 6. project `AGENTS.md` に書くと強いもの

各 project では、次を「変更時の必須セット作業」として明記すると運用が安定する。

- 更新すべき docs
- 最低限の確認コマンド
- 最低限の手動確認
- 失敗時に先に見るログやファイル

## 7. 今回時点の結論

- workspace の入口文書はかなり揃ってきた
- 次の改善は、文書の枚数を増やすことより「どの変更で何を更新するか」を固定することが重要
- 以後の project 改修では、この文書を docs 更新要否の判定基準として使う

## 8. 参考入口

- docs 全体の入口は [README.md](/E:/codex/workspace/docs/README.md)
- 実装前判断メモの型は [templates/pre-implementation-decision.template.md](/E:/codex/workspace/docs/templates/pre-implementation-decision.template.md)
- 現状確認メモの型は [templates/current-state-check.template.md](/E:/codex/workspace/docs/templates/current-state-check.template.md)
