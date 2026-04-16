# 画像生成プロンプト situation 管理機能 仕様

## 1. 位置づけ

- この文書は `/opsx:new` 相当の仕様書として扱う。
- 対象 project は `projects/skill-prompt-clipboard`。
- 既存 app を画像生成プロンプト管理向けに転用する。
- 旧用途のテンプレート内容やスキル表示は今回の目的から外す。
- ただしクリップボードコピー、リセット、エラー表示などの安全な共通処理は再利用する。
- 初回実装ではローカル Web アプリ内の固定データを正本とし、ユーザー編集の永続保存は後続候補にする。

## 2. 目的

- 特定 situation を再現するための複数プロンプトを一塊として扱えるようにする。
- situation の属性に合わせてタブ分類し、目的のプロンプト束を探しやすくする。
- 画像生成で使うワイルドカード候補を一覧化し、プロンプト作成時に参照できるようにする。
- 選択中のプロンプトまたは situation 全体をクリップボードへコピーできるようにする。

## 3. 対象ユーザーと利用場面

- 画像生成時に、似た場面や構図を何度も再現したいユーザー。
- キャラ、場所、構図、光、画風などの条件を situation として蓄積したいユーザー。
- 生成ツールへ貼り付ける前に、複数のプロンプト候補を比較しながら選びたいユーザー。

## 4. 用語

- situation: 再現したい場面や状況のまとまり。
- situation bundle: situation に属する複数のプロンプトの束。
- prompt variant: 同じ situation 内の個別プロンプト。基本版、短縮版、強調版、ネガティブなど。
- attribute tab: situation を探すための分類タブ。
- wildcard: `__lighting__` のように、差し替え候補を持つ語句のまとまり。

## 5. 初回スコープ

- 画像生成用の attribute tab を追加する。
- situation bundle のサンプルデータを追加する。
- situation 一覧から選ぶと、右側の編集欄に選択中 prompt variant が反映される。
- situation 内の prompt variant を選択できる。
- 既存のクリップボードコピー処理を使い、編集中の文面をコピーできる。
- ワイルドカード一覧を表示し、候補を参照できる。

## 6. 初回ではやらないこと

- 永続保存、追加、削除、並び替え。
- ワイルドカードのランダム展開。
- 複数候補の一括生成。
- Stable Diffusion、ComfyUI、Midjourney、NovelAI などのツール別出力最適化。
- package 名やフォルダ名の変更。

## 7. データ構造案

```ts
type ImagePromptAttribute = 'character' | 'pose' | 'place' | 'lighting' | 'style' | 'custom'

type ImagePromptVariant = {
  id: string
  label: string
  purpose: string
  prompt: string
}

type ImagePromptSituation = {
  id: string
  title: string
  attribute: ImagePromptAttribute
  summary: string
  tags: string[]
  variants: ImagePromptVariant[]
}

type WildcardGroup = {
  id: string
  token: string
  label: string
  options: string[]
}
```

## 8. UI 要件

- 属性切り替え、situation 選択、編集欄、コピー、リセットの主導線を分かりやすく保つ。
- 画像生成管理専用の見出しと文言で表示する。
- attribute tab は situation の探索用として使う。
- situation を選択した後、同じ bundle 内の prompt variant を切り替えられるようにする。
- ワイルドカードは編集欄の近くに参照パネルとして表示し、コピー主操作を邪魔しない。
- コピー中は既存通り二重実行を防ぐ。
- コピー失敗時は既存通りエラーを表示し、手動コピーできる編集欄を残す。

## 9. 既存挙動の保全

- 旧用途のテンプレート内容は残さなくてよい。
- クリップボードコピー、編集中の文面、リセット、コピー失敗時の表示は残す。
- `navigator.clipboard.writeText` と `document.execCommand('copy')` の fallback を維持する。
- `dist/`、`node_modules/`、ログファイルは正本として扱わず編集しない。
- テストは画像生成プロンプト管理の属性切り替え、リセット、ワイルドカード表示へ更新する。

## 10. 確認観点

- 画像生成用の主画面として表示される。
- 画像生成用の attribute tab を切り替えられる。
- situation を選ぶと prompt variant が表示され、編集欄に反映される。
- prompt variant を切り替えると編集欄が更新される。
- 編集後にコピーできる。
- リセットで選択中 variant の元文面に戻る。
- ワイルドカード一覧が表示され、空候補でも画面が崩れない。
- コピー失敗時のエラー表示が残る。

## 11. 未決事項

- 画像生成ツール別のプロンプト形式を分けるか。
- ワイルドカードを将来ランダム展開するか、候補選択だけに留めるか。
- ユーザー編集保存を `localStorage` で実装するか、JSON ファイル読み書きまで広げるか。
- package 名やフォルダ名は初回では維持するか、後続で変更するか。
