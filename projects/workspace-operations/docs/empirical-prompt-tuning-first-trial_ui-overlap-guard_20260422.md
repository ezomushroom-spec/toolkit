# empirical-prompt-tuning 初回 trial 準備

## 1. 対象

- Target: `ui-overlap-guard`
- Canonical file: `E:\codex\workspace\.agents\skills\ui-overlap-guard\SKILL.md`
- Priority: `Opportunistic`

## 2. この対象を選ぶ理由

- 見た目より前に operability を守る skill として機能するかを確認したい
- overlap, scrollbar collision, crushed control という狭い論点へ安全に絞れるかを見たい
- `ui-remake-safe` と違って、構造事故に集中した出力になるかを評価しやすい

## 3. Iteration 0

- description と body の整合は取れている
- structure -> visual clarity -> safety/state handling の順も明確
- 追加で見たい曖昧さは「scroll owner の決め方」と「wrapping chips を unsafe wrapping のまま許さないか」

## 4. trial fixture

### Fixture A: tab-list

- Path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\ui-overlap-guard-tab-list`
- 想定: chip row, heading, list, horizontal scrollbar が近接しすぎている

### Fixture B: sidebar-scroll

- Path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\ui-overlap-guard-sidebar-scroll`
- 想定: 複数 scroll owner と crushed chips が sidebar の operability を落としている

## 5. 固定 scenario

### Scenario A: tab row and list collision

- Case type: `median`
- User-like request:

```text
この画面で chip row と一覧の境界が危ないです。重なりとスクロール干渉を防ぐ方向で、実装前に整理してください。
```

Checklist:

- [critical] fixed row と scrollable content の分離に触れる
- wrapping や scrollbar collision の防止策が出る
- narrow width 再確認に触れる
- verification points が operability 中心になる

### Scenario B: sidebar multi-scroll

- Case type: `edge`
- User-like request:

```text
sidebar の controls がつぶれていて、scroll も干渉しています。どこを固定し、どこをスクロールさせるべきか整理してください。
```

Checklist:

- [critical] scroll owner の整理が出る
- labels / controls の crushed state を structural issue として扱う
- focus / active state の重なりに触れる
- cosmetic tweak に逃げない

## 6. fresh executor へ渡す prompt ひな形

### Prompt A

```text
日本語で回答してください。
Use the skill `ui-overlap-guard` at `E:\codex\workspace\.agents\skills\ui-overlap-guard\SKILL.md`.

Read `E:\codex\workspace\projects\workspace-operations\trial-fixtures\ui-overlap-guard-tab-list\screen.md`.
Produce a structural overlap-prevention direction before coding.
```

### Prompt B

```text
日本語で回答してください。
Use the skill `ui-overlap-guard` at `E:\codex\workspace\.agents\skills\ui-overlap-guard\SKILL.md`.

Read `E:\codex\workspace\projects\workspace-operations\trial-fixtures\ui-overlap-guard-sidebar-scroll\screen.md`.
Produce a structural overlap-prevention direction before coding.
```
