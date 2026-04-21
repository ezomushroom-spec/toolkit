# empirical-prompt-tuning 初回ロールアウト計画

## 1. 目的

- `Critical` な workspace skill に対して、empirical evaluation の前段である Iteration 0 と固定 scenario 設計を終える
- 初回 trial evaluation の対象を 3 件に絞り、運用コストを増やしすぎない

## 2. 対象

初回 3 件:

1. `project-scaffolder`
2. `windows-batch-launcher`
3. `subagent-debug-review`

後続候補:

4. `project-safety-snapshot`
5. `request-translate`

完了済み:

- `project-scaffolder`
- `windows-batch-launcher`
- `subagent-debug-review`

次の候補:

1. `project-safety-snapshot`
2. `request-translate`

初手は `project-scaffolder` とした。
理由は、生成物と停止条件が比較的観測しやすく、初回 empirical evaluation の判定軸を固めやすかったため。
実行準備は `empirical-prompt-tuning-first-trial_project-scaffolder_20260422.md` を正本とした。

## 3. 実装順

### Step 1

- 目的: Iteration 0 の静的レビューで description/body 乖離と古い参照を潰す
- 触る場所: 対象 skill の `SKILL.md`
- 戻し方: 各 skill の個別差分を戻す

### Step 2

- 目的: scenario と checklist を固定する
- 触る場所: 本文書または skill 付属 template
- 戻し方: scenario 文書差分を戻す

### Step 3

- 目的: 委任許可がある回で fresh executor による empirical evaluation を実施する
- 触る場所: 新規 evaluation log
- 戻し方: evaluation log を trial 記録として残し、target skill の修正だけを個別に戻す

## 4. 固定 scenario

### 4.1 `project-scaffolder`

#### Scenario A: 新規 project の中央値ケース

- User-like request: 画像整理ツール用に新しい project を立ち上げたい
- Case type: median

Checklist:

- [critical] `projects/<slug>/` と標準 3 文書が作られる
- `docs/` に初期計画文書が揃う
- 不明項目を勝手に作り込みすぎない
- 既存 project と衝突したら止まる

#### Scenario B: 日本語 project 名

- User-like request: 日本語名の project を安全に作りたい
- Case type: edge

Checklist:

- [critical] Windows で危険な文字を避けて folder 名を決める
- 本来の project 名の意味が失われすぎない
- 初期文書に未確定項目を残せる

### 4.2 `windows-batch-launcher`

#### Scenario A: dev server 起動 batch の作成

- User-like request: `start.bat` と `debug-start.bat` を作ってほしい
- Case type: median

Checklist:

- [critical] working directory 固定と失敗時可視化が入る
- ASCII 安全な batch 文面になる
- command 存在確認または代替 interpreter 方針がある
- debug launcher の役割が分かる

#### Scenario B: Python interpreter の食い違い

- User-like request: `py -3` だと落ちるので安全に直したい
- Case type: edge

Checklist:

- [critical] broad selector を盲信しない
- project-local interpreter 優先が示される
- log で実際の interpreter を確認できる

### 4.3 `subagent-debug-review`

#### Scenario A: 複数原因候補がある重い不具合

- User-like request: 保存失敗とフリーズの原因を切り分けたい
- Case type: median

Checklist:

- [critical] まず単純案件か分解可能案件かを判定する
- 委任するとしても調査役に限定する
- 主エージェントが最終統合責任を持つ
- 最終出力がレビューと修正方針にまとまる

#### Scenario B: 1 ファイルだけの軽微不具合

- User-like request: null 参照 1 か所だけを見てほしい
- Case type: edge

Checklist:

- [critical] 安易に subagent を使わない
- 重い調査フローへ拡張しない
- 最小修正方針へ寄せる

## 5. empirical evaluation 実施条件

- ユーザーが明示的に委任を許可している
- fresh executor を毎回分けられる
- expected answer を leak しない
- result log に成功 / 失敗 / 裁量補完 / failed critical item を残せる

## 6. 今回時点の確認結果

- Iteration 0 の静的レビューは実施済み
- `project-scaffolder` の empirical trial は実施済み
- `windows-batch-launcher` の empirical trial は実施済み
- `subagent-debug-review` の empirical trial は実施済み
- `project-safety-snapshot` の empirical trial は実施済み
- `request-translate` の empirical trial は実施済み
- 初回 3 件はいずれも `[critical]` failure なし
- 後続候補 2 件も `[critical]` failure なし
- 次段では `Important` 以下へ横展開するか、既存 trial の cleanup と記録整理へ移るかを決めればよい
