# empirical-prompt-tuning 初回 trial 準備

## 1. 対象

- Target: `pre-implementation-diagnosis`
- Canonical file: `E:\codex\workspace\.agents\skills\pre-implementation-diagnosis\SKILL.md`
- Priority: `Important`

## 2. この対象を選ぶ理由

- 実装前判断の質に大きく効く
- 2〜3 案比較と見送り理由をちゃんと出せるかを見たい
- 単純 patch に誤適用しない抑制も確認したい

## 3. trial fixture

### Fixture A: architecture-choice

- Path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\pre-implementation-diagnosis-architecture`
- 想定: Python 資産がある既存 app を、UI 改善込みで今後どう構成するか比較したい

### Fixture B: narrow-patch

- Path: `E:\codex\workspace\projects\workspace-operations\trial-fixtures\pre-implementation-diagnosis-patch`
- 想定: 単純 patch なので diagnosis を過剰適用しないかをみる

## 4. 固定 scenario

### Scenario A: 実装方式比較

- Case type: `median`
- User-like request:

```text
既存の Python 処理資産を活かしつつ、UI をもっと使いやすくしたいです。
今のまま Python GUI を整えるか、Web UI に分けるか、Shell だけ載せるかを比較して、実装前診断を出してください。
```

Checklist:

- [critical] 2〜3 の現実的な候補に絞る
- Python 資産を core / backend として維持する案を比較に含める
- 推奨案だけでなく見送る案の理由を出す
- 診断のあとすぐ coding へ飛ばない

### Scenario B: 単純 patch

- Case type: `edge`
- User-like request:

```text
保存ボタンの文言だけ直したいです。
```

Checklist:

- [critical] 実装前診断を過剰適用しない
- 小規模 patch として扱う
- architecture choice へ膨らませない

## 5. fresh executor へ渡す prompt ひな形

### Prompt A

```text
Use the skill `pre-implementation-diagnosis` at `E:\codex\workspace\.agents\skills\pre-implementation-diagnosis` for this task.

Work from the artifacts inside `E:\codex\workspace\projects\workspace-operations\trial-fixtures\pre-implementation-diagnosis-architecture`.
Produce a pre-implementation diagnosis before coding.
```

### Prompt B

```text
Use the skill `pre-implementation-diagnosis` at `E:\codex\workspace\.agents\skills\pre-implementation-diagnosis` for this task.

Work from the artifacts inside `E:\codex\workspace\projects\workspace-operations\trial-fixtures\pre-implementation-diagnosis-patch`.
Decide whether a pre-implementation diagnosis is appropriate before coding.
```
