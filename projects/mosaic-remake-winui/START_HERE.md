# START HERE

## この project は何か

- `mosaic-remake` の WinUI 3 移行用シェルです。
- 推論コアは当面 Python 側に残し、WinUI 側は画面骨格と接続入口を担当します。

## 最初に読む順番

1. `AGENTS.md`
2. `PROJECT_SUMMARY.md`
3. `README.md`
4. `start-winui.bat` と `debug-start-winui.bat`
5. WinUI 側の画面入口と Python bridge の接続箇所

## 正本

- 正本 UI シェル: この project 配下の WinUI 側コード
- 正本推論コア: 親案件の Python 側
- 正本文書: `README.md`, `AGENTS.md`, `PROJECT_SUMMARY.md`

## 主要入口

- 通常起動: `start-winui.bat`
- 代替入口: `debug-start-winui.bat`
- 主な確認方法: `dotnet build` と起動バッチでの生存確認

## 触る前に注意するもの

- 壊してはいけない既存挙動: Python bridge の health 導線、WinUI 起動安定性
- 明示依頼なしで触らないもの: PowerToys DLL 問題を避ける起動導線の前提
- backup / profile / generated: `bin/`, `obj/` などの生成物

## 最初の一手

- まず `AGENTS.md` と `PROJECT_SUMMARY.md` を読んで、WinUI shell と Python core の責務境界を確認する。
- そのうえで `README.md` を読んで、Python 側を正本に残す前提と起動時の注意を把握する。
- 次に `start-winui.bat` と `debug-start-winui.bat` を見て、通常の `dotnet run` 前提にしてよいかを判定する。
