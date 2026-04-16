# START HERE

## この project は何か

- React、TypeScript、Vite、Vitest を前提にした小規模 Web UI サンプルです。
- 主操作、危険操作、エラー表示の基本パターンを安全に試すための雛形として扱います。

## 最初に読む順番

1. `AGENTS.md`
2. `PROJECT_SUMMARY.md`
3. `src/` と `tests/`

## 正本

- 正本コード: `src/`
- 正本文書: `AGENTS.md`, `PROJECT_SUMMARY.md`, `docs/`
- 正本テスト: `tests/`

## 主要入口

- 通常起動: `npm run dev`
- 主な確認方法: `npm run test`

## 触る前に注意するもの

- 壊してはいけない既存挙動: 保存、プレビュー、危険操作の確認導線、エラー表示
- 明示依頼なしで触らないもの: project 全体の構成変更、無関係なリファクタ
- backup / profile / generated: 現時点で project 直下の backup は見当たらない

## 最初の一手

- まず `AGENTS.md` を読んで UI 前提と確認観点を把握する。
- 次に `src/` と `tests/` を見て、主操作と危険操作の扱いを揃える。
