# Project Rules

- このファイルは `skill-prompt-clipboard` 固有の前提だけを扱う。
- Workspace 共通ルールは上位の `AGENTS.md` を優先する。
- 正本コードは `src/`、仕様と計画は `docs/` とし、`dist/` やログを正本扱いしない。
- 主操作は属性切り替え、situation 選択、variant 切り替え、編集欄連動、コピー、リセットであり、この導線を崩さない。
- UI 改善は構造 -> 見た目 -> 安全性の順で行い、無関係な全面改修を混ぜない。
- クリップボード失敗時のエラー表示と再試行導線を保つ。
- build 系の変更は再現条件と戻し方を残す。

## この案件で確認を優先するもの

- 属性切り替え、situation 選択、variant 切り替えの連動
- コピーとリセットの到達性
- build 生成物やログを編集対象に混ぜていないこと

## build / run / test

- 開発起動: `npm run dev`
- 補助入口: `start.bat`, `debug-start.bat`
- 確認コマンド: `npm run lint`, `npm run test`, `npm run build`
- 実行前提: `dist/` やログを正本に混ぜないこと

## 変更時の必須セット作業

- 更新する docs: 入口や build 注意点が変わる場合は `README.md`、見通し変更時は `PROJECT_SUMMARY.md`
- 最低限の確認コマンド: `npm run test`、必要なら `npm run lint` と `npm run build`
- 最低限の手動確認: カテゴリ切り替え、テンプレート選択、コピー、リセット
- 失敗時に先に見るログやファイル: `src/App.tsx`、`src/App.test.tsx`、`docs/image-prompt-situation-manager-spec.md`、`build*.log`、`startup.log`
