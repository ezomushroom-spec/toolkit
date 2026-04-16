# Post Manager Backup 境界判断メモ

更新日: 2026-04-02

## 1. 目的

- `backup_app_before_electron_20260401_212252` の active / backup / archive 境界と移動結果を固定する。
- active / backup / archive の境界を文書で先に確定し、誤って active 実装先として触らないようにする。
- 物理移動を行う場合の条件、確認点、戻し方を先に残す。

## 2. 現状確認

- active project 本体は `E:\codex\workspace\projects\post-manager-remake\app`
- shell 側の主運用ターゲット候補は `E:\codex\workspace\projects\post-manager-remake\desktop-electron`
- 旧パスは `E:\codex\workspace\projects\post-manager-remake\backup_app_before_electron_20260401_212252`
- 現在の配置は `E:\codex\workspace\archive\projects-backups\backup_app_before_electron_20260401_212252`
- workspace 共通の archive 受け皿は `E:\codex\workspace\archive\projects-backups`

## 3. 判定

- `backup_app_before_electron_20260401_212252` は active project ではない
- 正本でもない
- 比較や復旧のために残す参照専用 backup として扱う
- 名前、内容、役割のどれを見ても `archive/projects-backups/` 側に置くのが本来の境界に合う

## 4. 採用案と実施結果

- 採用案: `archive/projects-backups/backup_app_before_electron_20260401_212252` へ移し、archive 側の参照専用 backup として扱う
- 実施結果: 2026-04-02 に `projects/post-manager-remake/` 直下から `archive/projects-backups/` へ移動した

理由:

- active project と誤認しやすい配置を解消できる
- workspace 共通ルールの active / backup / archive 境界に合う
- 移動前に対応表、確認点、戻し方を文書化できた

## 5. 見送る案

### A. このままずっと project 直下に残す

- 見送る理由:
  - active project と誤認しやすい
  - workspace 共通の active / backup / archive 境界に反する
  - 初見の作業者が `app/` と backup を並列の候補と誤解しやすい

### B. いま即時に archive へ物理移動する

- 見送る理由:
  - 今回は不採用ではなく、実施済み

## 6. 実施内容

### 対象

- 移動元: `E:\codex\workspace\projects\post-manager-remake\backup_app_before_electron_20260401_212252`
- 移動先: `E:\codex\workspace\archive\projects-backups\backup_app_before_electron_20260401_212252`
- 更新対象文書: `projects/post-manager-remake/AGENTS.md`, `START_HERE.md`, `PROJECT_SUMMARY.md`, 必要なら `docs/` 配下の関連文書

### 実装順

1. 旧パス参照の再検索
2. 旧→新対応表と戻し方を文書化
3. backup を `archive/projects-backups/` へ移動
4. 入口文書と判断メモの path を更新
5. 再検索して旧パス残りを確認

### 確認点

- `app/` と `desktop-electron/` の active 導線に影響がないこと
- `backup_app_before_electron_*` を active 実装先として示す文言が残っていないこと
- `archive/projects-backups/` 側で backup だと分かること
- `projects/post-manager-remake` 直下から backup が消えても、初見の読み順が崩れないこと

### 戻し方

- 移動先 `archive/projects-backups/backup_app_before_electron_20260401_212252` から元の `projects/post-manager-remake/` 直下へ戻す
- 文書 path も対応表どおりに旧パスへ戻す
- 物理移動と文書更新は同一単位で戻す

## 7. 今回時点の結論

- `backup_app_before_electron_20260401_212252` は参照専用 backup として確定
- active 実装先としては扱わない
- `archive/projects-backups/backup_app_before_electron_20260401_212252` へ移動済み
