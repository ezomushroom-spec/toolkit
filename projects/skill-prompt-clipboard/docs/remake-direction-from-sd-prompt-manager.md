# SD Prompt Manager 参考再構築方針

## 1. 結論

- 既存 React app へ場当たり的に機能追加するより、`E:\自作アプリ集\新しいフォルダー (2)` を参考に、画像生成プロンプト管理ツールとして再構築する方が建設的。
- 参考元の Python GUI をそのまま移植するのではなく、実データ構造と運用機能を引き継ぎ、UI は今後の拡張に耐える形へ整理する。
- 現在の React 実装は「situation 管理 UI の試作」として扱い、次段階では保存、wildcard、negative prompt、検索を軸に設計し直す。

## 2. 実装前診断

### 2-1. 要求の整理

- 依頼の本質: 画像生成プロンプトを、場面、派生版、ワイルドカード、タグ検索まで含めて使いやすく管理したい。
- 技術的に重要な論点: 保存先、外部 wildcard 連携、タグ DB、検索 UI、削除や上書きの安全性。
- 既存資産の扱い: 参考元の SQLite schema、wildcard ファイル、タグ検索、prompt / negative prompt 分離は再利用価値が高い。
- 既存処理やデータへの影響: 外部 wildcard フォルダや SQLite を直接書き換えると復旧コストが高いため、初回は読み取り専用または app 内保存に閉じる。

### 2-2. 候補アプローチ

| 候補 | 概要 | 強み | 弱み | 適合度 |
| --- | --- | --- | --- | --- |
| A | 現 React app を少しずつ拡張 | すぐ触れる。UI 試作が早い | DB、wildcard、タグ検索が後付けになりやすい | 中 |
| B | 参考元 Python app を修理・整理 | SQLite と wildcard 処理をそのまま使える | UI 改善と保守性に限界が出やすい | 中 |
| C | 参考元を仕様正本にして React app を再構築 | UI を作り直しつつ、実データ構造を取り込める | 初期設計が必要 | 高 |

### 2-3. 推奨案

- 推奨する構成: 候補 C。React app をベースに、参考元のデータ構造と運用機能を段階的に取り込む。
- 推奨理由: プロンプト管理は UI の見通し、検索、編集、コピーの操作性が重要で、React の方が画面構成を整理しやすい。一方で、参考元の SQLite と wildcard 管理は実運用の知見として残す価値がある。
- 見送る候補: 候補 A は短期修正向きだが、保存やインポートが入ると責務が崩れやすい。候補 B は既存機能を残しやすいが、UI の使いやすさ改善が主目的なら再構築の利点が大きい。
- 主なリスク: 外部 wildcard を直接編集して破損させること、タグ DB 全件を frontend に載せて重くすること、旧 app の便利機能を落とすこと。
- 次点案: まず Python app 側を読み取り専用 API または変換スクリプトとして使い、React 側へ JSON で渡す方式。

## 3. 機能凍結表

| 機能 | 現行挙動 | 初回再構築での扱い | 理由 |
| --- | --- | --- | --- |
| prompt / negative prompt 分離 | Python app で別欄管理 | keep | 画像生成では重要度が高い |
| prompt 保存 | SQLite `prompts` テーブル | fix | DB には現時点で prompt 0 件なので、保存 UI は作り直せる |
| タグ DB | SQLite `tags` 約 14 万件 | later | 全件を UI に載せると重い。検索設計が必要 |
| wildcard txt 読み込み | `data/wildcards` の txt を読む | keep | 実データ資産として有用 |
| wildcard yaml 読み込み | 一部 yaml が存在 | later | 形式差分があるため初回は txt 優先 |
| wildcard 編集・削除 | Python app で可能 | later | 外部資産破損リスクが高い |
| wildcard ランダムプレビュー | Python app で可能 | fix | 便利だが、まず参照とコピーを優先 |
| タグサジェスト | Python app で可能 | later | 実装負荷が高く、まず検索導線で代替できる |
| クリップボードコピー | Python / React 双方にあり | keep | 主操作 |
| situation bundle | React 試作で導入 | keep | ユーザー要望の中心 |

## 4. 既知差分・既知不具合表

| 項目 | 現状 | 再構築方針 |
| --- | --- | --- |
| Python app の prompt DB | `prompts` は 0 件 | 既存 prompt の移行より、新しい保存構造を優先 |
| タグ DB | 大量データが SQLite にある | 検索 API / 変換 / indexedDB などを別途比較 |
| wildcard 設定 | 外部 SD WebUI extension のパスを指す | 直接上書きしない。初回は読み取り専用またはコピー取り込み |
| React app の保存 | なし | `localStorage` か JSON import から検討 |
| React app の negative prompt | なし | 次段階で追加 |
| React app の wildcard | 固定サンプル表示のみ | txt wildcard の取り込みを検討 |

## 5. 副作用 / 再実行 / 戻し方マトリクス

| 対象 | 副作用 | 再実行リスク | 戻し方 |
| --- | --- | --- | --- |
| React app 内固定データ | コード変更のみ | 低 | git / ファイル単位で戻す |
| `localStorage` 保存 | ブラウザ内データ更新 | 古い schema が残る | version 付き key にし、初期化導線を用意 |
| 外部 wildcard 読み取り | なし | 低 | 読み取りを止める |
| 外部 wildcard 書き込み | 実運用ファイル更新 | 高 | 事前バックアップ必須。初回では避ける |
| SQLite 読み取り | DB ファイル参照 | 低 | 読み取り専用接続にする |
| SQLite 書き込み | DB 更新 | 中から高 | バックアップ必須。初回では避ける |

## 6. 手動確認フロー / 終了責務整理表

| フロー | 確認すること | 終了条件 |
| --- | --- | --- |
| situation 選択 | 属性タブ、一覧、variant が連動する | 編集欄に正しい文面が出る |
| prompt / negative prompt 編集 | 別欄で管理できる | 個別コピーできる |
| wildcard 参照 | `__name__` と候補が見える | 構文をコピーできる |
| 保存 | 再読み込み後も残る | schema version が合う |
| インポート | 外部資産を壊さず読み込める | 読み取り件数とエラーが表示される |
| エラー | 読み込み失敗、コピー失敗が分かる | 次の行動が表示される |

## 7. keep / fix / later 判定表

| 判定 | 対象 |
| --- | --- |
| keep | situation bundle、variant 切り替え、コピー、prompt / negative prompt 分離、txt wildcard 参照 |
| fix | UI 構造、保存 schema、wildcard 表示、ランダムプレビューの位置づけ |
| later | タグ DB 全文検索、入力中サジェスト、SQLite 書き込み、外部 wildcard 編集、yaml wildcard 完全対応 |

## 8. 改訂実装計画

1. `ImagePromptSituation` に `negativePrompt`、`favorite`、`notes` を追加する。
2. `docs/ui-design-direction.md` の方針に沿って、画面を作業用スタジオ型に再整理する。
3. `localStorage` で situation / variant の保存を入れる。
4. txt wildcard を JSON へ変換する読み取り専用 importer を作る。
5. wildcard 一覧で `__name__` 構文コピー、候補数、候補プレビューを表示する。
6. タグ DB 検索は別フェーズで、SQLite 直接利用か変換済み軽量 index かを比較する。

## 9. 実装前に確認すべきこと

- 再構築先は現在の React app でよいか。
- 初回保存は `localStorage` でよいか、それとも JSON ファイル import / export を優先するか。
- 外部 wildcard は読み取り専用で始めてよいか。
- 成人向けや用途限定 wildcard を最初から表示対象に含めるか、除外・分類するか。
