# Workspace 改善提案メモ

更新日: 2026-04-02

## 1. 目的

- `openai/codex` の公開 repo から参考化しやすい運用思想を、この workspace 向けに無理なく移植する。
- 実装案件そのものではなく、workspace 共通の進め方、文書更新、確認導線を強くする。

## 2. 前提

- この workspace は単一 repo ではなく、複数 project を束ねるハブである
- したがって、公開 repo の技術固有ルールをそのまま移すのではなく、`AGENTS.md` を強い運用規約として使う思想を参考にする
- 既存の active / backup / archive 境界、進行フロー、UI 安全性重視の方針は維持する

## 3. 改善案

### 提案 1. project `AGENTS.md` に必須セット作業を書く

現状:

- `projects/<name>/AGENTS.md` は方針や注意点の整理が中心
- `build / run / test` は揃ってきたが、「変更したら何を必ずセットでやるか」までは project ごとにばらつく

提案:

- 次を project `AGENTS.md` に短く明記する
  - 変更したら更新する docs
  - 変更したら確認する起動手順
  - 変更したら最低限見る失敗系

期待効果:

- ルールが判断基準だけでなく行動単位になる
- project ごとの確認漏れを減らせる

### 提案 2. `PROJECT_SUMMARY.md` の正本区分を少し厳密にする

現状:

- `PROJECT_SUMMARY.md` は見通し整理として機能している
- ただし project によっては、正本文書と参照専用文書の境界がやや暗黙

提案:

- 可能なら次を分けて書く
  - 正本コード
  - 正本設定
  - 正本データ
  - 正本文書
  - 参照専用文書

期待効果:

- docs 更新先がさらに明確になる
- 「読む資料」と「更新すべき資料」を混同しにくくなる

### 提案 3. workspace 共通の docs 更新ルールを 1 枚作る

現状:

- `AGENTS.md`、`START_HERE.md`、`PROJECT_SUMMARY.md`、案件 docs の役割はかなり整理された
- ただし「どんな変更でどの文書を更新するか」の横断ルールは、まだ各所に分散している

提案:

- `docs/` 配下に docs 更新ルールを追加し、少なくとも次を整理する
  - どんな変更で docs 更新が必要か
  - `AGENTS.md` / `START_HERE.md` / `PROJECT_SUMMARY.md` / 案件 docs の役割分担
  - 文書更新を後回しにしてよい条件

期待効果:

- 文書更新の迷いを減らせる
- 実装だけ進んで docs が遅れる状態を防ぎやすい

### 提案 4. project ごとの確認コマンドと手順を `AGENTS.md` に寄せる

現状:

- `build / run / test` の入口はかなり揃ってきた
- ただし「どの順で見るか」「失敗時に何を見るか」は project により暗黙

提案:

- project `AGENTS.md` に次を短く書く
  - 推奨確認順
  - 失敗時に先に見るログやファイル
  - 最低限 OK とみなす確認条件

期待効果:

- 確認の再現性が上がる
- 新しいチャットや新しい作業者でも同じ順で追いやすい

### 提案 5. 例外 project の扱いを root docs に明文化する

現状:

- `agents-governance-audit` のような docs-only project も存在する
- 今は入口文書を揃えたが、将来また例外 project が増える可能性がある

提案:

- root docs か `AGENTS.md` に、例外 project の扱いを短く書く
  - docs-only project では実装コード正本を持たなくてよい
  - ただし `START_HERE.md` と `PROJECT_SUMMARY.md` は維持する
  - `AGENTS.md` は簡略版でもよい

期待効果:

- 例外案件を無理に通常案件へ当てはめずに済む
- 将来の構成追加でも混乱しにくい

## 4. 優先順位

### 優先度 高

1. project `AGENTS.md` の必須セット作業化
2. docs 更新ルールの明文化

### 優先度 中

3. `PROJECT_SUMMARY.md` の正本区分強化
4. project ごとの確認順と失敗時確認先の明文化

### 優先度 低

5. 例外 project の扱い整理

## 5. 今回時点の結論

- この workspace はすでに入口文書と境界整理の基盤はかなり整っている
- 次の改善は「構造整理」よりも「運用ルールを行動単位へ寄せる」方向が効果的
- 特に `AGENTS.md` を、判断基準だけでなく「変更時の必須セット作業」まで書く形へ寄せるのが有効
