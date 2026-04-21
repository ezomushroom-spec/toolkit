# snapshot trial artifact policy

## 1. 目的

empirical-prompt-tuning で `project-safety-snapshot` を評価したあと、trial fixture と snapshot zip をどう扱うかを固定する。

## 2. ルール

### fixture project

- trial 用 fixture project は、結果確認が終わったら削除する
- fixture は評価補助であり、active project と混同しない

### snapshot zip

- snapshot zip は評価証跡として残してよい
- ただし、常時ため込まず、同一 target の trial zip は代表 1 件を残す
- zip の中身に実データや secrets が入る場合は残さない

## 3. 今回の扱い

- `project-safety-snapshot-fixture` の fixture project は削除済み
- `archive/snapshots/project-safety-snapshot-fixture/20260422_030548.zip` は評価証跡として残す

## 4. 運用判断

- trial の再現に必要な最小証跡だけ残す
- fixture と zip の両方を長期保持しない
- 実案件の snapshot と trial snapshot は混同しない

## 5. 再評価トリガー

- 同一 skill を再 trial して zip が増えたとき
- snapshot artifact に実データが混じる懸念が出たとき
