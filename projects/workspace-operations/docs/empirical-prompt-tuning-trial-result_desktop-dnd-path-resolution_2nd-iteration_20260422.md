# empirical-prompt-tuning trial result

## Target

- Target: `desktop-dnd-path-resolution`
- Canonical file: `E:\codex\workspace\.agents\skills\desktop-dnd-path-resolution\SKILL.md`
- Evaluation date: 2026-04-22
- Iteration: `2nd`
- Executor separation: empirical
- Revision theme: mixed drop と repeated failure の扱いの明確化

## Scenario A: mixed browser drop

- Request summary: browser で mixed drop が来ても既存 valid path を壊さず、warning と fallback を整理する
- Fixture path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\desktop-dnd-mixed-browser`
- Success: ○
- Failed `[critical]` items: なし
- Precision: 4 / 4 = 100%
- Tool usage: 利用メタデータはこの subagent surface では取得できず未記録
- Duration: 利用メタデータはこの subagent surface では取得できず未記録
- Retry count: 自己申告なし

Checklist review:

- [critical] browser では D&D を supplemental として扱う: ○
- mixed drop と path 不明時でも既存 valid path を保持する: ○
- browse dialog などの次行動を案内する: ○
- repeated warning の抑制に触れる: ○

Observed ambiguity:

- mixed drop を「拒否」ではなく「警告付き保留」と読むかは表現差が出るが、安全側の判断として一貫している

Discretion completion by executor:

- browser では path 推測を行わず、現状維持と fallback 案内を優先した

Revision taken:

- 必須改訂なし

## Scenario B: repeated shell failure

- Request summary: desktop shell で parent-folder 寄せが危ないケースを repeated failure を増やさず扱う
- Fixture path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\desktop-dnd-repeated-shell-failure`
- Success: ○
- Failed `[critical]` items: なし
- Precision: 5 / 5 = 100%
- Tool usage: 利用メタデータはこの subagent surface では取得できず未記録
- Duration: 利用メタデータはこの subagent surface では取得できず未記録
- Retry count: 自己申告なし

Checklist review:

- [critical] desktop shell では D&D を primary input として扱う: ○
- image file を parent folder へ寄せる条件付き判断に触れる: ○
- invalid parent folder では既存 valid value を保持する: ○
- repeated failure で同じ warning を増やしすぎない: ○
- invalid な限り不要 picker を毎回開かない: ○

Observed ambiguity:

- 変更候補ファイルの実在確認はしていないが、親フォルダ寄せを条件付きにする意図は安定して出た

Discretion completion by executor:

- `folder workflow に本当に合う場合だけ parent folder へ寄せる` という境界を自然に補完した

Revision taken:

- 必須改訂なし

## Overall result

- mixed drop, repeated failure, parent-folder 条件の 3 点とも安定して通った
- この skill は 2nd iteration でも裁量差が小さく、本文の追加改訂は見送ってよい
