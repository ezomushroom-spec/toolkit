# PROJECT_SUMMARY

## 目的

workspace のルール、skill、完了基準が実務でどれだけ機能しているかを、低コストで観測する。

## 正本

- 共通ルール: `E:\codex\workspace\AGENTS.md`
- フロー: `E:\codex\workspace\docs\workflow.md`
- 品質基準: `E:\codex\workspace\docs\quality-gates.md`
- 計測前段: `E:\codex\workspace\docs\effectiveness-measurement-prep.md`

## この project の主な文書

- `docs/measurement-rules.md`: 今見る指標、拾う元、集計頻度
- `docs/measurement-snapshot-YYYYMM.md`: 区切り単位の観測結果
- `docs/empirical-prompt-tuning-current-state_20260422.md`: 評価プロトコル導入前の現状確認
- `docs/empirical-prompt-tuning-adoption-decision_20260422.md`: 採用判断
- `docs/empirical-prompt-tuning-rollout-plan_20260422.md`: 初回ロールアウト計画
- `docs/empirical-prompt-tuning-first-trial_project-scaffolder_20260422.md`: 初回 trial の実行準備
- `docs/empirical-prompt-tuning-trial-result_project-scaffolder_20260422.md`: 初回 trial の結果
- `docs/empirical-prompt-tuning-first-trial_windows-batch-launcher_20260422.md`: batch launcher trial の実行準備
- `docs/empirical-prompt-tuning-trial-result_windows-batch-launcher_20260422.md`: batch launcher trial の結果
- `docs/empirical-prompt-tuning-first-trial_subagent-debug-review_20260422.md`: debug review trial の実行準備
- `docs/empirical-prompt-tuning-trial-result_subagent-debug-review_20260422.md`: debug review trial の結果
- `docs/empirical-prompt-tuning-first-trial_project-safety-snapshot_20260422.md`: snapshot trial の実行準備
- `docs/empirical-prompt-tuning-trial-result_project-safety-snapshot_20260422.md`: snapshot trial の結果
- `docs/empirical-prompt-tuning-first-trial_request-translate_20260422.md`: request translate trial の実行準備
- `docs/empirical-prompt-tuning-trial-result_request-translate_20260422.md`: request translate trial の結果
- `docs/skill-validator-policy-gap_20260422.md`: skill validator と workspace 運用のギャップ整理
- `docs/validator-recording-rule_20260422.md`: validator 記録ルール
- `docs/snapshot-trial-artifact-policy_20260422.md`: snapshot trial artifact の扱い
- `docs/empirical-prompt-tuning-important-rollout_20260422.md`: `Important` 群への横展開順
- `docs/empirical-prompt-tuning-opportunistic-rollout_20260422.md`: `Opportunistic` 群への横展開方針
- `docs/empirical-prompt-tuning-operating-rule_20260422.md`: empirical prompt tuning の 1 枚運用ルール
- `docs/empirical-prompt-tuning-result-log-storage-policy_20260422.md`: result log の正本と補助集計の分け方
- `docs/empirical-prompt-tuning-agents-trial-pause-decision_20260422.md`: `AGENTS.md` section trial をここで一区切りにする判断
- `docs/empirical-prompt-tuning-external-reflection-plan_20260422.md`: commit / PR をどう分けるかの計画
- `docs/empirical-prompt-tuning-staging-manifest_20260422.md`: 実 staging 単位へ落とした manifest
- `docs/empirical-prompt-tuning-publish-handoff_20260422.md`: remote 設定後にすぐ publish するための handoff
- `docs/empirical-prompt-tuning-pr-draft_20260422.md`: PR タイトルと本文の下書き
- `docs/empirical-prompt-tuning-finish-list_20260422.md`: 残りの未完了点だけをまとめた仕上げリスト
- `docs/empirical-prompt-tuning-first-trial_plan-review_20260422.md`: plan review trial の実行準備
- `docs/empirical-prompt-tuning-trial-result_plan-review_20260422.md`: plan review trial の結果
- `docs/empirical-prompt-tuning-first-trial_ui-overlap-guard_20260422.md`: ui overlap guard trial の実行準備
- `docs/empirical-prompt-tuning-trial-result_ui-overlap-guard_20260422.md`: ui overlap guard trial の結果
- `docs/empirical-prompt-tuning-first-trial_image-finishing-tool-design_20260422.md`: image finishing tool design trial の実行準備
- `docs/empirical-prompt-tuning-trial-result_image-finishing-tool-design_20260422.md`: image finishing tool design trial の結果
- `docs/empirical-prompt-tuning-first-trial_empirical-prompt-tuning_20260422.md`: empirical prompt tuning self-trial の実行準備
- `docs/empirical-prompt-tuning-trial-result_empirical-prompt-tuning_20260422.md`: empirical prompt tuning self-trial の結果
- `docs/empirical-prompt-tuning-first-trial_AGENTS-section-user-confirmation-and-delegation_20260422.md`: AGENTS section trial の実行準備
- `docs/empirical-prompt-tuning-trial-result_AGENTS-section-user-confirmation-and-delegation_20260422.md`: AGENTS section trial の結果
- `docs/empirical-prompt-tuning-first-trial_AGENTS-section-pre-implementation-checks_20260422.md`: AGENTS precheck section trial の実行準備
- `docs/empirical-prompt-tuning-trial-result_AGENTS-section-pre-implementation-checks_20260422.md`: AGENTS precheck section trial の結果
- `docs/empirical-prompt-tuning-first-trial_AGENTS-section-quality-checks_20260422.md`: AGENTS quality section trial の実行準備
- `docs/empirical-prompt-tuning-trial-result_AGENTS-section-quality-checks_20260422.md`: AGENTS quality section trial の結果
- `docs/empirical-prompt-tuning-first-trial_AGENTS-section-document-placement_20260422.md`: AGENTS document placement section trial の実行準備
- `docs/empirical-prompt-tuning-trial-result_AGENTS-section-document-placement_20260422.md`: AGENTS document placement section trial の結果
- `docs/empirical-prompt-tuning-first-trial_AGENTS-section-change-exit_20260422.md`: AGENTS change exit section trial の実行準備
- `docs/empirical-prompt-tuning-trial-result_AGENTS-section-change-exit_20260422.md`: AGENTS change exit section trial の結果
- `docs/empirical-prompt-tuning-second-iteration-candidates_20260422.md`: 2nd iteration 候補
- `docs/empirical-prompt-tuning-second-trial_windows-batch-launcher_20260422.md`: windows batch launcher 2nd iteration の実行準備
- `docs/empirical-prompt-tuning-trial-result_windows-batch-launcher_2nd-iteration_20260422.md`: windows batch launcher 2nd iteration の結果
- `docs/empirical-prompt-tuning-second-trial_desktop-dnd-path-resolution_20260422.md`: desktop D&D path resolution 2nd iteration の実行準備
- `docs/empirical-prompt-tuning-trial-result_desktop-dnd-path-resolution_2nd-iteration_20260422.md`: desktop D&D path resolution 2nd iteration の結果
- `docs/empirical-prompt-tuning-second-trial_subagent-debug-review_20260422.md`: subagent debug review 2nd iteration の実行準備
- `docs/empirical-prompt-tuning-trial-result_subagent-debug-review_2nd-iteration_20260422.md`: subagent debug review 2nd iteration の結果
- `docs/empirical-prompt-tuning-first-trial_implementation-planner_20260422.md`: implementation planner trial の実行準備
- `docs/empirical-prompt-tuning-trial-result_implementation-planner_20260422.md`: implementation planner trial の結果
- `docs/empirical-prompt-tuning-first-trial_pre-implementation-diagnosis_20260422.md`: pre-implementation diagnosis trial の実行準備
- `docs/empirical-prompt-tuning-trial-result_pre-implementation-diagnosis_20260422.md`: pre-implementation diagnosis trial の結果
- `docs/empirical-prompt-tuning-first-trial_code-review_20260422.md`: code review trial の実行準備
- `docs/empirical-prompt-tuning-trial-result_code-review_20260422.md`: code review trial の結果
- `docs/empirical-prompt-tuning-first-trial_ui-audit_20260422.md`: ui audit trial の実行準備
- `docs/empirical-prompt-tuning-trial-result_ui-audit_20260422.md`: ui audit trial の結果
- `docs/empirical-prompt-tuning-first-trial_ui-design-direction_20260422.md`: ui design direction trial の実行準備
- `docs/empirical-prompt-tuning-trial-result_ui-design-direction_20260422.md`: ui design direction trial の結果
- `docs/empirical-prompt-tuning-first-trial_ui-remake-safe_20260422.md`: ui remake safe trial の実行準備
- `docs/empirical-prompt-tuning-trial-result_ui-remake-safe_20260422.md`: ui remake safe trial の結果
- `docs/empirical-prompt-tuning-first-trial_desktop-dnd-path-resolution_20260422.md`: desktop D&D path resolution trial の実行準備
- `docs/empirical-prompt-tuning-trial-result_desktop-dnd-path-resolution_20260422.md`: desktop D&D path resolution trial の結果
- `docs/empirical-prompt-tuning-open-questions_20260422.md`: 未決事項

