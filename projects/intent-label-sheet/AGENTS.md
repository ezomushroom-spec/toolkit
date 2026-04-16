# Project Rules

## 1. この project の目的

- 意図ラベル集を下から出るシートUIで呼び出して使えるローカル小窓デスクトップアプリ
- Codex 利用時に skill 名を暗記したくない利用者
- 完了時に守るべき価値は「軽い起動」「すぐ開ける」「言い方をすぐコピーできること」「ブラウザではなく独立小窓で扱えること」

## 2. 正本

- 実装の正本: `src/`, `desktop-electron/`
- 設定の正本: `package.json`, `vite.config.ts`, `tsconfig*.json`, `eslint.config.js`, `desktop-electron/package.json`
- データの正本: `src/data/intentLabels.ts`
- 編集してはいけない生成物やバックアップ: `dist/`, `node_modules/`, `desktop-electron/node_modules/`, `build*.log`, `startup.log`, `startup-web.log`, `dev-server.log`, `desktop-electron/runtime/`

## 3. 壊してはいけない既存挙動

- 主操作: 意図ラベルの検索、選択、コピー
- よく使う導線: 下からシートを開く -> ラベル選択 -> 例文コピー
- 互換維持が必要な設定や保存形式: `src/data/intentLabels.ts` の構造
- 外してはいけない運用制約: ローカルだけで完結し、外部送信を前提にしない

## 4. build / run / test / lint

- 通常起動: `start.bat`
- Web 開発起動: `npm run dev:web`
- Web 確認: `start-web.bat`
- テスト: `npm run test`
- lint / format: `npm run lint`
- build: `npm run build:web`
- 実行に必要な前提: `npm install`, `desktop-electron` 側の `npm install`

## 5. 優先確認項目

- 正常系: 小窓起動、シート表示、カテゴリ切替、検索、コピー
- 失敗系: browser API 不可時でも desktop bridge でコピーできること
- 空入力: 検索空欄で一覧が戻ること
- 不正設定: ラベル定義が不足しても画面が即死しないこと
- 存在しないパス: 該当なし
- 途中停止やキャンセル: シート開閉で選択状態が壊れないこと
- 危険操作: 該当なし
- メモリ / GPU / 長時間処理: 過度に重いアニメーションや常駐処理を入れないこと

## 6. UI / 操作上の注意

- 主操作の位置や表現: シート内で最も見つけやすい位置に「言い方をコピー」を置く
- 危険操作の扱い: 該当なし
- エラー表示の要件: コピー失敗時は次の行動が分かる短い文を出す
- 二重実行防止: コピー中はボタンを待機状態にする

## 7. 実装時の注意

- 無関係なリファクタを混ぜない範囲: Vite 基本設定や lint 設定の大幅変更は別タスクに分ける
- 触る前に確認すべき関連処理: `src/App.tsx`, `src/data/intentLabels.ts`, `src/App.css`, `desktop-electron/main.js`, `desktop-electron/preload.js`
- 段階移行が必要な箇所: ローカルデータを別保存方式へ移すとき
- 戻し方: `src/` と `desktop-electron/` と project docs を単位に戻す

## 8. 変更時の必須セット作業

- 更新する docs: `AGENTS.md`, `START_HERE.md`, `PROJECT_SUMMARY.md`, `README.md`, `docs/pre-implementation-decision.md`
- 最低限の確認コマンド: `npm run test`, `npm run build:web`
- 最低限の手動確認: 小窓起動、シート開閉、検索、カテゴリ切替、コピー
- 失敗時に先に見るログやファイル: ブラウザコンソール、Vite ログ、`desktop-electron/runtime/startup-electron.log`、対象 component と data 定義

## 9. 完了報告で必ず触れること

- 何を変えたか
- 何を確認したか
- 何が未確認か
- 残るリスク

