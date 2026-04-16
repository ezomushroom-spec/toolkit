export type IntentCategory = 'planning' | 'project' | 'ui' | 'safety' | 'environment'

export type IntentLabel = {
  id: string
  label: string
  category: IntentCategory
  summary: string
  example: string
  internalSkill: string
  note: string
}

export const categoryLabels: Record<IntentCategory, string> = {
  planning: '整理と計画',
  project: 'project 開始',
  ui: 'UI',
  safety: '安全とレビュー',
  environment: '環境',
}

export const intentLabels: IntentLabel[] = [
  {
    id: 'request-translate',
    label: '依頼整理',
    category: 'planning',
    summary: '曖昧な依頼を論点ごとに整理する。',
    example: '依頼整理: この依頼を論点分解して。',
    internalSkill: 'request-translate',
    note: '口語的な依頼や複数トピックが混ざった相談の入口。',
  },
  {
    id: 'pre-implementation-diagnosis',
    label: '方式比較',
    category: 'planning',
    summary: '実装前に候補構成や技術方式を比較する。',
    example: '方式比較: この案件の実装方式候補を比較して。',
    internalSkill: 'pre-implementation-diagnosis',
    note: 'UI 構成変更や新規アプリ、再構築時に使う。',
  },
  {
    id: 'implementation-planner',
    label: '実装計画',
    category: 'planning',
    summary: '実装順、確認点、戻し方を固め、最後に brief まで出す。',
    example: '実装計画: この改修の順番と確認点を出して。',
    internalSkill: 'implementation-planner',
    note: '中規模以上の案件で最初に叩く計画 skill。',
  },
  {
    id: 'plan-review',
    label: '計画レビュー',
    category: 'planning',
    summary: '計画の穴や広げすぎを実装前に点検する。',
    example: '計画レビュー: この計画の穴を見て。',
    internalSkill: 'plan-review',
    note: '実装に入る前の最終チェック用。',
  },
  {
    id: 'project-scaffolder',
    label: '新規project',
    category: 'project',
    summary: '新しい project を標準構成で立ち上げる。',
    example: '新規project: この目的で新しい project を立ち上げて。',
    internalSkill: 'project-scaffolder',
    note: 'docs と入口文書を一気にそろえる。',
  },
  {
    id: 'ui-audit',
    label: 'UI監査',
    category: 'ui',
    summary: '既存 UI の問題や危険操作を診断する。',
    example: 'UI監査: この画面の問題点を見て。',
    internalSkill: 'ui-audit',
    note: '見た目より、主操作とエラー導線の点検に向く。',
  },
  {
    id: 'ui-design-direction',
    label: 'UI方向',
    category: 'ui',
    summary: '画面構成や視覚階層、製品に合うトーンを決める。',
    example: 'UI方向: この画面の方向を決めて。',
    internalSkill: 'ui-design-direction',
    note: 'UI をまだ実装せず、方向だけ固めたいときに使う。',
  },
  {
    id: 'ui-remake-safe',
    label: 'UI改善',
    category: 'ui',
    summary: '既存挙動を壊さずに UI を改善する。',
    example: 'UI改善: この UI を壊さず整理して。',
    internalSkill: 'ui-remake-safe',
    note: '構造を変えるが挙動は守りたい場面向け。',
  },
  {
    id: 'ui-overlap-guard',
    label: 'overlap確認',
    category: 'ui',
    summary: '密なレイアウトの衝突や潰れを確認する。',
    example: 'overlap確認: このレイアウトの潰れを見て。',
    internalSkill: 'ui-overlap-guard',
    note: 'タブやチップ、スクロール領域が多い画面で有効。',
  },
  {
    id: 'image-finishing-tool-design',
    label: '画像仕上げ判断',
    category: 'ui',
    summary: '画像仕上げツールとしての方向や制約を判断する。',
    example: '画像仕上げ判断: この提案が画像仕上げツール向きか見て。',
    internalSkill: 'image-finishing-tool-design',
    note: '汎用エディタ化を避けたい画像系案件向け。',
  },
  {
    id: 'project-safety-snapshot',
    label: 'snapshot',
    category: 'safety',
    summary: '高リスク変更の前に軽量 snapshot を作る。',
    example: 'snapshot: この project の退避を作ってから始めて。',
    internalSkill: 'project-safety-snapshot',
    note: '大きな UI 改修や構成変更の前にだけ使う。',
  },
  {
    id: 'code-review',
    label: 'レビュー',
    category: 'safety',
    summary: '変更後の主要リスクをレビューする。',
    example: 'レビュー: この変更の主要リスクを見て。',
    internalSkill: 'code-review',
    note: '実装後の確認や差分レビューに使う。',
  },
  {
    id: 'desktop-dnd-path-resolution',
    label: 'D&Dパス確認',
    category: 'environment',
    summary: 'drag-and-drop の path 解決を確認する。',
    example: 'D&Dパス確認: この導線の path 解決を見て。',
    internalSkill: 'desktop-dnd-path-resolution',
    note: 'desktop shell やブラウザ差があるときに使う。',
  },
  {
    id: 'windows-batch-launcher',
    label: '起動バッチ整備',
    category: 'environment',
    summary: 'Windows の起動バッチや launcher を整備する。',
    example: '起動バッチ整備: start.bat を整えて。',
    internalSkill: 'windows-batch-launcher',
    note: 'double-click 起動や debug-start.bat が必要なときに使う。',
  },
]
