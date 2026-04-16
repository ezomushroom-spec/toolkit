# Template Extraction Boundary

この文書は、現在の workspace から「ドメイン中立で切り出せる骨格」と「この workspace 固有として残すべき要素」を分けるための基準をまとめる。

目的は、将来的に `workspace-template` のような雛形を作るとき、何を残し、何を外し、何を可変項目にするかを先に固定することにある。

## 1. 判定基準

各文書、rule、skill は次の 3 区分で見る。

- `中立`: そのまま別ドメインへ持っていける
- `可変`: 骨格は残すが、利用ドメインに応じて差し替える
- `固有`: この workspace の運用文脈に強く依存する

判断基準は次のとおり。

- 特定技術、特定 UI 形態、特定プロダクトカテゴリに依存していないか
- 個別案件の失敗経験に根ざしていても、別ドメインで同じ失敗を防げるか
- デスクトップ、Web、データ処理、docs-only のいずれに移しても意味を保つか
- ルールより例示や具体技術名が先に立っていないか

## 2. 文書の切り分け

### 2.1 そのまま中立で残せる

- [workflow.md](/E:/codex/workspace/docs/workflow.md)
- [quality-gates.md](/E:/codex/workspace/docs/quality-gates.md)
- [documentation-update-rules.md](/E:/codex/workspace/docs/documentation-update-rules.md)
- [archive-boundaries.md](/E:/codex/workspace/docs/archive-boundaries.md)
- [skill-inventory.md](/E:/codex/workspace/docs/skill-inventory.md)
- `docs/templates/*`

理由:

- いずれも「どう進めるか」「何をもって完了とするか」「文書をどう管理するか」を扱っており、個別技術より運用構造が中心

### 2.2 骨格は残すが可変にする

- [AGENTS.md](/E:/codex/workspace/AGENTS.md)
- [coding-rules.md](/E:/codex/workspace/docs/coding-rules.md)
- [ui-principles.md](/E:/codex/workspace/docs/ui-principles.md)
- [subagent-prompts.md](/E:/codex/workspace/docs/subagent-prompts.md)

理由:

- 中核の思想は中立だが、現状はデスクトップ GUI、ローカル運用、画像系ツール、Electron / Tauri、D&D などに寄った記述が残る
- template 化するときは、可変セクションとして差し替えられる形にする

可変項目の例:

- UI 安全性をどこまで強く見るか
- デスクトップ中心か Web 中心か
- バッチ処理を標準論点に入れるか
- GPU / 長時間処理 / 常駐監視を標準確認に含めるか
- subagent の使用条件やモデル方針

### 2.3 この workspace 固有として残す

- [workspace-improvement-proposals_20260402.md](/E:/codex/workspace/docs/workspace-improvement-proposals_20260402.md)
- project 文脈に近い補足メモ
- 今後の個別改善履歴や棚卸し時の個別判断メモ

理由:

- 雛形ではなく、現在の workspace の改善履歴と判断経緯そのものだから

## 3. skill の切り分け

### 3.1 テンプレートの基幹 skill 候補

次は `workspace-template` へ持っていきやすい。

- `request-translate`
- `pre-implementation-diagnosis`
- `implementation-planner`
- `plan-review`
- `code-review`

理由:

- 依頼整理、方式比較、計画、レビューという汎用フローに対応している

### 3.2 可変枠として残す skill

- `ui-audit`
- `ui-design-direction`
- `ui-remake-safe`
- `ui-overlap-guard`
- `subagent-debug-review`
- `desktop-dnd-path-resolution`
- `windows-batch-launcher`

理由:

- 有用だが、対象ドメインや環境に応じて要不要が変わる

template 側では次のような扱いがよい。

- UI を重視する構成では採用
- データ処理中心や docs-only では外す
- Windows 依存 skill はオプション扱いにする

### 3.3 この workspace 固有として残す skill

- `image-finishing-tool-design`
- project 特化 skill 群
- home 側の remake / boundary / maintainer 系 skill 群
- plugin skill 群

理由:

- 画像仕上げツール、特定 project、特定実装スタック、特定外部サービスに依存する

## 4. template 化するときの構成案

最小構成は次を想定する。

```text
workspace-template/
├── AGENTS.md
├── docs/
│   ├── README.md
│   ├── workflow.md
│   ├── quality-gates.md
│   ├── documentation-update-rules.md
│   ├── archive-boundaries.md
│   └── templates/
│       ├── implementation-plan-template.md
│       ├── pre-implementation-decision.template.md
│       ├── current-state-check.template.md
│       ├── project-AGENTS.template.md
│       ├── START_HERE.template.md
│       └── PROJECT_SUMMARY.template.md
└── .agents/
    └── skills/
        ├── request-translate/
        ├── pre-implementation-diagnosis/
        ├── implementation-planner/
        ├── plan-review/
        └── code-review/
```

## 5. template 側で可変にしたい項目

雛形では、次をプレースホルダーとして持つと移植しやすい。

- この workspace が主に扱う対象
  - desktop app / web app / data pipeline / docs-only など
- UI の重要度
  - 高 / 中 / 低
- バッチ処理の重要度
  - 高 / 中 / 低
- 高リスク操作の代表例
- 標準で見るべき資源観点
  - memory / GPU / network / long-running jobs
- subagent 利用方針
  - 許可条件 / 推奨モデル / 推奨役割

## 6. 切り出しの順番

実際に template 化するときは、次の順で進める。

1. `AGENTS.md` の中立部分と可変部分を分ける
2. `workflow.md` と `quality-gates.md` をそのまま持っていく
3. `docs/templates/*` をそのまま持っていく
4. 基幹 skill 5 本だけを先に切り出す
5. UI 系や環境依存 skill は後からオプションとして追加する

## 7. 今回時点の結論

- 骨格の中立性は高い
- ただし `AGENTS.md` と一部 UI / 環境系ルールは可変層として扱うべき
- template 化は十分可能だが、まずは「中立」「可変」「固有」の境界を守ることを優先する
