# Project Summary

## 1. Purpose

- 画像生成用プロンプトを situation 単位で束ね、属性タブから選んでコピーできるローカル Web アプリです。
- React + TypeScript + Vite で構成された小規模ツールです。

## 2. Source of Truth

- 正本コード: `src/`
- 正本文書: `AGENTS.md`, `README.md`, `docs/`
- 正本設定: `package.json`, `vite.config.ts`, `tsconfig*.json`

## 3. Primary Entry Points

- 通常起動: `npm run dev`
- 代替入口: `start.bat`, `debug-start.bat`
- ビルドや検証の主要コマンド: `npm run build`, `npm run lint`, `npm run test`

## 4. Safe Read Scope

- 初見で読んでよいディレクトリ: `src/`, `public/`, `docs/`
- 先に確認すべき文書: `AGENTS.md`, `README.md`, `docs/image-prompt-situation-manager-spec.md`, `package.json`

## 5. Do Not Edit Without Explicit Request

- backup: project 直下には見当たらない
- profile / user data: 特になし
- build artifact / generated: `dist/`, `node_modules/`, `build*.log`, `startup.log`, `dev-server.log`
- secrets / local state: 特になし

## 6. Related Boundaries

- UI: `src/`
- backend / business logic: なし
- desktop shell / launcher: `.bat` 起動導線
- external integration: クリップボード操作
- local persistence: 初回実装では未導入

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
- `dist/` やログは再生成物として扱い、コード変更と分けて確認する。
