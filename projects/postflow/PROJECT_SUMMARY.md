# Project Summary

## 1. Purpose

- `PostFlow` は、画像投稿の前工程専用のローカルデスクトップアプリです。
- 主な利用者は、少人数の限られた範囲でローカル画像の投稿準備を行う利用者です。
- 投稿本文、タグ、説明文は他アプリが担い、本 project では扱いません。

## 2. Source of Truth

- この folder の役割: `PostFlow` のコード、runtime、判断文書をまとめて置く
- 正本コード: `projects/postflow/app/`
- 正本設定: `projects/postflow/app/postflow/config.py`
- 正本データ: `projects/postflow/runtime/postflow.db`
- 正本文書: `projects/postflow/docs/`
- 比較対象や参照専用 backup: なし

## 3. Primary Entry Points

- 通常起動: `start.bat`
- 直接起動: `python app/app.py`
- デバッグ起動: `debug-start.bat`
- 代替入口: なし
- ビルドや検証の主要コマンド:
  - 起動: `start.bat`
  - 直接起動: `python app/app.py`
  - 構文確認: `python -m py_compile ...`

## 4. Safe Read Scope

- 初見で読んでよいディレクトリ: `projects/postflow/`, `projects/postflow/docs/`
- 先に確認すべき文書: `START_HERE.md`, `AGENTS.md`, `docs/pre-implementation-decision.md`, `docs/implementation-plan.md`

## 5. Do Not Edit Without Explicit Request

- backup: `archive/`
- profile / user data: `*_profile`
- build artifact / generated: `build/`, `dist/`
- secrets / local state: 実装後に定義

## 6. Related Boundaries

- UI: PySide6 で作品一覧、画像準備、投稿確認の 3 画面を構成する
- backend / business logic: Python の service / repository 層
- shell / launcher: `start.bat`, `debug-start.bat`
- 外部連携や運用境界: 投稿作業そのものは外部アプリやブラウザ側で手動実施

## 7. Risks For Subagents

- 誤認しやすい正本や境界: 正本コードは `app/`、正本データは `runtime/`、判断文書は `docs/`
- 壊しやすい運用資産: 元画像ファイルを触らない方針
- 並列編集で衝突しやすい場所: 実装開始後の UI 画面と DB スキーマ

## 8. Recommended First Step

- まず `docs/current-state-check.md` で Step 5 までの現在地を確認する。
- 次に `docs/implementation-plan.md` を見て、残っている Step 6 の補強項目から着手する。

## 9. Rollback Hint

- 実装はアプリ土台、DB、Repository、Service、画面の順で区切り、各段階で戻せるようにします。
- 元画像ファイルは編集しないため、失敗時も運用資産への影響は閉じ込められます。
