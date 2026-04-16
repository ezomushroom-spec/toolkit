# デスクトップ版 仕様

## 1. 目的

- 画像生成用プロンプト管理を、Web アプリではなく Windows デスクトップアプリとして扱う。
- 正本 Python app のデータ資産を壊さず、prompt / negative prompt / wildcard を素早く参照・コピーできる作業画面を作る。

## 2. 正本

- 正本 app: `E:\自作アプリ集\新しいフォルダー (2)`
- DB: `data\prompts.db`
- wildcard: `data\wildcards`
- 初回は読み取り専用。保存や削除は仕様対象外。

## 3. 画面

- 上位タブ: `Prompt Studio` と `Wildcard Library` に分ける。
- `Prompt Studio`: 左に保存済み prompt / Situation 一覧、中央に prompt / negative prompt の編集欄とコピー操作、右にタグ検索とカテゴリ絞り込みを置く。
- `Wildcard Library`: wildcard 一覧、候補リスト、ローカル下書き編集欄、候補行ダブルクリック挿入、ランダム候補確認、ランダム候補コピー、`__name__` 構文コピー、prompt への挿入を置く。
- 画像プレビュー用の表示欄は置かない。文字列候補はリストとして扱う。
- 下: status bar。コピー成功、空入力、読み込み結果を表示する。

## 4. 操作

- Prompt をコピーできる。
- Negative prompt をコピーできる。
- Wildcard token をコピーできる。
- Wildcard token を prompt 編集欄へ挿入できる。
- Wildcard 候補をランダム表示できる。
- `Wildcard Library` の候補行をダブルクリックして prompt へ挿入できる。
- ランダム表示した wildcard 候補をコピーまたは prompt へ挿入できる。
- 正本 wildcard を直接編集せず、desktop 版ローカル `data/wildcard_drafts.json` に wildcard 下書きを保存できる。
- ローカル下書きは削除でき、正本候補表示へ戻せる。
- タグを検索できる。
- タグ検索をカテゴリで絞り込める。
- 選択タグを prompt または negative prompt へ挿入できる。
- タグ検索結果をダブルクリックして選択中の挿入先へ挿入できる。
- 作業中の prompt / negative prompt を desktop 版ローカル `data/session.json` に一時保存できる。
- 保存済み作業は起動時に編集欄へ復元できる。
- 生成シチュエーション名、登録タグ、使用 wildcard、メモを Situation Draft として desktop 版ローカル `data/situations.json` に保存できる。
- 保存済み Situation Draft を左リストから読み込める。
- 読み込み済み Situation から現在の prompt / negative prompt を残したまま新規 Situation 化できる。
- 正本データを再読み込みできる。

## 5. 安全性

- SQLite は `mode=ro` で開く。
- wildcard は `read_text` のみで読む。
- タグ検索も `mode=ro` の SQLite 読み取りだけで行う。
- 一時保存は desktop 版ローカル `data/session.json` だけへ書き込み、正本 DB には書き込まない。
- Situation Draft は desktop 版ローカル `data/situations.json` だけへ書き込み、正本 DB には書き込まない。
- Wildcard 下書きは desktop 版ローカル `data/wildcard_drafts.json` だけへ書き込み、正本 wildcard ファイルには書き込まない。
- 正本 DB / wildcard への書き込み操作は初回実装に含めない。
- Wildcard は専用タブへ分離するが、初回は読み取り、コピー、挿入までに留め、正本 wildcard の編集保存は入れない。
- 読み込み失敗時は dialog と status bar で知らせる。
