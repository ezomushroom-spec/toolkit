# Workspace Reorg Current State

## 現状確認

### 対象

- workspace root: `E:\codex\workspace`
- 対象フォルダ: `.agents` / `.codex` / `docs` / `projects` / `archive`
- 今回は実装コード、依存関係、ビルド設定は対象外

### 現在の大枠

- root には workspace 共通ルール `AGENTS.md` がある
- 共通文書は `docs` にまとまっている
- skill は `.agents/skills` にまとまっている
- Codex agent 定義は `.codex/agents` にまとまっている
- project 群は `projects` にまとまっている
- `archive` は立ち上がっており、backup 退避先と参照入口が入り始めている

### 良い点

- workspace 共通ルールと project 群の置き場は大きく崩れていない
- `.agents` と `.codex` は用途が分かれている
- `docs` に workflow、coding rules、UI 原則、quality gates、template があり、共通文書の土台がある
- `projects/agents-governance-audit` があり、運用監査メモの置き場を分けられている

### 問題点

#### 1. project 入口文書は改善中だが、まだ標準化の途中

- `START_HERE.md` は主要 project に入りつつある
- ただし `AGENTS.md` の有無や粒度は project ごとの差が残りやすい
- `README.md` を入口に使う project との役割分担は継続して明文化が必要

#### 2. active と backup の境界整理は着手済みだが、運用定着はこれから

- backup 名フォルダ 2 件は `archive/projects-backups/` へ移動済み
- ただし、active project 内に backup 群を残している案件があり、入口文書で参照専用と明示しないと誤認しやすい
- 今後の backup を最初からどこへ置くか、命名と生成手順をどう統一するかは未決

#### 3. `docs` のテンプレート分離は進んだが、参考文書の整理は残る

- `docs/templates/` 新設でテンプレート 3 本は分離済み
- 一方で参考文書や補助文書の区分けは未完了で、将来増えると探しにくさが戻る

#### 4. root `AGENTS.md` は維持可能だが、今後の肥大化余地がある

- 現時点では破綻していない
- ただし品質ルール、実装前診断、サブエージェント運用が積み上がっており、追加を続けると詳細が root に戻りやすい

#### 5. `archive` の責務は立ち上がったが、まだ初期段階

- `archive/START_HERE.md` と `docs/archive-boundaries.md` を追加し、backup 2 件を移動済み
- ただし retired project や参照専用 docs の扱いはこれから決める

### project 入口文書の確認結果

| project | AGENTS.md | START_HERE / PROJECT_BRIEF / README | 補足 |
| --- | --- | --- | --- |
| agents-governance-audit | あり | START_HERE あり | 調査案件フォルダ |
| app-sample | あり | START_HERE あり | 入口整備済み |
| launcher-v2-remake | あり | START_HERE あり | 入口整備済み |
| mosaic-remake | あり | START_HERE あり | 入口整備済み |
| mosaic-remake-winui | あり | START_HERE / README あり | 入口整備済み |
| post-manager-remake | あり | START_HERE あり | 入口整備済み |
| skill-prompt-clipboard | あり | START_HERE / README あり | 入口整備済み |

### 現時点の判断

- 入口文書の整備は前進しており、不足していた active project の `AGENTS.md` も補完済み
- 引き続き大規模な一括再配置は避け、基準が固まった単位だけを動かす方針が妥当
- 次は active project 内に残る backup 群の整理と、`docs` 内の参考文書区分けを優先する価値が高い

## 採用判断

- 今回の優先着手は「全面再配置」ではなく「再編前提の棚卸しと方針固定」だった
- 次段として、入口文書の標準形と active / archive の運用基準を反映し、backup 2 件の移動まで適用した

## 未決事項

- 今後の backup を生成時点で `archive/projects-backups/` に置くか
- project 入口文書を `START_HERE.md` へ事実上統一してよいか
- `docs` を `guides` / `templates` などへ段階分割するか、まだ root 配下で維持するか
