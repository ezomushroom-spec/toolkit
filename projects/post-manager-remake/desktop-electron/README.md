# Post Manager Electron Shell

このディレクトリは、既存の Python / FastAPI ベースの Post Manager を Electron で包むための最小シェルです。

## 方針

- 業務処理は `../app` の Python 側をそのまま使う
- Electron はローカルデスクトップの起動基盤とウィンドウを担当する
- D&D やフォルダ選択の強化はこの上に積む

## 初回セットアップ

```bash
npm install
```

## 起動

```bash
npm start
```

## 一括準備

プロジェクトルートにある `prepare_electron_migration.bat` を使うと、

- `app` のバックアップ作成
- `desktop-electron` の `npm install`
- Electron シェル起動

を順番に実行できます。

## 補足

- Python backend が単体起動できない場合、先に `../app/start_webui.bat` を確認してください
- この段階では UI は既存 Web UI をそのまま表示します
- backend の起動失敗ログは `runtime/backend.log` に追記されます