## empirical-prompt-tuning の現在地

- 初回 `Critical` 3 件の trial は完了
- いずれも `[critical]` failure なし
- `project-safety-snapshot` の trial は完了
- `request-translate` の trial は完了
- snapshot artifact の扱いは固定済み
- `implementation-planner` の trial は完了
- `pre-implementation-diagnosis` の trial は完了
- `code-review` の trial は完了
- `ui-audit` の trial は完了
- `ui-design-direction` の trial は完了
- `ui-remake-safe` の trial は完了
- `desktop-dnd-path-resolution` の trial は完了
- `Important` 群の初回横展開は完了
- `Opportunistic` 群の優先順は固定済み
- `plan-review` の trial は完了
- `ui-overlap-guard` の trial は完了
- `image-finishing-tool-design` の trial は完了
- `empirical-prompt-tuning` の trial は完了
- `Opportunistic` 群の初回横展開は完了
- root `AGENTS.md` の `ユーザー確認と委任` 節 trial は完了
- root `AGENTS.md` の `実装前の確認` 節 trial は完了
- root `AGENTS.md` の `品質確認` 節 trial は完了
- root `AGENTS.md` の `文書と配置` 節 trial は完了
- root `AGENTS.md` の `変更の出口` 節 trial は完了
- 1 枚運用ルールは `empirical-prompt-tuning-operating-rule_20260422.md`
- result log の正本は個別文書、補助集計は別扱い
- `AGENTS.md` section trial は現時点で一区切り
- publish 前提の branch と 2 commit は作成済み
- 残りの未完了点は `empirical-prompt-tuning-finish-list_20260422.md`
- `windows-batch-launcher` の 2nd iteration は完了
- `desktop-dnd-path-resolution` の 2nd iteration は完了
- `subagent-debug-review` の 2nd iteration は完了
- 初回に選んだ 2nd iteration 候補は一通り完了
- validator failure は `schema mismatch` と `instruction quality issue` に分けて記録する

## いまの運用方針

- 最初は手動集計
- 見る指標は 4 本に限定
- 自動化は、手動でも続くと判断できてから検討
