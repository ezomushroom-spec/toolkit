# empirical-prompt-tuning PR record

## タイトル

`Introduce empirical prompt tuning rollout for workspace skills`

## 概要

- `empirical-prompt-tuning` を workspace 向けの評価・改訂 protocol として追加
- 既存 skill 群への初回 rollout と主要 2nd iteration の記録を追加
- `AGENTS.md` 主要節への trial、result 保管方針、運用ルール、外部反映計画を文書化

## 変更内容

### protocol 本体

- 新しい `empirical-prompt-tuning` skill を追加
- `project-scaffolder`、`desktop-dnd-path-resolution`、`windows-batch-launcher`、`subagent-debug-review` を最小改訂
- root `AGENTS.md` の委任解釈を 1 行補強

### rollout records

- `Critical`、`Important`、`Opportunistic` の初回 trial 記録を追加
- `windows-batch-launcher`、`desktop-dnd-path-resolution`、`subagent-debug-review` の 2nd iteration 記録を追加
- `AGENTS.md` 主要 section の trial 記録を追加
- operating rule、result storage policy、finish list、external reflection plan、staging manifest を追加

## レビュー観点

- `empirical-prompt-tuning` の位置づけが「置き換え」ではなく「評価 protocol」になっているか
- 既存 skill の最小改訂が過剰な template 化になっていないか
- result log を個別文書正本にした方針が妥当か
- `AGENTS.md` section trial の一区切り判断が妥当か

## 公開状態

- PR: `https://github.com/ezomushroom-spec/toolkit/pull/2`
- 状態: draft
- base branch: `master`
- head branch: `codex/empirical-prompt-tuning-rollout`
- この文書は、実際に作成した PR のタイトルと本文の記録として残す

## 補足

- worktree には別件の未反映差分が残っているが、この PR の commit には含めていない
