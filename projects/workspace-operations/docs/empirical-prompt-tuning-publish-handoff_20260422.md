# empirical-prompt-tuning publish record

## 1. 目的

branch publish と PR 作成まで完了した時点の状態を、後から追えるように残す。

## 2. 公開状態

- branch: `codex/empirical-prompt-tuning-rollout`
- commit 1: `9851a2c` `[AI] Add empirical prompt tuning protocol`
- commit 2: `d5b6683` `[AI] Add empirical prompt tuning rollout records`
- commit 3: `734a75f` `[AI] Add publish handoff for empirical prompt tuning`
- remote: `origin https://github.com/ezomushroom-spec/toolkit.git`
- PR: `https://github.com/ezomushroom-spec/toolkit/pull/2`

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

## 5. ここから先にやること

1. PR review を進める
2. 必要なら fix commit をこの branch に積む
3. ready for review へ切り替えるか判断する
4. 必要なら別件差分は別 branch で扱う

## 6. 注意点

worktree には未反映の unrelated diff がまだ残っている。

そのため、追加修正を積む前に `git status --short` を再確認し、この branch と無関係な差分を巻き込まないこと。
