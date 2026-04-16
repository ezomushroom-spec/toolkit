# docs Structure Notes

## 現状確認

- `docs/` には正式運用文書とテンプレートが同階層で並んでいた
- 文書数が増えるほど、初見で「読むべき文書」と「複製して使う雛形」が混ざりやすい

## 採用判断

- 今回は小さく `docs/templates/` を新設し、テンプレート 3 本だけを分離する
- 正式運用文書は引き続き `docs/` 直下に残す
- `guides/` などの大きい再編はまだ行わない

## 今回 templates へ寄せたもの

- `docs/templates/START_HERE.template.md`
- `docs/templates/project-AGENTS.template.md`
- `docs/templates/implementation-plan-template.md`

## 直下に残したもの

- `workflow.md`
- `coding-rules.md`
- `ui-principles.md`
- `quality-gates.md`
- `archive-boundaries.md`
- `subagent-prompts.md`
- `codex-config-suggestions.md`

## 未決事項

- `subagent-prompts.md` を templates 扱いへ寄せるか
- `vibe-framework.md` を正式文書として残すか、参考文書へ寄せるか
- 将来的に `docs/guides/` を作るか
