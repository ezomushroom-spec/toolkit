# empirical-prompt-tuning 2nd iteration candidates

## 1. 目的

初回 trial が成功で終わった対象の中から、次にもう一段だけ厳しく再評価すると効果が高い skill を絞る。

## 2. 優先候補

### 1. `windows-batch-launcher`

- 理由:
  - launcher failure は利用者体験への影響が大きい
  - `.venv` 破損時の fallback 範囲や first-run install の扱いに未決が残っている
- 2nd iteration で見たい点:
  - 壊れた `.venv` と複数 Python 環境の混在
  - install を勝手に走らせるかどうかの判断境界
  - log 出力と終了コードの扱い

### 2. `desktop-dnd-path-resolution`

- 理由:
  - browser / desktop shell 分岐は通ったが、parent-folder 解決条件は edge case で差が出やすい
  - path 抽出失敗時の warning 抑制や mixed drop の扱いをもう一段見たい
- 2nd iteration で見たい点:
  - folder と file が混在した drop
  - image file 以外の単体 file drop
  - 既存 valid value を持つ状態での repeated failure

### 3. `subagent-debug-review`

- 理由:
  - 使いどころの判断ミスがコストへ直結する
  - 初回では heavy / simple の分岐は見えたが、 borderline case をまだ試していない
- 2nd iteration で見たい点:
  - 並列化したくなるが利得が薄いケース
  - strict review と bug investigation のどちらへ寄せるか迷うケース
  - subagent 不使用判断の根拠

## 3. 今回は見送る対象

- `project-scaffolder`
  - 初回で description/body の主要ズレを補正済み
- `request-translate`
  - 現時点で ambiguity の再発が見えていない
- `implementation-planner`
  - まずは実案件での使われ方を見てからでよい
- `pre-implementation-diagnosis`
  - 初回で architecture case と patch case の差が十分見えた
- `code-review`
  - findings quality はまず安定している
- `ui-audit`, `ui-design-direction`, `ui-remake-safe`
  - UI 系は実案件が出た時に文脈つきで再評価した方が有益

## 4. 推奨順

1. `windows-batch-launcher`
2. `desktop-dnd-path-resolution`
3. `subagent-debug-review`

## 5. 実施条件

- fresh executor を使える回で行う
- 1 skill あたり 1 つの再評価テーマに絞る
- 初回 result を上書きせず、2nd iteration として別 result を残す
