# UI デザイン方針

## 1. Screen Purpose

- 画面種別: 画像生成プロンプト管理の作業用 app 画面。
- 主操作: situation を選び、prompt variant を調整し、生成ツールへコピーする。
- 最初の数秒で伝えること: どの situation を選んでいて、どの文面をコピーできるか。

## 2. Constraints And Fixed Assumptions

- UI の大きな変更は許容する。
- 旧用途のテンプレート管理 UI は保全対象ではない。
- クリップボードコピー、リセット、コピー失敗時のエラー表示は維持する。
- 外部 wildcard や SQLite 書き込みはまだ入れない。
- デザイン性は確保するが、制作作業を邪魔する装飾は避ける。

## 3. Proposed Composition

- 上部: app 名、現在の保存方式、主要な今後の領域を示すコンパクトな masthead。
- 左: attribute と situation の選択。
- 中央: 選択中 situation の説明、variant 切り替え、prompt 編集、コピー操作。
- 下部または右下: wildcard 候補の参照。
- 役割のない装飾カードは置かない。

## 4. Visual Hierarchy And Main Action

- 最強調: 編集中 prompt の textarea と `この文面をコピー`。
- 次点: situation タイトルと variant 切り替え。
- 補助: tags、wildcard、保存方式、将来機能の表示。
- アクセント色は 1 系統に制限し、背景は暗めの作業台 + 明るい編集面で差をつける。

## 5. Responsive Behavior

- desktop: 左 sidebar + 中央 editor の 2 カラムを維持。
- narrow: 1 カラムへ落とし、attribute、situation、editor、wildcard の順で縦に並べる。
- タブや variant は折り返しを許容し、押しやすさを優先する。

## 6. Fit With Existing UI

- 現在の `category-list`、`template-list`、`editor-panel` の概念は残す。
- ただし名称と見た目は、画像生成プロンプト管理に合わせて置き換える。
- 正本 SD Prompt Manager の 3 領域構成は、今後 `Prompt Studio`、`Wildcard Library`、`Builder` として段階導入する。

## 7. Validation Points

- 主操作が `この文面をコピー` だと分かる。
- situation と variant の関係が分かる。
- コピー中に二重実行できない。
- エラーが編集欄の近くに出る。
- 狭い画面でも操作順が崩れない。
- 装飾より作業領域が優先されている。
