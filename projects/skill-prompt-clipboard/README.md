# Image Prompt Situation Manager

画像生成用プロンプトを situation 単位で束ね、属性タブから選んでコピーできるローカルアプリです。  
同じ場面の基本版、構図強化版、ネガティブ版などを切り替えながら、生成ツールへ貼り付ける文面を整えられます。

## 主な機能

- `人物` `ポーズ` `場所` `光` `画風` `カスタム` の属性タブ切り替え
- situation 選択と編集欄の連動
- situation 内の複数 prompt variant 切り替え
- 1 クリックでのクリップボードコピー
- situation 全体のコピー
- コピー失敗時のエラー表示
- 選択中 variant へのリセット
- ワイルドカード候補の参照

## 使い方

1. 属性タブから目的に近い分類を選びます。
2. situation 一覧から再現したい場面を選びます。
3. `基本`、`光重視`、`ネガティブ` などの prompt variant を選びます。
4. 必要なら右側の編集欄で文章を調整します。
5. `この文面をコピー` または `situation 全体をコピー` を押して生成ツールへ貼り付けます。

## 開発コマンド

```bash
npm install
npm run dev
```

テストと lint は次のコマンドで実行できます。

```bash
npm run lint
npm run test
```

## 現在の注意点

- `npm run lint` と `npm run test` は通過済みです。
- `npm run build` は今回の確認で通過済みです。

## 主な構成

- `src/App.tsx`: situation 定義、属性タブ、variant 切り替え、コピー処理、状態管理
- `src/App.css`: 画面レイアウトとコンポーネント見た目
- `src/index.css`: 配色、ベースタイポグラフィ、全体テーマ
- `src/App.test.tsx`: 属性タブ、variant 切り替え、リセット、ワイルドカード表示のテスト

## 想定している次の拡張

- situation と prompt variant の追加、編集、削除
- `localStorage` などによるローカル保存
- ワイルドカードの候補選択やランダム展開
- 画像生成ツール別の出力形式切り替え
