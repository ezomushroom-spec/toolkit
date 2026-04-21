# empirical-prompt-tuning trial result

## Target

- Target: `ui-overlap-guard`
- Canonical file: `E:\codex\workspace\.agents\skills\ui-overlap-guard\SKILL.md`
- Evaluation date: 2026-04-22
- Executor separation: empirical

## Scenario A: tab row and list collision

- Request summary: chip row と一覧の境界、scrollbar collision、sticky row 近接を防ぐ方針を出す
- Fixture path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\ui-overlap-guard-tab-list`
- Success: ○
- Failed `[critical]` items: なし
- Precision: 4 / 4 = 100%
- Tool usage: 利用メタデータはこの subagent surface では取得できず未記録
- Duration: 利用メタデータはこの subagent surface では取得できず未記録
- Retry count: 自己申告なし

Checklist review:

- [critical] fixed row と scrollable content の分離に触れる: ○
- wrapping や scrollbar collision の防止策が出る: ○
- narrow width 再確認に触れる: ○
- verification points が operability 中心になる: ○

Observed ambiguity:

- `一行のまま収める` と `必要に応じて横スクロール` の表現差はあるが、unsafe wrapping を避ける方向は一貫している

Discretion completion by executor:

- sticky row と first card の安全距離、focus / active 状態での高さ保持まで含めて構造保護へ寄せた

Next revision theme:

- 目立った failure はなく、必須改訂なし

## Scenario B: sidebar multi-scroll

- Request summary: sidebar 内の複数 scroll owner、crushed controls、focus overlap を防ぐ方針を出す
- Fixture path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\ui-overlap-guard-sidebar-scroll`
- Success: ○
- Failed `[critical]` items: なし
- Precision: 4 / 4 = 100%
- Tool usage: 利用メタデータはこの subagent surface では取得できず未記録
- Duration: 利用メタデータはこの subagent surface では取得できず未記録
- Retry count: 自己申告なし

Checklist review:

- [critical] scroll owner の整理が出る: ○
- labels / controls の crushed state を structural issue として扱う: ○
- focus / active state の重なりに触れる: ○
- cosmetic tweak に逃げない: ○

Observed ambiguity:

- `scroll owner を一本化` と `fixed header + scroll body へ分ける` の細部は実装依存だが、複数近接 scroll owner を避ける方向は安定している

Discretion completion by executor:

- section 境界の明示、stable gutter、minimum height、narrow width 時の unsafe wrapping 回避を一貫して出した

Next revision theme:

- 目立った failure はなく、必須改訂なし

## Overall result

- overlap, clipping, crushed controls, scroll interference を cosmetic でなく structural requirement として扱えている
- `Opportunistic` 群の 2 件目として通過してよい
