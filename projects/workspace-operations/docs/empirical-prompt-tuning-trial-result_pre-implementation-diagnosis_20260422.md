# empirical-prompt-tuning trial result

## Target

- Target: `pre-implementation-diagnosis`
- Canonical file: `E:\codex\workspace\.agents\skills\pre-implementation-diagnosis\SKILL.md`
- Evaluation date: 2026-04-22
- Executor separation: empirical

## Scenario A: 実装方式比較

- Request summary: Python 資産を活かしつつ UI を改善する構成比較を行う
- Success: ○
- Failed `[critical]` items: なし
- Precision: 4 / 4 = 100%
- Tool usage: 利用メタデータはこの subagent surface では取得できず未記録
- Duration: 利用メタデータはこの subagent surface では取得できず未記録
- Retry count: 自己申告なし

Checklist review:

- [critical] 2〜3 の現実的な候補に絞る: ○
- Python 資産を core / backend として維持する案を比較に含める: ○
- 推奨案だけでなく見送る案の理由を出す: ○
- 診断のあとすぐ coding へ飛ばない: ○

Observed ambiguity:

- `shell` の具体技術までは確定せず、必要時のみ追加確認に回している

Discretion completion by executor:

- 候補を A / B / C の 3 本に絞り、Python core を守る案を推奨した

Next revision theme:

- 目立った failure はなく、必須改訂なし

## Scenario B: 単純 patch

- Request summary: 保存ボタン文言だけの修正で diagnosis を適用すべきかを判断する
- Success: ○
- Failed `[critical]` items: なし
- Precision: 3 / 3 = 100%
- Tool usage: 利用メタデータはこの subagent surface では取得できず未記録
- Duration: 利用メタデータはこの subagent surface では取得できず未記録
- Retry count: 自己申告なし

Checklist review:

- [critical] 実装前診断を過剰適用しない: ○
- 小規模 patch として扱う: ○
- architecture choice へ膨らませない: ○

Observed ambiguity:

- なし

Discretion completion by executor:

- `No architecture change` という文脈を根拠に、適用不要と明確に切った

Next revision theme:

- 目立った failure はなく、必須改訂なし

## Overall result

- 両 scenario とも成功
- この skill は `比較が必要な案件では 2〜3 案に絞る` と `単純 patch には適用しない` の両方を満たした
- 次の対象へ進んでよい
