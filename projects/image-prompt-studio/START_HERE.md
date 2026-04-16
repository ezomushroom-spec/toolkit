# START HERE

## この project は何か

- 画像生成用プロンプトを、situation の束として管理してコピーするローカルアプリです。
- 人物、ポーズ、場所、光、画風などの属性タブから situation を選び、基本版やネガティブ版などの prompt variant を切り替えられます。

## 最初に読む順番

1. `AGENTS.md`
2. `PROJECT_SUMMARY.md`
3. `README.md`
4. `docs/image-prompt-situation-manager-spec.md`
5. `src/App.tsx`
6. `src/App.test.tsx`
7. `src/App.css`, `src/index.css`

## 正本

- 現行挙動とデータ構造の正本: `E:\自作アプリ集\新しいフォルダー (2)`
- React 版の実装先: `src/`
- 移行判断と計画の正本: `AGENTS.md`, `PROJECT_SUMMARY.md`, `README.md`, `docs/`
- 正本テスト: `src/App.test.tsx`

## 主要入口

- 通常起動: `npm run dev`
- 主な確認方法: `npm run lint`, `npm run test`

## 触る前に注意するもの

- 壊してはいけない既存挙動: 属性切り替え、situation 選択、variant 切り替え、編集欄連動、コピー、リセット
- 明示依頼なしで触らないもの: 無関係な UI 全面改修、Vite 実行環境差分の広い掘り下げ
- backup / profile / generated: `dist` などの生成物

## 最初の一手

- まず `AGENTS.md` と `PROJECT_SUMMARY.md` を読んで、正本 Python app と React 版の境界を把握する。
- そのうえで `docs/reference-sd-prompt-manager-findings.md` と `docs/remake-direction-from-sd-prompt-manager.md` を読んで、正本の扱いと再構築方針を把握する。
- 次に `src/App.tsx` と `src/App.test.tsx` を見て、主操作とテストの対応を確認する。
