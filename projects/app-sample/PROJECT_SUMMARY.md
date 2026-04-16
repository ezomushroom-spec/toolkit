# Project Summary

## 1. Purpose

- React、TypeScript、Vite、Vitest を前提にした小規模 Web UI サンプルです。
- 主操作、危険操作、エラー表示の基本パターンを安全に試すための雛形として扱います。

## 2. Source of Truth

- 正本コード: `src/`
- 正本文書: `AGENTS.md`, `PROJECT_SUMMARY.md`, `docs/`
- 正本テスト: `tests/`
- 正本設定: project 直下の Vite / TypeScript / test 関連設定

## 3. Primary Entry Points

- 通常起動: Vite 開発サーバー
- 代替入口: テスト実行
- ビルドや検証の主要コマンド: `npm run dev`, `npm run test`

## 4. Safe Read Scope

- 初見で読んでよいディレクトリ: `src/`, `tests/`, `docs/`
- 先に確認すべき文書: `AGENTS.md`

## 5. Do Not Edit Without Explicit Request

- backup: 現時点で project 直下には見当たらない
- profile / user data: 特になし
- build artifact / generated: 明示依頼なしで生成物を追加しない
- secrets / local state: 特になし

## 6. Related Boundaries

- UI: `src/`
- backend / business logic: frontend 内ローカルロジックのみ
- desktop shell / launcher: なし
- external integration: 特になし

## 7. Risks for Subagents

- 誤認しやすい正本: 小規模なため少ないが、実装方針は `AGENTS.md` を優先する
- 壊しやすい運用資産: 特になし
- 並列編集で衝突しやすい場所: `src/` の主要画面ファイル

## 8. Recommended First Step

- まず `AGENTS.md` を読んで UI 前提と確認観点を把握する。
- 次に `src/` と `tests/` を見て、主操作と危険操作の扱いを揃える。

## 9. Rollback Hint

- 変更は基本的に `src/` と `tests/` の単位で戻す。
- project 固有ルールに関わる変更は `AGENTS.md` と合わせて確認する。
