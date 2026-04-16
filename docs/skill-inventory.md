# Skill Inventory

この文書は、現在この workspace から参照可能な skill 群を俯瞰し、重複、近接、特化、棚卸し優先度を整理するための棚卸し結果である。

## 1. 対象範囲

今回の棚卸し対象は次の 3 系統。

- workspace 固有 skill: `E:\codex\workspace\.agents\skills`
- home 側 skill: `C:\Users\ezomu\.codex\skills`
- plugin skill: `C:\Users\ezomu\.codex\plugins\cache\...\SKILL.md`

件数は次のとおり。

- workspace: 15
- home: 28
- plugin: 7
- 合計: 52

## 2. 棚卸し方針

今回は削除や統合を先に行わず、まず次で分類する。

- `基幹`: workspace の標準導線で繰り返し使う
- `補助`: 特定論点を補強する
- `特化`: 特定製品、画面、project に強く依存する
- `環境依存`: OS、shell、起動、D&D など特定環境向け

棚卸し判定は次の 4 区分で付ける。

- `維持`
- `要説明強化`
- `特化維持`
- `統合見送り`

## 3. 棚卸し結果

### 3.1 workspace 基幹 skill

#### 維持

- `request-translate`
- `pre-implementation-diagnosis`
- `implementation-planner`
- `plan-review`
- `code-review`

判断:

- workspace の標準導線として役割が明確
- 依頼整理 → 診断 → 計画 → レビュー の段階が崩れていない
- 統合すると逆に入口が曖昧になるため統合見送り

### 3.2 workspace UI 系

#### 維持

- `ui-audit`
- `ui-design-direction`
- `ui-remake-safe`
- `ui-overlap-guard`

#### 補助として維持

- `image-finishing-tool-design`
- `project-safety-snapshot`

判断:

- `ui-audit`: 問題診断
- `ui-design-direction`: 方向決めと業種適合の補正
- `ui-remake-safe`: 壊さず実装改善と overlap / scroll 干渉の防止
- `ui-overlap-guard`: 密レイアウト事故防止
- `image-finishing-tool-design`: 画像仕上げツール専用補正
- `project-safety-snapshot`: 高リスク変更前の軽量退避

結論:

- 近接はあるが、役割は分かれている
- `ui-domain-fit-guard` は `ui-design-direction` に統合済み
- `ui-overlap-guard` は残すが、`ui-remake-safe` に主要観点を吸収済み
- 棚卸し判定は `統合見送り`

### 3.3 workspace 環境依存 skill

#### 維持

- `desktop-dnd-path-resolution`
- `windows-batch-launcher`
- `project-scaffolder`

#### 削除

- `python-web-electron-shell-migrator`

判断:

- いずれも OS、shell、アーキテクチャ差に依存し、一般 skill に吸収しにくい
- 実案件で使いどころが明確
- `project-scaffolder` は template 初期化を安定させる workspace 固有の省力化 skill として維持する
- ただし `python-web-electron-shell-migrator` は用途が極めて限定的なため削除し、知見は `pre-implementation-diagnosis` と project 文脈へ吸収する

### 3.4 workspace 不具合/レビュー系

#### 維持

- `subagent-debug-review`

判断:

- `code-review` より重いケースに限定されていて、完全重複ではない
- ただし名前だけでは使い分けが伝わりにくいため、将来 `要説明強化` 候補

### 3.5 home 側の汎用 UI / 設計 / テスト系

#### 維持

- `ui-design-system`
- `run-e2e-tests`
- `run-integration-tests`
- `run-pre-commit-checks`
- `run-smoke-tests`
- `cross-platform-paths`
- `settings-precedence`
- `debug-failing-test`

#### 要説明強化

- `ui-design-system`

判断:

- `ui-design-system` は component 選定や実装パターンに強く、workspace の UI skill と完全重複ではない
- ただし UI 系 skill が増えたため、`ui-design-direction` や `ui-audit` との差を入口文書側で意識する必要がある

