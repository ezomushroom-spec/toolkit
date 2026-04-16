# Project Summary Template

この雛形は `projects/<name>/PROJECT_SUMMARY.md` 用。
初見の人や Codex が、対象・正本・入口・危険領域を 1 枚で把握できるようにする。

---

# Project Summary

## 1. Purpose

- この project が何をするものか
- 主な利用者や運用前提

## 2. Source of Truth

- この folder の役割:
- 正本コード:
- 正本設定:
- 正本データ:
- 正本文書:
- 比較対象や参照専用 backup:

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
- shell / launcher:
- 外部連携や運用境界:

## 7. Risks For Subagents

- 誤認しやすい正本や境界:
- 壊しやすい運用資産:
- 並列編集で衝突しやすい場所:

## 8. Recommended First Step

- 初見で最初に確認することを 1-3 行で書く

## 9. Rollback Hint

- どの単位で戻せるか
- コードと運用資産をどう分けるか

---

詳細仕様や長い背景説明は `START_HERE.md` や `docs/`、`README.md` へ逃がし、この文書は見通し重視で保つ。
