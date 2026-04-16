# 画像生成プロンプト situation 管理機能 実装計画

## 1. 依頼の要点

- この文書は `/opsx:ff` 相当の実装計画として扱う。
- 目的: 既存 `skill-prompt-clipboard` を画像生成プロンプト管理向けに転用し、画像生成プロンプトを situation 単位で管理できるようにする。
- 対象 project: `projects/skill-prompt-clipboard`
- 変更したいこと: situation bundle、attribute tab、prompt variant、ワイルドカード参照、コピー導線を追加する。
- 変えないこと: コピー fallback、リセット、コピー中の二重実行防止、コピー失敗時のエラー表示。
- 省くこと: 旧用途のテンプレート管理、スキルチップ表示、旧用途の文言。

## 2. 現状確認

- 対象画面: `src/App.tsx` の単一画面。
- 関連処理: situation 定義、属性選択、situation 選択、variant 選択、編集欄連動、クリップボードコピー、リセット。
- 関連データ: `imagePromptSituations`、`attributeLabels`、`wildcardGroups`。
- 正本: `src/App.tsx`、`src/App.css`、`src/App.test.tsx`。
- 制約: `dist/`、`node_modules/`、ログファイルは正本ではないため編集しない。

## 3. 論点分解

- UI の論点: 画像生成プロンプト管理専用画面として、属性、situation、variant、ワイルドカードの関係を分かりやすくする。
- データの論点: 既存 `PromptTemplate` ではなく、画像生成用の `ImagePromptSituation` を正本データにする。
- 外部 I/O の論点: 初回は既存クリップボードコピーのみ。保存やファイル I/O は扱わない。
- 互換性の論点: app 内の旧用途向け表示は削除対象だが、コピー処理と安全状態は維持する。
- 運用上の論点: 初回は固定サンプルデータで UI と流れを固め、保存機能は後続判断にする。

## 4. 最小実装単位

### Step 1

- 目的: 画像生成用データ型とサンプルデータを追加する。
- 触る場所: `src/App.tsx`
- この段階で確認すること: TypeScript の型エラーがないこと。
- 戻し方: 追加した型とデータ定義だけを削除する。

### Step 2

- 目的: 画面全体を画像生成プロンプト管理向けの文言と構造に置き換える。
- 触る場所: `src/App.tsx`、必要最小限で `src/App.css`
- この段階で確認すること: 画像生成用の属性タブと situation 選択が表示されること。
- 戻し方: 置き換え前の `App.tsx` と `App.css` へ戻す。

### Step 3

- 目的: attribute tab、situation 一覧、prompt variant 選択を追加する。
- 触る場所: `src/App.tsx`、`src/App.css`
- この段階で確認すること: attribute tab を切り替え、situation と variant を選べること。
- 戻し方: 画像生成用 UI ブロックと state を削除する。

### Step 4

- 目的: 編集欄、コピー、リセットを画像生成 prompt variant に対応させる。
- 触る場所: `src/App.tsx`
- この段階で確認すること: 選択中 variant の文面が編集欄に入り、コピーとリセットが動くこと。
- 戻し方: 画像生成用 state と variant 参照処理を戻す。

### Step 5

- 目的: ワイルドカード参照パネルを追加する。
- 触る場所: `src/App.tsx`、`src/App.css`
- この段階で確認すること: ワイルドカード一覧が表示され、コピー主操作を邪魔しないこと。
- 戻し方: ワイルドカードデータと表示パネルを削除する。

### Step 6

- 目的: テストと文書を画像生成プロンプト管理向けに更新する。
- 触る場所: `src/App.test.tsx`、必要なら `README.md`、`PROJECT_SUMMARY.md`
- この段階で確認すること: 画像生成用タブ、situation 選択、variant リセット、ワイルドカード表示を確認できること。
- 戻し方: 追加テストと文書追記を削除する。

## 5. 確認計画

- 正常系: 画像生成 situation 選択、variant 切り替え、コピー、situation 全体コピー、リセット。
- 失敗系: クリップボード失敗時にエラー表示が出ること。
- 空入力: 編集欄を空にしても画面が落ちず、コピー操作の扱いが明確なこと。
- 不正設定: 初回スコープでは外部設定なし。
- 存在しないパス: 初回スコープではファイルパス入力なし。
- 途中停止 / キャンセル: コピー中は二重実行できないこと。
- 危険操作: 削除、上書き、外部送信は初回スコープ外。
- メモリ / GPU / 長時間処理: 対象外。ローカル UI とクリップボード操作のみ。

## 6. 実行する確認コマンド

- `npm run test`
- `npm run lint`
- `npm run build`

## 7. 未決事項

- 画像生成ツール別形式は初回では分けない。
- 永続保存は初回では入れない。
- ワイルドカードのランダム展開は初回では入れない。
- app 名称変更は初回では行わない。
- `E:\自作アプリ集\新しいフォルダー (2)` の参考元は `docs/reference-sd-prompt-manager-findings.md` に要点を整理済み。
- 参考元から直接取り込む場合は、まず txt wildcard の読み取り専用インポートから検討する。

## 8. 完了条件

- 画像生成用の situation bundle を属性タブで探せる。
- situation 内の複数 prompt variant を切り替えられる。
- 選択中 variant を編集してコピーできる。
- リセットで選択中 variant の元文面に戻せる。
- ワイルドカード候補を参照できる。
- 旧用途のテンプレート導線が画像生成プロンプト管理導線へ置き換わっている。
- `npm run test` と `npm run lint` の結果を報告できる。
