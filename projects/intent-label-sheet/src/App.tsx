import { useMemo, useState } from 'react'
import './App.css'
import { categoryLabels, intentLabels, type IntentCategory, type IntentLabel } from './data/intentLabels'

async function copyText(text: string) {
  if (window.intentLabelDesktop?.writeClipboardText) {
    await window.intentLabelDesktop.writeClipboardText(text)
    return
  }

  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(text)
    return
  }

  const textArea = document.createElement('textarea')
  textArea.value = text
  textArea.setAttribute('readonly', 'true')
  textArea.style.position = 'absolute'
  textArea.style.left = '-9999px'
  document.body.appendChild(textArea)
  textArea.select()
  const copied = document.execCommand('copy')
  document.body.removeChild(textArea)

  if (!copied) {
    throw new Error('コピーに失敗しました。')
  }
}

function filterLabels(
  labels: IntentLabel[],
  activeCategory: IntentCategory | 'all',
  query: string,
) {
  const normalized = query.trim().toLowerCase()

  return labels.filter((item) => {
    const categoryMatch = activeCategory === 'all' || item.category === activeCategory
    const queryMatch =
      normalized.length === 0 ||
      item.label.toLowerCase().includes(normalized) ||
      item.summary.toLowerCase().includes(normalized) ||
      item.example.toLowerCase().includes(normalized) ||
      item.note.toLowerCase().includes(normalized)

    return categoryMatch && queryMatch
  })
}

function App() {
  const [activeCategory, setActiveCategory] = useState<IntentCategory | 'all'>('all')
  const [query, setQuery] = useState('')
  const [status, setStatus] = useState('意図ラベルを選んでコピーできます')
  const [isCopying, setIsCopying] = useState(false)

  const visibleLabels = useMemo(
    () => filterLabels(intentLabels, activeCategory, query),
    [activeCategory, query],
  )

  const handleCopy = async (text: string, message: string) => {
    setIsCopying(true)
    try {
      await copyText(text)
      setStatus(message)
    } catch (error) {
      setStatus(error instanceof Error ? error.message : 'コピーに失敗しました')
    } finally {
      setIsCopying(false)
    }
  }

  return (
    <main className="app-shell">
      <section className="sheet-panel open standalone" aria-label="意図ラベルシート">
        <div className="sheet-handle static">
          <span className="handle-bar"></span>
          <span>意図ラベル</span>
          <span className={isCopying ? 'status-text busy' : 'status-text'}>{status}</span>
        </div>

        <div className="sheet-body">
          <div className="sheet-toolbar">
            <label className="search-box">
              <span className="eyebrow">Search</span>
              <input
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="ラベル名や使用場面で絞り込む"
              />
            </label>

            <div className="category-row" role="tablist" aria-label="カテゴリ">
              <button
                type="button"
                className={activeCategory === 'all' ? 'chip active' : 'chip'}
                onClick={() => setActiveCategory('all')}
              >
                すべて
              </button>
              {(Object.keys(categoryLabels) as IntentCategory[]).map((category) => (
                <button
                  key={category}
                  type="button"
                  className={activeCategory === category ? 'chip active' : 'chip'}
                  onClick={() => setActiveCategory(category)}
                >
                  {categoryLabels[category]}
                </button>
              ))}
            </div>
          </div>

          <div className="label-grid">
            {visibleLabels.map((item) => (
              <article key={item.id} className="label-card">
                <div className="label-card-head">
                  <strong>{item.label}</strong>
                  <span>{categoryLabels[item.category]}</span>
                </div>
                <p>{item.summary}</p>
                <button
                  type="button"
                  className="copy-inline-button"
                  onClick={() => handleCopy(item.example, `「${item.label}」をコピーしました`)}
                  disabled={isCopying}
                >
                  コピー
                </button>
              </article>
            ))}
          </div>

          {visibleLabels.length === 0 ? (
            <p className="empty-note">該当する意図ラベルがありません。</p>
          ) : null}
        </div>
      </section>
    </main>
  )
}

export default App
