# Project Summary

## 1. Purpose

- 画像生成用プロンプトを situation 単位で束ね、属性タブから選んで prompt / negative prompt を編集・保存・コピーできるローカル Web アプリです。
- 正本 Python app の `data/wildcards` から、確認済み txt wildcard を読み取り専用で取り込み、React 側で `__name__` 構文と候補プレビューを表示します。
- React + TypeScript + Vite で構成された小規模ツールです。

## 2. Source of Truth

- 現行挙動とデータ構造の正本: `E:\自作アプリ集\新しいフォルダー (2)`
- React 版の実装先: `src/`
- 移行判断と計画の正本: `AGENTS.md`, `README.md`, `docs/`
- 正本設定: `package.json`, `vite.config.ts`, `tsconfig*.json`

## 3. Primary Entry Points

- 通常起動: `npm run dev`
- 代替入口: `start.bat`, `debug-start.bat`
- ビルドや検証の主要コマンド: `npm run import:wildcards`, `npm run build`, `npm run lint`, `npm run test`

## 4. Safe Read Scope

- 初見で読んでよいディレクトリ: `src/`, `public/`, `docs/`
- 正本確認で読む場所: `E:\自作アプリ集\新しいフォルダー (2)\src\models\database.py`, `E:\自作アプリ集\新しいフォルダー (2)\src\models\wildcard_manager.py`, `E:\自作アプリ集\新しいフォルダー (2)\src\ui\tabs`
- 先に確認すべき文書: `AGENTS.md`, `README.md`, `docs/remake-direction-from-sd-prompt-manager.md`, `docs/reference-sd-prompt-manager-findings.md`, `package.json`

## 5. Do Not Edit Without Explicit Request

- backup: project 直下には見当たらない
- reference canonical app: `E:\自作アプリ集\新しいフォルダー (2)` は明示依頼なしで編集しない
- profile / user data: 特になし
- build artifact / generated: `dist/`, `node_modules/`, `build*.log`, `startup.log`, `dev-server.log`
- secrets / local state: 特になし

## 6. Related Boundaries

- UI: `src/`
- backend / business logic: なし
- desktop shell / launcher: `.bat` 起動導線
- external integration: クリップボード操作
- external read-only source: `E:\自作アプリ集\新しいフォルダー (2)\data\wildcards` から許可リスト化した txt wildcard を importer で取り込む。
- local persistence: React 版は `localStorage` に version 付き schema で保存。正本の保存構造は Python app の SQLite / wildcard ファイル。

## 7. Risks for Subagents

- 誤認しやすい正本: `dist/` を正本と誤認しやすい
- 壊しやすい運用資産: 特になし
- 並列編集で衝突しやすい場所: `src/App.tsx` と `src/App.css`

## 8. Recommended First Step

- まず `AGENTS.md` を読んで、主操作と build 生成物の境界を確認する。
- 次に `README.md` と `docs/image-prompt-situation-manager-spec.md` を読んで、画像生成プロンプト管理の仕様を把握する。
- 次に `src/App.tsx` と `src/App.test.tsx` を見て、表示ロジックとテストの対応を確認する。

## 9. Rollback Hint

- 変更は `src/`、`docs/`、`package.json` の単位で戻す。
- wildcard 取り込みだけを戻す場合は `scripts/import-canonical-wildcards.mjs`、`src/generated/canonicalWildcards.ts`、`src/App.tsx` の wildcard 表示差分を戻す。
- `dist/` やログは再生成物として扱い、コード変更と分けて確認する。
