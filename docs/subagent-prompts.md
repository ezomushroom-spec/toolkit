# Subagent And Skill Cheat Sheet

毎回 skill 名や順番を思い出さなくて済むように、この workspace で実際に使える意図ラベル、skill、委任の使い分けをまとめる。

- ユーザーは skill 名を暗記しなくてよい
- まずは「何をしたいか」の意図ラベルで伝える
- skill 名は内部対応や明示指定が必要なときだけ使う
- subagent はユーザーが明示的に委任を許可したときだけ使う
- 迷ったら、まず論点整理系 skill を使い、その後で診断、計画、実装へ進む
- 近い skill が複数あるときは、「何を決めたいか」で分ける

## 1. 基本順序

`依頼整理 -> 方式比較 -> 実装計画 -> 実装 -> レビュー -> 文書更新`

内部対応の標準順序:

`request-translate -> pre-implementation-diagnosis -> implementation-planner -> plan-review -> implement -> code-review -> documentation update`

## 2. 役割マップ

### 2.1 依頼整理と診断

| 意図ラベル | 内部対応 | 使うとき |
|---|---|---|
| `依頼整理` | `request-translate` | 曖昧、複数論点、口語的な依頼を論点分解するとき |
| `方式比較` | `pre-implementation-diagnosis` | 新規 UI、技術選定、構成変更、クロスレイヤー設計、再構築方針を比較するとき |
| `実装計画` | `implementation-planner` | 実装順、確認点、戻し方を計画化し、最後に brief まで固めるとき |
| `計画レビュー` | `plan-review` | 計画の穴や breakage risk を確認するとき |

### 2.1.1 project 開始

| 意図ラベル | 内部対応 | 使うとき |
|---|---|---|
| `新規project` | `project-scaffolder` | 新しい project を標準構成で立ち上げるとき |

### 2.2 UI 系

| 意図ラベル | 内部対応 | 使うとき |
|---|---|---|
| `UI監査` | `ui-audit` | 既存 UI の問題を診断したいとき |
| `UI方向` | `ui-design-direction` | 画面構成、視覚階層、レイアウト方向、業種や製品性格に合うトーンを決めたいとき |
| `UI改善` | `ui-remake-safe` | 既存挙動を保ったまま UI を実装改善したいとき |
| `overlap確認` | `ui-overlap-guard` | 密なレイアウトの衝突、潰れ、スクロール干渉を疑うとき |
| `画像仕上げ判断` | `image-finishing-tool-design` | 画像仕上げツールとしての製品方針、レシピ再利用、preview / final 一貫性、batch 志向を見たいとき |

### 2.3 実装、レビュー、不具合

| 意図ラベル | 内部対応 | 使うとき |
|---|---|---|
| `レビュー` | `code-review` | 変更後の主要リスクをレビューするとき |
| `重い不具合レビュー` | `subagent-debug-review` | 複雑な不具合や厳密レビューを切り分けたいとき |
| `snapshot` | `project-safety-snapshot` | 高リスク変更の前に軽量 snapshot を作ってから進めたいとき |

### 2.4 環境、構成、OS 依存

| 意図ラベル | 内部対応 | 使うとき |
|---|---|---|
| `D&Dパス確認` | `desktop-dnd-path-resolution` | D&D の path 解決や desktop shell 差を扱うとき |
| `起動バッチ整備` | `windows-batch-launcher` | Windows の起動バッチや launcher を整備するとき |

## 3. 迷いやすい skill の分け方

### 3.1 `request-translate` と `pre-implementation-diagnosis`

- 依頼が曖昧、複数論点、何を決めるか自体が曖昧なら `request-translate`
- 比較候補を出して構成や方式を選びたいなら `pre-implementation-diagnosis`

### 3.2 `ui-audit` と `ui-design-direction`

- 今の UI の何が悪いかを知りたいなら `ui-audit`
- どういう UI にするべきかを決めたいなら `ui-design-direction`

### 3.3 `ui-design-direction` と `ui-remake-safe`

