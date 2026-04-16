# デバッグ優先安定化計画 2026-04-05

## 1. Goal

このアプリをこのまま機能改良し続けても破綻しにくい状態へ寄せることを目的にする。

主眼は次の3点。

- 比較系プリセットの仕様と実装の不一致を減らす
- プレビュー更新と操作系の状態管理を安定化する
- 保存/復元と preset 定義の契約を固定する

今回は実装計画のみを対象とし、機能追加や見た目の刷新は含めない。

## 2. Target Files

- `E:\codex\workspace\projects\narrative-thumbnail-studio\app\ui\main_window.py`
  - 状態の正本が集中しており、プレビュー更新、保存/読込、割当順、オフセット管理の中心。
- `E:\codex\workspace\projects\narrative-thumbnail-studio\app\ui\preview_panel.py`
  - ズーム、パン、並び替え、split 操作の判定と見た目を持つ。
- `E:\codex\workspace\projects\narrative-thumbnail-studio\app\core\layout_engine.py`
  - 描画ロジックとセル境界計算の正本候補。
- `E:\codex\workspace\projects\narrative-thumbnail-studio\app\core\presets.py`
  - JSON プリセット定義のロードとバリデーションを担う。
- `E:\codex\workspace\projects\narrative-thumbnail-studio\app\presets\*.json`
  - UI と描画が前提にしているパラメータ定義の正本。
- `E:\codex\workspace\projects\narrative-thumbnail-studio\app\core\exporter.py`
  - 単体出力と一括出力の整合性確認対象。
- `E:\codex\workspace\projects\narrative-thumbnail-studio\app\ui\image_pool_panel.py`
  - チェック選択と削除/順序変更の入口。
- `E:\codex\workspace\projects\narrative-thumbnail-studio\app\test_main_window.py`
- `E:\codex\workspace\projects\narrative-thumbnail-studio\app\test_preview.py`
- `E:\codex\workspace\projects\narrative-thumbnail-studio\app\test_gui.py`
  - 現状は確認スクリプト寄りなので、最小回帰確認の受け皿候補。

## 3. Ordered Implementation Steps

### Step 1. 比較系プリセットの契約を固定する

- 目的
  - `split_ratio` など、描画コードが使う値を preset JSON と UI の両方で正式に扱う。
- 対象
  - `app/presets/vsplit.json`
  - `app/presets/hsplit.json`
  - `app/presets/bg_color_split.json`
  - `app/presets/blur_border.json`
  - `app/presets/fade_transition.json`
  - `app/presets/arrow_compare.json`
  - `app/presets/label_compare.json`
  - `app/core/presets.py`
- この順番にする理由
  - ここが曖昧なまま UI や preview を直すと、後でまた preset 定義不足が露出するため。
- 確認点
  - JSON に存在する値だけを UI が見せること
  - コードが期待するパラメータが JSON に揃っていること
  - `catalog.fill_mode` のような未接続定義を洗い出して処理方針を決めること
- 戻し方
  - 変更対象を JSON と `presets.py` に限定し、描画コードへはまだ広げない

### Step 2. セル形状の正本を一本化する

- 目的
  - 見た目、当たり判定、ハンドル位置、並び替えターゲット表示の基準を揃える。
- 対象
  - `app/core/layout_engine.py`
  - `app/ui/preview_panel.py`
- この順番にする理由
  - 斜めワイプで顕在化した問題が、split 系全体の構造問題だから。
- 作業内容
  - 矩形 bounds と path 形状の役割を分ける
  - split 系は path ベースの問い合わせ API を持てるように整理する
  - `blur_border` と `fade_transition` を近似で済ませるか厳密にするかを決める
- 確認点
  - `vsplit`、`hsplit`、`diagonal_wipe` のズーム、パン、並び替え、split drag が見た目と一致すること
- 戻し方
  - まずは `preview_panel.py` 内に閉じた補助関数で導入し、必要なら後から `layout_engine.py` 側へ昇格する

### Step 3. プレビュー更新経路を安定化する

- 目的
  - 連続操作時の不要な再描画、古い worker の残留、`load_full()` の重複を減らす。
- 対象
  - `app/ui/main_window.py`
  - `app/ui/preview_panel.py`
  - 必要に応じて `app/core/image_pool.py`
