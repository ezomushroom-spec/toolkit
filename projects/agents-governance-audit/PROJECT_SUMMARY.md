# Project Summary

## 1. Purpose

- workspace の `AGENTS.md`、skills、docs、入口文書の棚卸しや再編判断を記録する監査案件です。
- 実装コードではなく、現状確認、採用判断、未決事項の文書を残す用途です。

## 2. Source of Truth

- この folder の役割: 監査メモと再編判断の保管場所
- 正本コード: なし
- 正本設定: なし
- 正本データ: なし
- 正本文書: このフォルダ内の監査メモと方針文書
- 比較対象や参照専用 backup: workspace root の `AGENTS.md`、`.codex/`、`.agents/skills`、`docs/`、`projects/`

## 3. Primary Entry Points

- 通常起動: なし
- 代替入口: なし
- ビルドや検証の主要コマンド: 実ファイル構成と文書の突き合わせ

## 4. Safe Read Scope

- 初見で読んでよいディレクトリ: この project 配下の監査メモ、workspace root の `AGENTS.md`、`docs/`、`.agents/skills`
- 先に確認すべき文書: `START_HERE.md`, `agents-md-inventory_20260329.md`, `workspace-reorg-principles_20260331.md`

## 5. Do Not Edit Without Explicit Request

- backup: 該当なし
- profile / user data: 該当なし
- build artifact / generated: 該当なし
- secrets / local state: 実 project 側の設定や運用資産

## 6. Related Boundaries

- workspace root rules: `E:\codex\workspace\AGENTS.md`
- workspace docs: `E:\codex\workspace\docs`
- workspace skills: `E:\codex\workspace\.agents\skills`, `C:\Users\ezomu\.codex\skills`
- project entry docs: `E:\codex\workspace\projects\*`

## 7. Risks For Subagents

- 誤認しやすい正本や境界: 監査メモと実 project の正本コードを混同しないこと
- 壊しやすい運用資産: 他 project の設定、データ、生成物
- 並列編集で衝突しやすい場所: workspace root の `AGENTS.md`、`docs/`、各 project の入口文書

## 8. Recommended First Step

- まず `START_HERE.md` と既存監査メモを読んで、すでに固定済みの判断を再調査しない。
- 次に workspace 実ファイルを見て、文書との差だけを追加で整理する。

## 9. Rollback Hint

- この project は文書中心なので、変更はファイル単位で戻せる。
- 実 project 側の実装や運用資産とは分離して扱う。
