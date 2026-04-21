# empirical-prompt-tuning 2nd iteration 準備

## 1. 対象

- Target: `desktop-dnd-path-resolution`
- Canonical file: `E:\codex\workspace\.agents\skills\desktop-dnd-path-resolution\SKILL.md`
- Iteration theme: mixed drop と repeated failure の扱いの明確化

## 2. この iteration で見たいこと

- browser で mixed drop が来たときに、support 範囲外として安全に扱えるか
- image file を parent folder へ寄せる条件をどこまで狭く読むか
- repeated failure 時に既存 valid value を守りつつ warning 抑制できるか
- invalid path のたびに picker を開かない判断が出るか

## 3. 固定 scenario

### Scenario A: mixed browser drop

- Case type: `edge`
- Fixture path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\desktop-dnd-mixed-browser`
- User-like request:

```text
通常ブラウザで使う drop zone です。画像と無関係ファイルの mixed drop が来ても既存 path を壊したくありません。fallback と warning の扱いを整理してください。
```

Checklist:

- [critical] browser では D&D を supplemental として扱う
- mixed drop と path 不明時でも既存 valid path を保持する
- browse dialog などの次行動を案内する
- repeated warning の抑制に触れる

### Scenario B: repeated shell failure

- Case type: `edge`
- Fixture path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\desktop-dnd-repeated-shell-failure`
- User-like request:

```text
desktop shell では drag and drop を主入力にしたいです。ただ、画像ファイルを毎回 parent folder に寄せるのが危ないケースがあります。repeated failure を増やさずに扱う方針を整理してください。
```

Checklist:

- [critical] desktop shell では D&D を primary input として扱う
- image file を parent folder へ寄せる条件付き判断に触れる
- invalid parent folder では既存 valid value を保持する
- repeated failure で同じ warning を増やしすぎない
- invalid な限り不要 picker を毎回開かない

## 4. fresh executor へ渡す prompt ひな形

### Prompt A

```text
日本語で回答してください。
Use the skill `desktop-dnd-path-resolution` at `E:\codex\workspace\.agents\skills\desktop-dnd-path-resolution\SKILL.md`.

Read `E:\codex\workspace\projects\workspace-operations\trial-fixtures\desktop-dnd-mixed-browser\screen.md`.
Produce a practical path-handling direction before coding.
```

### Prompt B

```text
日本語で回答してください。
Use the skill `desktop-dnd-path-resolution` at `E:\codex\workspace\.agents\skills\desktop-dnd-path-resolution\SKILL.md`.

Read `E:\codex\workspace\projects\workspace-operations\trial-fixtures\desktop-dnd-repeated-shell-failure\screen.md`.
Produce a practical path-handling direction before coding.
```
