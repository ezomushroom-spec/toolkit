# Project Rules

- このファイルは `mosaic-remake-winui` 固有の前提だけを扱う。
- Workspace 共通ルールは上位の `AGENTS.md` を優先する。
- WinUI 側は UI shell と bridge 接続に責務を絞り、推論や画像加工の正本を複製しない。
- 推論コアの正本は親案件 `mosaic-remake` 側の Python に残し、この project では shell 側の都合で業務ロジックを書き換えない。
- 起動確認はまず `start-winui.bat` と `debug-start-winui.bat` を基準にし、通常の `dotnet run` 前提へ勝手に寄せない。
- PowerToys 由来の DLL 解決問題を避ける前提、Windows App SDK bootstrap、bridge health 導線を壊さない。
- `bin/`、`obj/`、`build-diag.log`、`startup.log`、`tmp_ui_capture.png` は生成物や調査物として扱い、正本に混ぜない。

## この案件で確認を優先するもの

- launcher 経由での WinUI 起動安定性
- Python bridge の health 導線
- shell 側に業務ロジックが重複していないこと

## 変更時の必須セット作業

- 更新する docs: `AGENTS.md`、`START_HERE.md`、`PROJECT_SUMMARY.md`、必要なら親案件 `mosaic-remake` 側の判断メモ
- 最低限の確認コマンド: `start-winui.bat` または `debug-start-winui.bat`
- 最低限の手動確認: WinUI 起動、bridge health、launcher 経由の導線、shell 側に業務ロジックが増えていないこと
- 失敗時に先に見るログやファイル: `startup.log`、`build-diag.log`、bridge 関連コード、親案件の Python 側正本
