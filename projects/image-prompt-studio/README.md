# Image Prompt Situation Manager

画像生成用プロンプトを situation 単位で束ね、属性タブから選んでコピーできるローカルアプリです。  
同じ場面の基本版、構図強化版、ネガティブ版などを切り替えながら、生成ツールへ貼り付ける文面を整えられます。

## 主な機能

- `人物` `ポーズ` `場所` `光` `画風` `カスタム` の属性タブ切り替え
- situation 選択と編集欄の連動
- situation 内の複数 prompt variant 切り替え
- prompt / negative prompt の分離編集
- 1 クリックでのクリップボードコピー
- ネガティブプロンプト単体のコピー
- situation 全体のコピー
- 選択中 variant の `localStorage` 保存
- 保存データの初期化
- コピー失敗時のエラー表示
- 選択中 variant へのリセット
- 正本 `data/wildcards` 由来の txt ワイルドカード参照
- `__name__` 形式のワイルドカード構文コピー

## 使い方

1. 属性タブから目的に近い分類を選びます。
2. situation 一覧から再現したい場面を選びます。
3. `基本`、`光重視`、`ネガティブ` などの prompt variant を選びます。
4. 必要なら右側の prompt / negative prompt 欄で文章を調整します。
5. 残したい調整は `選択中の版を保存` で保存します。
6. `この文面をコピー`、`ネガティブをコピー`、または `situation 全体をコピー` を押して生成ツールへ貼り付けます。

## 開発コマンド

```bash
npm install
npm run dev
```

テストと lint は次のコマンドで実行できます。

```bash
npm run import:wildcards
npm run lint
npm run test
npm run build
```

## 現在の注意点

- `npm run lint` と `npm run test` は通過済みです。
- `npm run build` は今回の確認で通過済みです。
- `npm run import:wildcards` は `E:\自作アプリ集\新しいフォルダー (2)\data\wildcards` を読み取り専用で参照し、`src/generated/canonicalWildcards.ts` を再生成します。
- 初回取り込み対象は `school komono.txt`、`tipo_location.txt`、`view.txt` の 3 件に限定しています。未確認の txt と txt 以外のファイルは summary として除外します。
- 正本 Python app と正本 wildcard ファイルには書き込みません。

## 主な構成

- `src/App.tsx`: situation 定義、属性タブ、variant 切り替え、prompt / negative prompt、コピー処理、localStorage 保存、状態管理
- `src/App.css`: 画面レイアウトとコンポーネント見た目
- `src/index.css`: 配色、ベースタイポグラフィ、全体テーマ
- `src/App.test.tsx`: 属性タブ、variant 切り替え、リセット、localStorage 保存、ワイルドカード表示のテスト
- `scripts/import-canonical-wildcards.mjs`: 正本 wildcard txt の読み取り専用 importer
- `src/generated/canonicalWildcards.ts`: importer で生成される正本由来 wildcard の表示データ

## 想定している次の拡張

- situation と prompt variant の追加、編集、削除
- ワイルドカードの候補選択やランダム展開
- 画像生成ツール別の出力形式切り替え
