# Project Rules

- この案件の正本実装先は `E:\codex\workspace\projects\narrative-thumbnail-studio\app` として扱う。
- `E:\自作アプリ集\narrative-thumbnail-studio` は移管前の元配置として残し、参照や差分確認には使ってよいが、以後の主実装先とは混同しない。
- `E:\codex\workspace\projects\narrative-thumbnail-studio` は判断記録、調査結果、次の実装準備文書の置き場として扱う。
- 実装やレビューでは、docs より先に正本コードを確認する。
- 正本コードを変更する場合は、影響対象を `ui/` `core/` `presets/` に分けて整理してから着手する。
- `preset_panel_preview*.png`、`test_*.png`、`startup_error.log`、`_pythonw_*` は参照用生成物として扱い、明示依頼なしで編集しない。
- `presets/*.json` はプリセット定義の正本候補なので、UI 側の挙動変更と切り離して勝手に変更しない。
- `起動.bat` と `デバッグ起動.bat` は利用者導線なので、変更時は戻し方を先に明示する。
- 画像読み込み、出力、履歴、削除系の操作は誤操作コストがあるため、確認、対象明示、二重実行防止を優先して確認する。
- UI 改善や機能追加を行う場合は、構造 -> 見た目 -> 安全性の順で扱う。
- この案件で `projects` 配下に残す文書は、少なくとも `現状確認` `採用判断` `未決事項` を分ける。

## 変更時の必須セット作業

- 更新する docs: `AGENTS.md`、`START_HERE.md`、`PROJECT_SUMMARY.md`、この project 配下の判断メモ
- 最低限の確認コマンド: 正本側で使う起動方法を基準に確認し、必要なら `起動.bat` と `デバッグ起動.bat` の導線も見直す
- 最低限の手動確認: 画像読込、出力、履歴、削除系の誤操作防止、プリセット反映、起動導線
- 失敗時に先に見るログやファイル: `startup_error.log`、`_pythonw_*`、正本側の `ui/`、`core/`、`presets/`