- この順番にする理由
  - 仕様の正本が揃ってからでないと、先に最適化しても無駄な分岐が残るため。
- 作業内容
  - interactive 用画像の再利用方針を決める
  - worker の多重起動を減らす
  - `set_cell_bounds()` / `set_split_info()` / `update_offsets()` の責務を明確化する
- 確認点
  - パラメータ連打、split drag、wheel zoom、画像入替時に UI が古い状態へ戻らないこと
- 戻し方
  - 最初はキャンセル機構よりも「起動頻度削減」を優先し、変更範囲を `MainWindow` に寄せる

### Step 4. 保存/復元の契約を固定する

- 目的
  - プロジェクト保存/読込で戻る状態を明文化し、復元順依存を減らす。
- 対象
  - `app/ui/main_window.py`
  - `app/core/image_pool.py`
  - `app/ui/preset_panel.py`
- この順番にする理由
  - プレビューと preset 契約が安定していないと、保存形式を固定できないため。
- 作業内容
  - 保存対象を `selected_image_paths / assigned_image_paths / current_params / text_config / crop_offsets_by_path` に絞って正本化する
  - 読込順を固定する
  - slot 基準の legacy offset は互換読込だけ残す
- 確認点
  - 保存直後の再読込で、preset、割当順、クロップ、テキスト設定が一致すること
- 戻し方
  - 既存キーは残し、新フォーマットへ全面移行しない

### Step 5. 単体出力と一括出力の共通入口を整理する

- 目的
  - preview、単体出力、一括出力の画像解決とパラメータ適用を揃える。
- 対象
  - `app/ui/main_window.py`
  - `app/core/exporter.py`
- この順番にする理由
  - ここは user-visible な結果差分につながるため、安定化後にまとめて揃える価値が高い。
- 作業内容
  - 画像解決ロジックを 1 箇所に寄せる
  - `Exporter.export_all_presets()` の古い前提を整理する
- 確認点
  - 現在表示中の preset と単体出力が一致すること
  - 一括出力が preset ごとの必要枚数と current offsets を破綻なく扱うこと
- 戻し方
  - 既存の `export_single()` は温存し、呼び出し順の整理に留める

### Step 6. 最小回帰テストを追加する

- 目的
  - 今後の改良で再発しやすい箇所を自動確認できるようにする。
- 対象
  - `app/test_main_window.py`
  - `app/test_preview.py`
  - `app/test_gui.py`
  - 必要なら新規 `app/tests/` 配下
- この順番にする理由
  - 先に仕様と状態を安定化してからでないと、テストが固定できないため。
- 最低限の対象
  - `vsplit`
  - `diagonal_wipe`
  - `grid_2x2`
  - project save/load
- 確認点
  - 起動確認ではなく、値と状態の一致をアサーションすること
- 戻し方
  - 既存確認スクリプトは残しつつ、まずは小さな自動確認を足す

## 4. Risks

- `main_window.py` は責務が集中しているため、1 箇所の変更で preview、export、save/load の複数機能へ波及しやすい。
- split 系の仕様整理を中途半端に行うと、`diagonal_wipe` だけ直って他の comparison preset が置き去りになる。
- 保存形式を急に整理しすぎると、既存 `.nts.json` との互換を壊す。
- プレビュー最適化を先にやりすぎると、仕様未確定のまま複雑化する。

## 5. Unknowns Requiring Final Judgment

- `blur_border` と `fade_transition` の入力判定は、厳密な可視領域基準にするか、左右矩形近似のままにするか。
- `catalog.fill_mode = asymmetric` は実装を追加するか、preset JSON から外すか。
- comparison 系 preset に `split_ratio` を全面追加するか、操作可能 preset を限定するか。
- interactive 用画像キャッシュをどの粒度で持つか。
  - slot 単位
  - entry path 単位
  - output size を含む複合 key

## 6. Suggested Implementation Scope

初回の安全な着手範囲は次の4点に限定する。

- comparison 系 preset JSON と `presets.py` の契約整理
- `preview_panel.py` の split 系入力判定の整理
- `main_window.py` の split 更新と preview 更新責務の整理
- `catalog.fill_mode` の不一致解消

保存/復元の全面整理と worker 最適化は、その後の第2段で扱うのが安全。

