# 複数画像レイアウト拡張案 2026-04-05

## 1. Goal

複数画像を使ったサムネイル構成の表現幅を増やしつつ、現在の軽快な preview 操作と export 導線を崩さないことを目的にする。

今回の主眼は次の3点。

- 既存の `grid_2x2 / grid_h3 / center_hero / catalog / asymmetric` の延長として自然に増やせること
- 似た preset を増やしすぎず、用途ごとの差がはっきりしていること
- 既存の画像割当、クロップ、export、project 保存/復元の仕組みに乗せられること

## 2. 現状の評価

現状の複数画像系 preset は、基礎は揃っている。

- `grid_2x2`
  - 均等配置の基本形
- `grid_h3`
  - 横並びの比較や工程紹介向け
- `center_hero`
  - 主役1枚を強く見せる用途に向く
- `catalog`
  - 枚数変動に強い
- `asymmetric`
  - 変化はあるが、用途がやや限定的

不足しているのは「枚数」ではなく「見せ方の型」。

特に足りないのは次の系統。

- 縦長・スマホ向けの複数画像構成
- 主役1枚 + 補助2〜4枚を自然に見せる変則構成
- 工程や差分を順番付きで見せるストーリー型
- 作品まとめを高密度に見せるポートフォリオ型

## 3. 追加候補の分類

### A. 主役強調系

目的:
1枚を主役にし、他を補助に使う。

候補:

- `hero_top_strip`
  - 上に主役大、下に補助3枚横並び
- `hero_left_stack`
  - 左に主役大、右に補助2〜3枚縦積み
- `hero_bottom_pair`
  - 上に主役、下に補助2枚

向いている用途:

- 完成絵 + 差分
- メインビジュアル + 表情/細部
- 投稿サムネイルで一枚目を強く見せたい場合

### B. ストーリー系

目的:
順番や工程を見せる。

候補:

- `step_flow_3`
  - 3枚を左から右へ流す
- `step_flow_4`
  - 4枚を読み順付きで流す
- `before_after_plus_detail`
  - 比較2枚 + 詳細1枚

向いている用途:

- ラフ → 線画 → 着彩
- 修正前後 + 部分拡大
- 制作工程紹介

### C. 高密度一覧系

目的:
複数画像を一覧で強く見せる。

候補:

- `masonry_5`
  - 5枚の可変比率タイル
- `masonry_6`
  - 6枚の高密度タイル
- `portfolio_4`
  - 4枚を大小混在で見せる

向いている用途:

- 作品まとめ
- キャラ差分一覧
- 1投稿で多く見せたいケース

### D. 縦長向け系

目的:
900x1200 などの縦長出力で破綻しにくい構成を持つ。

候補:

- `vertical_hero_stack`
  - 上主役 + 下2段
- `vertical_triptych`
  - 3枚縦積み
- `vertical_catalog`
  - 縦長向けの可変一覧

向いている用途:

- スマホ閲覧想定
- Pixiv縦型
- 情報を縦方向に流したい構成

## 4. 優先度

初回に足す候補は 3 個で十分。

優先順:

1. `hero_top_strip`
2. `before_after_plus_detail`
3. `vertical_hero_stack`

理由:

- `hero_top_strip`
  - 既存の `center_hero` に近く、実装リスクが低い
  - 主役強調の需要が高い
- `before_after_plus_detail`
  - 比較系と複数画像系の橋渡しになり、このアプリの用途と合う
- `vertical_hero_stack`
  - 出力サイズの縦型 preset と相性が良く、既存価値を伸ばせる

## 5. 実装方針

### 方針A

まずは新規 preset を追加し、既存 UI のまま運用する。

利点:

- 安全
- 既存構造に乗せやすい
- デバッグ範囲が狭い

欠点:

- スロット比率を後から細かく変えたくなる

### 方針B

先に複数画像レイアウト共通の「スロット比率調整」を導入する。

利点:

- 拡張性が高い

欠点:

- preview、保存/復元、preset 契約に広く波及する
- 今の段階では重い

採用案:

- まずは方針A
- その後、必要になった preset 群だけ共通パラメータ化する

## 6. 対象ファイル

- `E:\codex\workspace\projects\narrative-thumbnail-studio\app\core\layout_engine.py`
  - 新規 compose 実装
- `E:\codex\workspace\projects\narrative-thumbnail-studio\app\core\presets.py`
  - JSON 読込自体は既存のままで足りる想定
- `E:\codex\workspace\projects\narrative-thumbnail-studio\app\presets\*.json`
  - 新規 preset 定義
- `E:\codex\workspace\projects\narrative-thumbnail-studio\app\ui\preset_panel.py`
  - 表示順や説明文の調整候補
- `E:\codex\workspace\projects\narrative-thumbnail-studio\app\ui\main_window.py`
  - slot role 名や保存/復元確認
- `E:\codex\workspace\projects\narrative-thumbnail-studio\app\test_regressions.py`
  - 最低限の回帰確認追加

## 7. 実装順

### Step 1

`hero_top_strip` を追加する

- 目的
  - 主役強調系の基準を1つ作る
- 影響
  - `layout_engine.py`
  - `presets/hero_top_strip.json`
- 確認
  - 3枚/4枚運用の見え方
  - preview のクロップ操作

### Step 2

`before_after_plus_detail` を追加する

- 目的
  - 比較用途を複数画像側へ広げる
- 影響
  - `layout_engine.py`
  - `presets/before_after_plus_detail.json`
- 確認
  - 3枚構成の割当順
  - ラベルとの相性

### Step 3

`vertical_hero_stack` を追加する

- 目的
  - 縦長出力の実用品を増やす
- 影響
  - `layout_engine.py`
  - `presets/vertical_hero_stack.json`
- 確認
  - 900x1200 での情報密度
  - PC表示/モバイル表示の見え方

### Step 4

preset 説明文とおすすめ導線を調整する

- 目的
  - 増えた preset の用途差を分かりやすくする
- 影響
  - `preset_panel.py`
  - preset preview 文言

### Step 5

回帰テストを追加する

- 目的
  - 新規複数画像 preset の保存/復元と描画契約を固定する
- 影響
  - `test_regressions.py`

## 8. リスク

- preset を増やしすぎると選択しづらくなる
- 似た構成が増えると違いが分かりにくい
- 先に ratio 調整や自由レイアウトまで広げると、preview 操作系へ波及して重くなる

## 9. 最小安全スコープ

初回は次の範囲に限定する。

- 新規 preset 3 個
- 既存 UI の構造は変えない
- 新規共通パラメータは増やさない
- 既存の drag / zoom / export / save-load の仕組みに乗せる

この範囲なら、体験を保ったまま複数画像レイアウトを素直に強化できる。

