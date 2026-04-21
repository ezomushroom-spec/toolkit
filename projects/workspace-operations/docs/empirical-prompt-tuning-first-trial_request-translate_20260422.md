# empirical-prompt-tuning 初回 trial 準備

## 1. 対象

- Target: `request-translate`
- Canonical file: `E:\codex\workspace\.agents\skills\request-translate\SKILL.md`
- Priority: `Important`

## 2. この対象を選ぶ理由

- 入口の論点整理品質が後段全体に効く
- lightweight fixture で複数ケースを回しやすい

## 3. 固定 scenario

### Scenario A: 複数論点の依頼

- Case type: `median`
- User-like request:

```text
この画面の UI も直したいし、保存失敗もあるし、起動バッチも怪しいです。どこから進めるべきか整理して。
```

Checklist:

- [critical] 論点を分離する
- likely goal と制約を抜く
- 実装に入らず次の段階を示す

### Scenario B: かなり曖昧な依頼

- Case type: `edge`
- User-like request:

```text
なんか全体的に使いにくいのでいい感じにして。
```

Checklist:

- [critical] 不明点を不明のまま見える化する
- 勝手に実装詳細を決めすぎない
- 次の整理ステップへ落とす

## 4. fresh executor へ渡す prompt ひな形

### Prompt A

```text
Use the skill `request-translate` at `E:\codex\workspace\.agents\skills\request-translate` for this task.

Translate this ambiguous multi-topic request into a structured pre-implementation task without writing code:

この画面の UI も直したいし、保存失敗もあるし、起動バッチも怪しいです。どこから進めるべきか整理して。
```

### Prompt B

```text
Use the skill `request-translate` at `E:\codex\workspace\.agents\skills\request-translate` for this task.

Translate this ambiguous request into a structured pre-implementation task without writing code:

なんか全体的に使いにくいのでいい感じにして。
```
