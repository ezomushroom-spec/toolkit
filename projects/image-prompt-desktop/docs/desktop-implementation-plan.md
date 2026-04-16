# デスクトップ版 実装計画

## 1. 対象

- 新規 project: `E:\codex\workspace\projects\image-prompt-desktop`
- 正本: `E:\自作アプリ集\新しいフォルダー (2)`
- UI: PySide6
- 初回接続: 正本 SQLite と `data\wildcards` の読み取り

## 2. 実装順

1. `main.py`、`requirements.txt`、launcher bat を作る。
2. `core.py` に正本 path、prompt / tag 件数、prompt 一覧、txt wildcard 読み取りを実装する。
3. `main_window.py` に 3 ペイン UI を作る。
4. prompt / negative prompt / wildcard token のコピーを実装する。
5. 空データと読み取り失敗を status / dialog で表示する。
6. unittest で wildcard 解析を確認する。
7. 正本 tags を読み取り専用で検索し、選択タグを prompt / negative prompt へ挿入する。
8. wildcard ランダム候補確認とタグカテゴリ絞り込みを追加する。
9. 作業中 prompt / negative prompt を desktop 版ローカル session JSON に一時保存する。
10. タグ検索結果と wildcard 候補のダブルクリック挿入、ランダム候補のコピー / 挿入を追加する。
11. 生成シチュエーション名、登録タグ、使用 wildcard、メモを Situation Draft として desktop 版ローカル JSON に保存する。
12. Prompt 編集画面から wildcard 領域を分離し、上位タブ `Prompt Studio` / `Wildcard Library` に整理する。
13. 正本 wildcard を直接編集せず、desktop 版ローカル wildcard 下書きとして編集・保存・削除できるようにする。

## 3. 確認点

- 正本 DB を読み取り専用 `mode=ro` で開く。
- 正本 wildcard は `read_text` のみで読み、書き込まない。
- タグ検索は `mode=ro` の SQL SELECT のみにする。
- wildcard ランダム確認は正本 txt を読むだけにし、候補ファイルへ書き込まない。
- ダブルクリック挿入は UI 編集欄だけに反映し、正本 DB / wildcard へ書き込まない。
- session JSON は `image-prompt-desktop\data\session.json` に限定し、正本 `data` へ書き込まない。
- Situation Draft JSON は `image-prompt-desktop\data\situations.json` に限定し、正本 `data` へ書き込まない。
- `Prompt Studio` にはタグ検索だけを残し、wildcard の参照・候補操作は `Wildcard Library` に分離する。
- 画像プレビュー用途の表示欄は作らず、wildcard 候補はリストで扱う。
- Wildcard 下書き JSON は `image-prompt-desktop\data\wildcard_drafts.json` に限定し、正本 wildcard ファイルへ書き込まない。
- `python -m unittest discover -s tests` が通る。
- PySide6 が入っている環境では `python main.py` で起動できる。
- launcher は作業ディレクトリを project root に固定する。

## 4. 戻し方

- 正本には書き込まないため、戻しは `image-prompt-desktop` 側の差分を破棄する。
- 後続で保存や削除を入れる場合は、実装前に正本 `data` のバックアップと復元手順を追加する。
