# empirical-prompt-tuning publish handoff

## 1. 目的

remote 未設定の状態でも、次回すぐに push / PR へ進めるための handoff を残す。

## 2. 現在の状態

- branch: `codex/empirical-prompt-tuning-rollout`
- commit 1: `9851a2c` `[AI] Add empirical prompt tuning protocol`
- commit 2: `d5b6683` `[AI] Add empirical prompt tuning rollout records`

## 3. この branch に含まれるもの

### commit 1

- `empirical-prompt-tuning` skill 本体
- 既存 skill 4 件の最小改訂
- `AGENTS.md` の最小補強
- `docs/skill-inventory.md`
- `docs/subagent-prompts.md`

### commit 2

- `workspace-operations` 配下の導入記録
- first / second trial 文書群
- result log 群
- operating rule
- result log storage policy
- `AGENTS.md` trial pause decision
- external reflection plan
- staging manifest

## 4. 今回 branch に含めていないもの

次は intentional に除外している。

- `docs/README.md`
- `docs/quality-gates.md`
- `docs/workflow.md`
- `.codex/config.toml`
- `.codex/agents/python-web-electron-shell-migrator.toml` の移動系差分
- `projects/attendance-manager/` など別件 project 追加

## 5. 次回やること

1. remote を設定する
2. `git push -u <remote> codex/empirical-prompt-tuning-rollout`
3. PR を作る
4. 必要なら別件差分は別 branch で扱う

## 6. 注意点

worktree には未反映の unrelated diff がまだ残っている。

そのため、push 前に `git status --short` を再確認し、この branch の 2 commit 以外を追加で stage しないこと。
