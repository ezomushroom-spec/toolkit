# START HERE

## この project は何か

- 意図ラベル集を下から出るシートUIで呼び出して使えるローカル小窓デスクトップアプリ

## 最初に読む順番

1. `AGENTS.md`
2. `PROJECT_SUMMARY.md`
3. `README.md`
4. `docs/pre-implementation-decision.md`
5. `src/` と `desktop-electron/` の主要ファイル

## 正本

- 正本コード: `src/`, `desktop-electron/`
- 正本設定: `package.json`, `vite.config.ts`, `tsconfig*.json`, `eslint.config.js`, `desktop-electron/package.json`
- 正本文書: `AGENTS.md`, `PROJECT_SUMMARY.md`, `README.md`, `docs/pre-implementation-decision.md`
- 正本未確定なら、その候補: なし

## 主要入口

- 通常起動: `start.bat`
- Web 確認: `start-web.bat`
- 代替入口: `debug-start.bat`, `debug-start-web.bat`
- 主な確認方法: `npm run test`, `npm run build:web`

## 触る前に注意するもの

- 壊してはいけない既存挙動: 小窓起動、シート開閉、検索、ラベル選択、コピー
- 明示依頼なしで触らないもの: Vite 基本設定や shell 起動導線の大幅変更
- backup / profile / generated: `dist/`, `node_modules/`, `desktop-electron/node_modules/`, `build*.log`, `startup.log`, `startup-web.log`, `dev-server.log`, `desktop-electron/runtime/`

## 最初の一手

- `AGENTS.md` と `PROJECT_SUMMARY.md` を読んで正本境界を確認し、次に `src/App.tsx`, `src/data/intentLabels.ts`, `desktop-electron/main.js` を見る