### 3.6 home 側の診断 / remaking / boundary 系

#### 特化維持

- `desktop-remake-vs-migration-diagnosis`
- `legacy-app-remake-planner`
- `local-inference-app-boundary-review`
- `python-core-winui-preview-bridge`
- `read-only-canonical-overlay-apps`
- `review-layout-safe-winui`
- `launcher-ui-remake-safe`

#### 要説明強化

- `desktop-remake-vs-migration-diagnosis`
- `legacy-app-remake-planner`
- `local-inference-app-boundary-review`

判断:

- いずれも一般論ではなく、特定の remake 文脈や boundary 判断に強い
- 価値は高いが、名前だけでは近さが分かりにくい
- 削除や統合はせず、必要時に project 文脈から呼ぶ前提で残す

### 3.7 home 側の project 特化 / 業務特化 skill

#### 特化維持

- `pixiv-tool-workspace-maintainer`
- `post-manager-maintainer`
- `template-thumbnail-composer-maintainer`
- `python-manager-discovery`
- `windows-pyinstaller-desktop-maintainer`
- `windows-pyside-launch-troubleshooting`
- `windows-python-gui-repo-triage`
- `eagle-friendly-image-dnd`
- `generate-snapshot`
- `workspace-delegation-orchestrator`
- `playwright`
- `ComfyUI-to-Python-Extension-Skill`

判断:

- project 特化や技術特化のため、無理に一般化しない
- 特化 skill は「残す前提」で、入口側だけ整理する

### 3.8 plugin skill

#### 維持

- `frontend-skill`
- `web-design-guidelines`
- `react-best-practices`
- `shadcn`
- `deploy-to-vercel`
- `stripe-best-practices`
- `supabase-postgres-best-practices`

判断:

- plugin skill は web 実装や外部サービス統合の補助であり、workspace 固有 skill とは役割が違う
- plugin 側の skill は削除対象ではなく、必要時に優先して使う

## 4. 今回の棚卸し結論

### 4.1 今すぐ統合すべき skill

- `ui-domain-fit-guard` → `ui-design-direction` に統合済み

理由:

- 近接は多いが、役割重複よりも「入口の説明不足」が主因
- ただし `ui-domain-fit-guard` は方向決め skill に自然に吸収できる範囲だった
- `implementation-brief-builder` は `implementation-planner` の最終出力へ統合した

### 4.2 今すぐ説明強化したい skill 群

- `ui-design-system`
- `subagent-debug-review`
- `desktop-remake-vs-migration-diagnosis`
- `legacy-app-remake-planner`
- `local-inference-app-boundary-review`

理由:

- 価値は高いが、名前だけでは近接 skill との差が見えにくい

### 4.3 入口整理で十分な領域

- workspace UI 系
- workspace 診断 / 計画系

理由:

- すでに `docs/subagent-prompts.md` で分け方を書けば実運用しやすい
- skill 自体を削る段階ではない

### 4.4 特化維持すべき領域

- project 特化 skill
- remake / boundary 系
- OS / shell / launcher 系

理由:

- 汎用化すると価値が落ちる

## 5. 次回棚卸しの発火条件

次のどれかが増えたら、再度棚卸しする。

- 同じ依頼で複数 skill が同じ説明に見える
- skill 名だけでは役割差が伝わらない
- 実案件で trigger が不安定になる
- UI 系 skill がさらに 2 本以上増える
- 特化 skill を基幹 skill と誤用する事例が出る

## 6. 次の実務アクション

今回の棚卸し後に優先するのは次。

1. `docs/subagent-prompts.md` を入口の正本として維持する
2. 追加 skill は「置き換え」か「補助」かを本文に明記する
3. `要説明強化` 判定の skill は、必要時に本文か入口文書で差分説明を足す
4. 統合や削除は、trigger の不安定さが実際に出てから判断する
5. `python-web-electron-shell-migrator` のような極端に限定的な skill は、実案件で使われなくなった時点で削除候補に入れる
