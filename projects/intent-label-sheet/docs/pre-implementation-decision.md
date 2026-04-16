# 実装前判断メモ

更新日: 2026-04-16

## 1. 文書の目的

- `intent-label-sheet` をブラウザ表示ではなく、小窓のデスクトップアプリとして扱うための shell 方式を決める
- 利用者と実装担当が、なぜその方式を採るかを迷わないようにする

## 2. 前提

- 対象 project: `E:\codex\workspace\projects\intent-label-sheet`
- 対象画面 / 機能: 下から出る意図ラベルシート、検索、カテゴリ絞り込み、クリップボードコピー
- 現在の正本候補:
  - UI とデータ: `src/`
  - 設定: `package.json`, `vite.config.ts`
- 実コード / 実データ / 現用設定で確認したこと:
  - 現在は React + Vite のローカル Web アプリ
  - backend や重い処理はなく、ローカルデータとクリップボード操作だけを使う
  - Windows でのローカル起動を前提にしている
- 変えない条件:
  - 意図ラベルのデータ構造は当面 `src/data/intentLabels.ts` を正本とする
  - 機能は軽量に保つ
  - 外部送信や常駐監視は入れない
- 再確認可能な条件:
  - 将来の tray 常駐、グローバルホットキー、ローカル保存は後で拡張できる

## 3. 候補比較

### 候補 A: Electron shell を追加する

- 概要:
  - 現在の React + Vite アプリをそのまま renderer として使い、Electron の小窓 shell を追加する
- 要件適合性:
  - 高い。小窓化、always-on-top、frameless 化、tray や global shortcut 追加まで広げやすい
- 実装の確実性:
  - 高い。Node / npm だけで完結し、既存 workspace に Electron の参考例がある
- 保守性 / 拡張性:
  - 中。Tauri より重いが、実装は読みやすく広げやすい
- UI / 運用面の評価:
  - 高い。ブラウザではなく専用小窓として扱える
- 既存資産の再利用:
  - 高い。既存 `src/` をほぼそのまま使える
- 主な弱点:
  - ランタイムが重め
  - 配布サイズが大きくなりやすい

### 候補 B: Tauri shell を追加する

- 概要:
  - 現在の React + Vite アプリを Tauri の frontend として包む
- 要件適合性:
  - 高い。軽量な小窓アプリには向く
- 実装の確実性:
  - 中。Rust toolchain の前提が増え、非専門ユーザーには保守ハードルが上がる
- 保守性 / 拡張性:
  - 中。軽いが、shell 側の修正は Electron より学習コストが高い
- UI / 運用面の評価:
  - 高い。小窓化には十分
- 既存資産の再利用:
  - 高い。frontend はそのまま使える
- 主な弱点:
  - 初期セットアップが重い
  - workspace 内の参考資産が少ない

### 候補 C: Web アプリのまま使い続ける

- 概要:
  - 現在の Vite アプリをブラウザで使い続ける
- 要件適合性:
  - 中。軽さはあるが、独立した小窓アプリにはならない
- 実装の確実性:
  - 非常に高い
- 保守性 / 拡張性:
  - 高い
- UI / 運用面の評価:
  - 中。ブラウザ枠が残り、求める「小窓感」が弱い
- 既存資産の再利用:
  - 非常に高い
- 主な弱点:
  - 今回の要望を満たし切らない

## 4. 採用判断

- 採用案:
  - 候補 A: Electron shell を追加する
- 採用理由:
  - 今回の目的は「軽さ」だけでなく「専用の小窓として扱えること」
  - 既存の React + Vite をそのまま再利用しやすい
  - workspace 内に Electron の参考例があり、実装と保守の確実性が高い
  - Tauri は軽いが、Rust toolchain を前提にすると今の利用者には運用負荷が上がる
- 見送る案と理由:
  - 候補 B は軽さでは魅力があるが、初期構築と保守負荷が今は高い
  - 候補 C は最も簡単だが、デスクトップ小窓化という要望を満たさない
- 読む先:
  - `src/`
  - `package.json`
  - 参考: `E:\codex\workspace\projects\post-manager-remake\desktop-electron`
- 実装先:
  - `desktop-electron/` を新規追加する
- 文書更新先:
  - `AGENTS.md`
  - `START_HERE.md`
  - `PROJECT_SUMMARY.md`
  - `README.md`

## 5. keep / fix / 後送り

### keep

- 現在の React + Vite UI
- `src/data/intentLabels.ts` のローカルデータ構造
- 検索、カテゴリ切替、コピー導線

### fix

- ブラウザ起動前提をやめて、小窓 shell から開けるようにする
- 必要なら frameless / always-on-top / narrow window の初期設定を入れる

### 今回やらないもの

- tray 常駐
- グローバルホットキー
- 自動起動
- ローカル保存の複雑化
- shell から business logic を増やすこと

## 6. 実装前に守る運用ルール

- 保護対象データ / 設定:
  - `src/data/intentLabels.ts`
  - 既存 frontend の挙動
- 先に確認する危険操作:
  - なし
- 触る範囲:
  - `desktop-electron/`
  - 必要最小限の `package.json` script
  - 起動用 batch
- 触らない範囲:
  - frontend の機能追加を広げすぎない
  - 外部送信や複雑な native bridge を入れない
- 戻し方:
  - `desktop-electron/` を外し、従来どおり `npm run dev` / `start.bat` に戻す

## 7. 未決事項

- 実装前に決めること:
  - まずは dev 用 shell のみ作るか、配布 build まで入れるか
  - 窓サイズと frameless を初回から入れるか
- 実装中に再確認する分岐:
  - クリップボード処理を browser API のまま使うか、shell API へ寄せるか
- ユーザー確認が必要な重要トレードオフ:
  - 今回はなし。最初は Electron で確実に小窓化し、軽量化をさらに求める場合に Tauri を再比較する

## 8. 次の一手

1. `desktop-electron/` を追加し、既存 frontend を読み込む最小 shell を作る
2. 窓サイズ、タイトル、always-on-top のような小窓向け初期設定を入れる
3. shell 追加後に、起動確認と従来の Web 起動の両方を確認する
