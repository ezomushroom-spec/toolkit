# Project Summary

## 1. Purpose

- 意図ラベル集を下から出るシートUIで呼び出して使えるローカル小窓デスクトップアプリ
- Codex 利用時に skill 名を覚えたくない利用者向け

## 2. Source of Truth

- この folder の役割: 意図ラベル集をローカル小窓で呼び出す frontend + desktop shell
- 正本コード: `src/`, `desktop-electron/`
- 正本設定: `package.json`, `vite.config.ts`, `tsconfig*.json`, `eslint.config.js`, `desktop-electron/package.json`
- 正本データ: `src/data/intentLabels.ts`
- 正本文書: `AGENTS.md`, `START_HERE.md`, `PROJECT_SUMMARY.md`, `README.md`
- 比較対象や参照専用 backup: なし

## 3. Primary Entry Points

- 通常起動: `start.bat`
- 代替入口: `debug-start.bat`, `start-web.bat`, `debug-start-web.bat`
- ビルドや検証の主要コマンド: `npm run test`, `npm run build:web`

## 4. Safe Read Scope

- 初見で読んでよいディレクトリ: `src/`, `docs/`
- 先に確認すべき文書: `AGENTS.md`, `README.md`, `PROJECT_SUMMARY.md`

## 5. Do Not Edit Without Explicit Request

- backup: なし
- profile / user data: なし
- build artifact / generated: `dist/`, `node_modules/`, `desktop-electron/node_modules/`, `build*.log`, `startup.log`, `startup-web.log`, `dev-server.log`, `desktop-electron/runtime/`
- secrets / local state: なし

## 6. Related Boundaries

- UI: `src/App.tsx`, `src/App.css`, `src/index.css`
- backend / business logic: なし
- shell / launcher: `desktop-electron/main.js`, `desktop-electron/preload.js`, `start.bat`, `debug-start.bat`
- 外部連携や運用境界: クリップボード操作のみ

## 7. Risks For Subagents

- 誤認しやすい正本や境界: `dist/` を正本と誤認しやすい
- 壊しやすい運用資産: ローカルデータ定義 `src/data/intentLabels.ts`
- 並列編集で衝突しやすい場所: `src/App.tsx`, `src/App.css`

## 8. Recommended First Step

- `START_HERE.md` を読み、正本コードと未確定項目を切り分ける

## 9. Rollback Hint

- `src/` と docs を単位に戻す
- `dist/` やログは再生成物として扱い、コード変更と分けて確認する
