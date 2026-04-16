# intent-label-sheet

意図ラベル集を、**独立した小窓デスクトップアプリ**として呼び出して使うための project です。
内部 UI は React + Vite で構成し、`desktop-electron/` の shell から小窓表示します。

## 通常起動

```powershell
.\start.bat
```

初回は frontend と desktop shell の依存導入を行い、その後に frontend を build して Electron 小窓を開きます。

## ブラウザ確認

```powershell
.\start-web.bat
```

UI のみをブラウザで確認したい場合の入口です。

## 主な機能

- 意図ラベル一覧の表示
- カテゴリ絞り込み
- 検索
- おすすめの言い方のコピー
- 内部対応 skill の確認
- 右下寄せの小窓としての表示

## 構成

- `src/`: frontend の正本
- `desktop-electron/`: 小窓 shell
- `src/data/intentLabels.ts`: 意図ラベルのローカル定義

## 想定する使い方

- skill 名を覚えずに「やりたいこと」からラベルを選ぶ
- 小窓のまま例文をコピーして Codex へ渡す