- 構図、視覚階層、画面構成、製品に合う方向を決めたいなら `ui-design-direction`
- 実装を前提に、既存挙動を保ちながら UI を直したいなら `ui-remake-safe`

### 3.4 `ui-remake-safe` と `ui-audit`

- 改善方針の診断だけなら `ui-audit`
- 実装を前提に、壊さず改善したいなら `ui-remake-safe`

### 3.5 `pre-implementation-diagnosis` と `image-finishing-tool-design`

- 技術方式やアーキテクチャを比較したいなら `pre-implementation-diagnosis`
- 画像仕上げツールとして何を守るべきか、何を避けるべきかを見たいなら `image-finishing-tool-design`

## 4. よく使う言い方

skill 名は不要で、まず次の言い方でよい。

### 4.1 依頼がふわっとしている

```text
依頼整理: この依頼を論点分解して。
```

### 4.2 実装方式を比較したい

```text
方式比較: この案件の実装方式候補を比較して。
```

### 4.3 実装順を固めたい

```text
実装計画: この改修の実装順、確認点、戻し方を整理して。
```

### 4.4 計画の穴を見たい

```text
計画レビュー: この計画の breakage risk と scope の穴を見て。
```

### 4.5 新しい project を作りたい

```text
新規project: この目的で新しい project を立ち上げて。
```

### 4.6 既存 UI の問題を見たい

```text
UI監査: この画面の主操作、危険操作、エラー表示を監査して。
```

### 4.7 UI の方向を決めたい

```text
UI方向: この画面の構図と視覚階層を整理して。
```

### 4.8 業種や製品性格に合う方向を見たい

```text
UI方向: この UI 案が製品性格や業種に合う方向か見て。
```

### 4.9 画像仕上げツールとして判断したい

```text
画像仕上げ判断: この提案が画像仕上げツールとして適切か見て。
```

### 4.10 既存 UI を壊さず改善したい

```text
UI改善: この UI を壊さず改善する方針を出して。
```

### 4.11 密なレイアウトの overlap を見たい

```text
overlap確認: このレイアウトの overlap risk を見て。
```

### 4.12 高リスク変更の前に安全退避したい

```text
snapshot: この project の snapshot を作ってから始めて。
```

### 4.13 変更後の主要リスクをレビューしたい

```text
レビュー: この変更の主要リスクをレビューして。
```

## 5. 委任を使うとき

ユーザーが「サブエージェントを使ってよい」と明示したときは、まず次を使う。

```text
workspace-delegation-orchestrator を使って、いま自分でやる作業と委任する探索を切り分けて。
```

探索系の委任で相性がよい例:

- 入口文書の不整合確認
- project 構成の棚卸し
- 実行入口や依存の洗い出し
- docs の古い参照や重複の点検

## 6. project 特化の候補

- `post-manager-remake`: `post-manager-maintainer`, `legacy-app-remake-planner`
- Pixiv 系横断: `pixiv-tool-workspace-maintainer`
- Windows GUI workspace 全体把握: `windows-python-gui-repo-triage`
- 技術負債の棚卸し: `generate-snapshot`

## 7. 棚卸しの考え方

今の skill 群は数が多いため、削除より先に「入口整理」を優先する。

- UI 系は統合より役割分担の明文化を優先する
- `project-scaffolder` は project 開始専用で、依頼整理や計画 skill の代替にしない
- `project-safety-snapshot` は高リスク変更前の補助で、常時運用にしない
- skill 名の暗記は前提にせず、意図ラベルから内部対応へ結びつける
- `ui-design-direction` は業種適合やアンチパターンの確認も含む
- `ui-remake-safe` は overlap や scroll 干渉の防止も含む
- 診断系は段階順に並べて使い分ける
- project 特化 skill は無理に一般化しない
- 新しい skill を足すときは、まず既存 skill の置き換えか補助かを明示する

棚卸しが必要か迷ったら、次を確認する。

- 同じ依頼で複数 skill が同じ説明に見えるか
- skill 名だけでは役割差が分からないか
- 実案件で trigger が不安定になっているか

この 3 つが増えてきたら、skill の削除より先にこの文書を更新する。
