# Docs Index

`docs/` 配下の役割を迷わず辿るための入口。
workspace 共通ルール、運用ルール、template、改善メモの置き場所を簡潔にまとめる。

## 0. 最初の読み順

初見では、まず次の順で読む。

1. [../AGENTS.md](/E:/codex/workspace/AGENTS.md)
2. [workflow.md](/E:/codex/workspace/docs/workflow.md)
3. [quality-gates.md](/E:/codex/workspace/docs/quality-gates.md)
4. 必要に応じて目的別ガイドや template を読む

役割は次のとおり。

- `AGENTS.md`: 何を優先し、何を避けるか
- `workflow.md`: どう進めるか
- `quality-gates.md`: 何をもって完了とするか

## 0.5 迷ったときの参照先

迷った内容ごとに、まず見る先を固定する。

- 何を優先するか迷う: [../AGENTS.md](/E:/codex/workspace/AGENTS.md)
- どの順で進めるか迷う: [workflow.md](/E:/codex/workspace/docs/workflow.md)
- 完了扱いにしてよいか迷う: [quality-gates.md](/E:/codex/workspace/docs/quality-gates.md)
- docs をどこまで更新するか迷う: [documentation-update-rules.md](/E:/codex/workspace/docs/documentation-update-rules.md)
- skill の使い分けで迷う: [subagent-prompts.md](/E:/codex/workspace/docs/subagent-prompts.md)
- skill の棚卸し結果や整理方針を見たい: [skill-inventory.md](/E:/codex/workspace/docs/skill-inventory.md)
- active 案件の入口一覧を見たい: [projects-index.md](/E:/codex/workspace/docs/projects-index.md)
- 公開向けにこの workspace の位置づけを知りたい: [public-workspace-overview.md](/E:/codex/workspace/docs/public-workspace-overview.md)

## 1. 最初に読むもの

- [../AGENTS.md](/E:/codex/workspace/AGENTS.md): workspace 共通ルールと作業前提
- [workflow.md](/E:/codex/workspace/docs/workflow.md): 着手条件から完了判定までの実運用フロー
- [quality-gates.md](/E:/codex/workspace/docs/quality-gates.md): 完了報告と確認観点
- [documentation-update-rules.md](/E:/codex/workspace/docs/documentation-update-rules.md): docs 更新の判断基準

## 2. 目的別ガイド

- [public-workspace-overview.md](/E:/codex/workspace/docs/public-workspace-overview.md): 公開版として何を含み、何を意図している workspace か
- [archive-boundaries.md](/E:/codex/workspace/docs/archive-boundaries.md): active / backup / archive の境界整理
- [coding-rules.md](/E:/codex/workspace/docs/coding-rules.md): 実装時の基本ルール
- [ui-principles.md](/E:/codex/workspace/docs/ui-principles.md): UI 改善時の優先原則
- [subagent-prompts.md](/E:/codex/workspace/docs/subagent-prompts.md): skill / subagent の使い分け早見表
- [skill-inventory.md](/E:/codex/workspace/docs/skill-inventory.md): skill 群の棚卸し結果と整理方針
- [template-extraction-boundary.md](/E:/codex/workspace/docs/template-extraction-boundary.md): template 化の切り分け基準
- [effectiveness-measurement-prep.md](/E:/codex/workspace/docs/effectiveness-measurement-prep.md): 実効性計測の前段整理
- [workspace-improvement-proposals_20260402.md](/E:/codex/workspace/docs/workspace-improvement-proposals_20260402.md): 今後の改善候補

## 2.1 案件一覧

- [projects-index.md](/E:/codex/workspace/docs/projects-index.md): 現在の project 入口一覧

## 2.2 作業の型

- 進め方を確認する: [workflow.md](/E:/codex/workspace/docs/workflow.md)
- 完了条件を確認する: [quality-gates.md](/E:/codex/workspace/docs/quality-gates.md)
- 迷ったら入口一覧を見る: [projects-index.md](/E:/codex/workspace/docs/projects-index.md)

## 3. テンプレート

- [templates/implementation-plan-template.md](/E:/codex/workspace/docs/templates/implementation-plan-template.md): 中規模以上の実装計画
- [templates/pre-implementation-decision.template.md](/E:/codex/workspace/docs/templates/pre-implementation-decision.template.md): 実装前判断メモ
- [templates/current-state-check.template.md](/E:/codex/workspace/docs/templates/current-state-check.template.md): 現状確認メモ
- [templates/project-AGENTS.template.md](/E:/codex/workspace/docs/templates/project-AGENTS.template.md): project `AGENTS.md`
- [templates/START_HERE.template.md](/E:/codex/workspace/docs/templates/START_HERE.template.md): `START_HERE.md`
- [templates/PROJECT_SUMMARY.template.md](/E:/codex/workspace/docs/templates/PROJECT_SUMMARY.template.md): `PROJECT_SUMMARY.md`

## 4. 文書の置き分け

- workspace 共通ルールは `docs/` または root `AGENTS.md`
- project 固有の入口は `projects/<name>/AGENTS.md`、`START_HERE.md`、`PROJECT_SUMMARY.md`
- project 固有の現状確認、採用判断、未決事項は `projects/<name>/docs/`
- docs-only / audit-only project では、監査メモや判断文書を project 直下に置いてよい

## 5. docs-only / audit-only project の扱い

コード実装が主目的でない project でも、入口文書は揃えてよい。

- `AGENTS.md`: 調査対象、参照境界、更新対象を短く書く
- `START_HERE.md`: 読み順と最初に見るメモを書く
- `PROJECT_SUMMARY.md`: project の目的、正本文書、参照先をまとめる

この場合、build / run / test は無理に埋めず、`文書確認の観点` や `監査対象` を主に書く。

## 6. 補足

- template は本文をそのまま埋めるより、案件に合わせて不要項目を削る
- 文書を増やすより、読む先、実装先、更新先を迷わないことを優先する
