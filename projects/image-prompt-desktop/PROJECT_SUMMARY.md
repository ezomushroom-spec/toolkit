# Project Summary

## 1. Purpose

- 正本 `E:\自作アプリ集\新しいフォルダー (2)` の画像生成プロンプト管理機能を、PySide6 の Windows デスクトップアプリとして再構築する。
- 初回は正本 DB / wildcard を読み取り、prompt / negative prompt / wildcard token のコピー導線を作る。

## 2. Source of Truth

- 現行挙動とデータ構造の正本: `E:\自作アプリ集\新しいフォルダー (2)`
- デスクトップ再構築先: `E:\codex\workspace\projects\image-prompt-desktop`
- 正本 DB: `E:\自作アプリ集\新しいフォルダー (2)\data\prompts.db`
- 正本 wildcard: `E:\自作アプリ集\新しいフォルダー (2)\data\wildcards`

## 3. Entry Points

- source run: `python main.py`
- launcher: `start.bat`
- debug launcher: `debug-start.bat`
- tests: `python -m unittest discover -s tests`

## 4. Current Scope

- PySide6 3 ペイン UI
- 上位タブ `Prompt Studio` / `Wildcard Library`
- 正本 SQLite 読み取り専用接続
- 正本 txt wildcard 読み取り
- prompt / negative prompt / wildcard token のコピー
- wildcard token の prompt への挿入
- wildcard ランダム候補確認
- wildcard 候補行のダブルクリック挿入
- desktop 版ローカル `data/wildcard_drafts.json` への wildcard 下書き編集
- ランダム候補のコピー / Prompt 挿入
- 正本 tags の読み取り専用検索
- タグカテゴリ絞り込み
- 選択タグの prompt / negative prompt への挿入
- タグ検索結果のダブルクリック挿入
- desktop 版ローカル `data/session.json` への作業中 prompt 一時保存
- desktop 版ローカル `data/situations.json` への Situation Draft 保存
- 保存済み Situation の読み込みと新規 Situation 化
- status bar と読み込み失敗 dialog

## 5. Out of Scope

- 正本 DB 書き込み
- wildcard 作成、削除、リネーム、保存
- 正本 wildcard の直接編集保存
- 外部 SD WebUI wildcard フォルダへの書き込み
- PyInstaller packaging
- タグ DB の高度な全文検索、サジェスト、カテゴリ別フィルタ

## 6. Rollback

- 正本には書き込まないため、戻しは `image-prompt-desktop` 側の差分破棄で済む。
- 作業中 prompt の一時保存だけを消す場合は `data/session.json` を削除する。
- Situation Draft だけを消す場合は `data/situations.json` を削除する。
- 後続で書き込み機能を入れる前に、正本 `data` のバックアップと復元手順を追加する。
