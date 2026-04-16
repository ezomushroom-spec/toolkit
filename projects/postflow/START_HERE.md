# START HERE

## この project は何か

- `PostFlow` は、画像投稿の前工程を整理するローカルデスクトップアプリです。
- 作品単位で画像を管理し、投稿順、先頭画像、投稿先ごとの進行状態、投稿前確認を扱います。

## 最初に読む順番

1. `AGENTS.md`
2. `PROJECT_SUMMARY.md`
3. `docs/current-state-check.md`
4. `docs/implementation-plan.md`
5. `docs/pre-implementation-decision.md`

## 正本

- 正本コード: `projects/postflow/app/`
- 正本設定: `projects/postflow/app/postflow/config.py`
- 正本文書: `projects/postflow/docs/`
- 正本未確定の候補: なし

## 主要入口

- 通常起動: `start.bat`
- 直接起動: `python app/app.py`
- デバッグ起動: `debug-start.bat`
- 代替入口: なし
- 主な確認方法: アプリ起動、DB 初期化、作品作成、画像追加、並び替え、先頭画像設定、投稿先状態更新、再起動後保持

## 触る前に注意するもの

- 壊してはいけない既存挙動: 作品作成、画像追加、並び替え、先頭画像設定、投稿先状態更新、投稿前確認
- 明示依頼なしで触らないもの: `archive/`, `build`, `dist`, `*_profile`, `src_backup_*`
- backup / profile / generated: workspace 共通ルールに従い編集しない

## 最初の一手

- まず `docs/current-state-check.md` で Step 5 までの現在地を確認する。
- 次に `docs/implementation-plan.md` を見て、残っている Step 6 の異常系、安全性、見た目補強の範囲を固定する。
