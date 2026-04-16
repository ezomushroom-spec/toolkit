# WinUI試金石_懸念整理

## 現状確認

- 対象プロジェクトは `E:\codex\workspace\projects\mosaic-remake-winui`。
- `.NET SDK 8.0.419` 導入後、`dotnet restore` は成功。
- 初期状態では `dotnet build` が `XamlCompiler.exe ... exited with code 1` で失敗していた。
- 切り分けのため `MainWindow.xaml` を最小構成へ縮小するとビルド成功。
- 元レイアウトへ戻して検証した結果、`Window` 要素に `Width` / `Height` を直接書いていたことが XAML コンパイル失敗の直接原因だった。
- `Width` / `Height` を削除し、`MainWindow.xaml.cs` の `ConfigureWindow()` で `AppWindow.Resize(new SizeInt32(1400, 920))` を行う形へ移したところ、現行レイアウトのまま `dotnet build` が成功した。
- `App.xaml` の resource 定義は今回の失敗原因ではなかった。

## 採用判断

- WinUI 3 はこの環境で主要フレームワーク候補として継続可能。
- 業務ロジックの正本は引き続き `E:\codex\workspace\projects\mosaic-remake` 側の Python core に置く。
- WinUI 側は shell / UI / bridge 呼び出しに責務を絞り、推論や画像加工を重複実装しない。
- Window サイズや位置の制御は XAML 属性ではなく code-behind か専用 window service で扱う。
- `App.xaml` の brush resource 方式はそのまま採用してよい。

## 未決事項

- WinUI 起動時の初期位置、最小サイズ、リサイズ制約をどこまで定義するか。
- `FileOpenPicker` / `FolderPicker` と desktop D&D の併設方針。
- Python bridge を CLI のまま伸ばすか、将来ローカル API へ寄せるか。
- 画像プレビューを WinUI ネイティブ描画にするか、まずは backend 出力画像の表示から入るか。
- exe 起動中の再ビルドでファイルロックが起きるため、開発運用として「実行中は再ビルド前に閉じる」ルールを明示するか。

## 新たに判明した実行時懸念

- 2026-03-30 時点で `dotnet build` は成功するが、生成した `MosaicRemake.WinUI.exe` はこのマシン上で起動直後に終了する。
- Windows のイベントログでは、障害モジュールが `C:\Program Files\PowerToys\Microsoft.UI.Xaml.dll` と記録されており、WinUI ランタイム解決がアプリ期待値とずれている可能性が高い。
- 例外コードは `0xc000027b`、WER 側の署名には `80040154` が含まれており、Windows App Runtime 未整備または誤った共有 DLL 解決が疑わしい。
- `Windows App Runtime 1.6` の導入を試みたが、この環境では UAC 昇格が必要で自動完了できなかった。
- `WindowsAppSdkSelfContained=true` への切り替えも試したが、今度は `Microsoft.Build.Packaging.Pri.Tasks.dll` がローカル SDK 内に存在せず、self-contained ビルドに必要な Appx/Pri 系ツール不足で停止した。

## 現時点の判断

- WinUI 3 を主要候補から外す必要はまだない。
- ただし、このマシンでは「ビルドは通るが、そのまま実行確認までは完走できない」という環境依存リスクがある。
- 試金石としての次の判断材料は、次のどちらかを満たせるかどうか。
  - Windows App Runtime 1.6 を正規導入した状態で framework-dependent 実行が安定する
  - self-contained ビルドに必要な Visual Studio / AppxPackage / PRI ツール群を整備し、アプリ同梱実行へ寄せられる

## 追記: PATH 汚染の切り分け結果

- 追加確認の結果、このユーザー環境には `Microsoft.WindowsAppRuntime.1.6` 自体はインストール済みだった。
- それでも通常起動で落ちる主因は、`PATH` 上の `C:\Program Files\PowerToys\` から `Microsoft.UI.Xaml.dll` を掴んでいることだった。
- `PowerToys` をその起動プロセスの `PATH` から外した状態で exe を起動すると、少なくとも 10 秒以上プロセスが生存することを確認した。
- そのため、暫定の採用案は `framework-dependent + 専用 launcher` である。
- 実装済みの [`start-winui.bat`](E:\codex\workspace\projects\mosaic-remake-winui\start-winui.bat) と [`debug-start-winui.bat`](E:\codex\workspace\projects\mosaic-remake-winui\debug-start-winui.bat) は、この回避策をローカル起動入口として固定するためのもの。
- さらに [`BootstrapInitializer.cs`](E:\codex\workspace\projects\mosaic-remake-winui\BootstrapInitializer.cs) と [`WindowsAppSdkVersionInfo.cs`](E:\codex\workspace\projects\mosaic-remake-winui\WindowsAppSdkVersionInfo.cs) を追加し、Windows App SDK の bootstrap を明示化した。
- 2026-03-30 時点で、`start-winui.bat` と `debug-start-winui.bat` の両方で 10 秒以上のプロセス生存を確認できている。
