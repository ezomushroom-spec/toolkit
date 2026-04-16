# Project Summary Template

サブエージェント向けの案件サマリー雛形です。
各 project では `PROJECT_SUMMARY.md` として配置し、最初に読む文書として使います。

```md
# Project Summary

## 1. Purpose

- この案件が何をするものかを 1-2 行で書く。

## 2. Source of Truth

- 正本コード:
- 正本データ:
- 正本設定:
- 正本が未確定なら、その候補:

## 3. Primary Entry Points

- 通常起動:
- 代替入口:
- ビルドや検証の主要コマンド:

## 4. Safe Read Scope

- 初見で読んでよいディレクトリ:
- 先に確認すべき文書:

## 5. Do Not Edit Without Explicit Request

- backup:
- profile / user data:
- build artifact / generated:
- secrets / local state:

## 6. Related Boundaries

- UI:
- backend / business logic:
- desktop shell / launcher:
- external integration:

## 7. Risks for Subagents

- 誤認しやすい正本:
- 壊しやすい運用資産:
- 並列編集で衝突しやすい場所:

## 8. Recommended First Step

- 初見サブエージェントが最初にやるべき確認を 1-3 行で書く。

## 9. Rollback Hint

- 問題が出たとき、どの単位で戻すかを短く書く。
```
