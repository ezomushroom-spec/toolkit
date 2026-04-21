# empirical-prompt-tuning 外部反映計画

## 1. 目的

今回の `empirical-prompt-tuning` 導入差分を、どの単位で commit / PR に切るかを決める。

## 2. 前提

現在の worktree には、今回の導入差分以外の変更や未追跡物も混在している。

そのため、外部反映では「workspace 全体の差分をそのまま 1 回で出す」方式を取らない。

## 3. 推奨する切り方

### 1 本目: protocol 導入本体

次を 1 本目の commit / PR 候補にする。

- `.agents/skills/empirical-prompt-tuning/`
- 既存 skill の最小改訂
- `docs/skill-inventory.md`
- `docs/subagent-prompts.md`
- `AGENTS.md` の最小補強

この束は「protocol の追加と、明白な整合修正」に限定する。

### 2 本目: workspace-operations 文書群

次を 2 本目の commit / PR 候補にする。

- `projects/workspace-operations/docs/empirical-prompt-tuning-*.md`
- `projects/workspace-operations/PROJECT_SUMMARY.md`
- `projects/workspace-operations/START_HERE.md`

この束は「導入記録、trial 記録、運用ルール、未決整理」に限定する。

## 4. 今回は分ける理由

### A. レビュー観点が違う

skill 本体の追加・改訂と、運用記録文書の大量追加では、見るべき論点が違う。

### B. 戻し方が明確になる

もし文書運用だけ差し戻したくなっても、protocol 本体を巻き戻さずに扱いやすい。

### C. 既存の unrelated diff と切り分けやすい

workspace には別件の project や docs 差分も残っているため、最小の意味単位に切ったほうが安全である。

## 5. 今回 commit に含めないもの

次は今回の protocol 反映 commit に自動では含めない。

- 別件 project の新規追加
- `docs/projects-index.md` など今回と無関係な未追跡文書
- 既存の archive / migration 系差分
- protocol と無関係な config 変更

## 6. 例外理由と戻し方

今回の外部反映では、「workspace 全差分を一括反映しない」こと自体を例外ではなく安全策として扱う。

戻し方は次の通り。

1. protocol 本体だけ戻したい場合は 1 本目だけを戻す
2. trial 記録や運用文書だけ戻したい場合は 2 本目だけを戻す

## 7. 今の推奨

次に外部反映へ進めるなら、まず今回差分の中から protocol 本体だけを staging 対象として明示し、その後に workspace-operations 文書群を別束で扱う。
