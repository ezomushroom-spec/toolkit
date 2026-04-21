# empirical-prompt-tuning trial result

## Target

- Target: `windows-batch-launcher`
- Canonical file: `E:\codex\workspace\.agents\skills\windows-batch-launcher\SKILL.md`
- Evaluation date: 2026-04-22
- Iteration: `2nd`
- Executor separation: empirical
- Revision theme: install boundary と version-pinned Python fallback の明確化

## Scenario A: install boundary

- Request summary: `node_modules` が無い初回状態で install を自動実行するかどうかの境界を持つ launcher を作る
- Fixture path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\windows-batch-launcher-install-boundary`
- Success: △
- Failed `[critical]` items: なし
- Precision: 3 / 4 = 75%
- Tool usage: 利用メタデータはこの subagent surface では取得できず未記録
- Duration: 利用メタデータはこの subagent surface では取得できず未記録
- Retry count: 自己申告なし

Checklist review:

- [critical] install を自動実行するかどうかの判断を明示する: ○
- silent failure を避ける visible failure path がある: ○
- ASCII-safe な batch を保つ: ○
- debug launcher で原因追跡ができる: ○

Observed ambiguity:

- executor は end-user double-click launcher でも `npm install` 自動実行を選んだ
- 初回 trial で残っていた install 境界の裁量余地が実際に再現した

Discretion completion by executor:

- 利用者の迷いを減らすことを優先して bootstrap launcher として振る舞わせた

Revision taken:

- skill 本文へ、developer bootstrapper と end-user / distributed launcher の install 境界を明示した
- 明示許可がない場合は visible failure で止める方向を補足した

## Scenario B: broken venv fallback

- Request summary: 壊れた `.venv` を飛ばし、broad selector を盲信せず安全な Python fallback を行う
- Fixture path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\windows-batch-launcher-broken-venv`
- Success: ○
- Failed `[critical]` items: なし
- Precision: 4 / 4 = 100%
- Tool usage: 利用メタデータはこの subagent surface では取得できず未記録
- Duration: 利用メタデータはこの subagent surface では取得できず未記録
- Retry count: 自己申告なし

Checklist review:

- [critical] broad selector を盲信しない: ○
- broken `.venv` を検知して次候補へ進む判断がある: ○
- log に実 interpreter path と exit code が残る: ○
- fallback を広げすぎず、失敗理由が見える: ○

Observed ambiguity:

- `.venv` と `venv` の実体判定方法は fixture 特有だが、candidate の試行順と log 方針は安定している

Discretion completion by executor:

- local interpreter 候補を先に probe し、そこで落ちた後に `py -3.10` へ進んだ

Revision taken:

- skill 本文へ、version-pinned `py -x.y` は local interpreter 候補を probed or ruled out した後に使うことを補足した

## Overall result

- install boundary では裁量差が再現し、本文補強の価値があった
- broken `.venv` fallback は安定して通った
- この 2nd iteration により、launcher 種別ごとの install 境界と Python fallback 順が初回より明確になった
