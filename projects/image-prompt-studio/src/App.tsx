import { useEffect, useMemo, useState } from 'react'
import {
  canonicalWildcards,
  canonicalWildcardsSource,
  skippedCanonicalWildcards,
  type CanonicalWildcardGroup,
} from './generated/canonicalWildcards'
import './App.css'

type ImagePromptAttribute = 'character' | 'pose' | 'place' | 'lighting' | 'style' | 'custom'

type ImagePromptVariant = {
  id: string
  label: string
  purpose: string
  prompt: string
  negativePrompt?: string
}

type ImagePromptSituation = {
  id: string
  title: string
  attribute: ImagePromptAttribute
  summary: string
  tags: string[]
  variants: ImagePromptVariant[]
}

type WildcardGroup = CanonicalWildcardGroup

const attributeLabels: Record<ImagePromptAttribute, string> = {
  character: '人物',
  pose: 'ポーズ',
  place: '場所',
  lighting: '光',
  style: '画風',
  custom: 'カスタム',
}

const imagePromptSituations: ImagePromptSituation[] = [
  {
    id: 'quiet-window-reading',
    title: '窓辺で本を読む少女',
    attribute: 'character',
    summary: '穏やかな室内、窓明かり、静かな読書時間を再現する束です。',
    tags: ['少女', '読書', '窓辺', '静けさ'],
    variants: [
      {
        id: 'base',
        label: '基本',
        purpose: 'situation を素直に再現する標準版。',
        prompt:
          'a quiet girl reading a book by the window, soft morning light, calm room, gentle expression, cozy atmosphere, detailed eyes, natural pose, warm colors, high quality illustration',
      },
      {
        id: 'cinematic',
        label: '光重視',
        purpose: '窓から入る光と空気感を強める版。',
        prompt:
          'a girl reading a book beside a large window, sunbeams through thin curtains, dust in the light, peaceful interior, soft backlight, warm highlights, cinematic composition, delicate illustration',
      },
      {
        id: 'negative',
        label: 'ネガティブ',
        purpose: '破綻しやすい要素を避ける補助プロンプト。',
        prompt:
          'low quality, blurry, bad anatomy, extra fingers, missing fingers, distorted hands, messy background, harsh shadow, overexposed face, text, watermark',
      },
    ],
  },
  {
    id: 'rainy-street-turn',
    title: '雨の路地で振り返る人物',
    attribute: 'pose',
    summary: '歩行中に振り返る動き、濡れた路面、夜の反射をまとめた束です。',
    tags: ['振り返り', '雨', '夜', '路地'],
    variants: [
      {
        id: 'base',
        label: '基本',
        purpose: 'ポーズと状況の両方を指定する標準版。',
        prompt:
          'a person turning back while walking in a rainy alley, wet pavement reflections, umbrella in hand, night city lights, dynamic pose, subtle motion, atmospheric illustration',
      },
      {
        id: 'composition',
        label: '構図強化',
        purpose: '奥行きと視線誘導を強める版。',
        prompt:
          'rear three-quarter view of a person turning back in a narrow rainy alley, leading lines, wet asphalt reflections, neon bokeh, off-center composition, dramatic yet quiet mood',
      },
      {
        id: 'negative',
        label: 'ネガティブ',
        purpose: '雨や夜景で崩れやすい要素を抑える補助版。',
        prompt:
          'low quality, muddy details, unreadable face, broken umbrella, extra limbs, distorted body, oversaturated neon, flat lighting, text, watermark',
      },
    ],
  },
  {
    id: 'greenhouse-afternoon',
    title: '午後の温室',
    attribute: 'place',
    summary: 'ガラス越しの光、植物、少し湿った空気を描く場所ベースの束です。',
    tags: ['温室', '植物', '午後', 'ガラス'],
    variants: [
      {
        id: 'base',
        label: '基本',
        purpose: '場所の印象を安定して出す版。',
        prompt:
          'inside a quiet greenhouse in the afternoon, lush plants, glass ceiling, filtered sunlight, humid air, soft shadows, peaceful atmosphere, detailed background illustration',
      },
      {
        id: 'character-in-place',
        label: '人物入り',
        purpose: '場所を主役にしつつ人物を加える版。',
        prompt:
          'a small figure standing inside a greenhouse, surrounded by lush plants, filtered afternoon sunlight through glass panels, quiet humid atmosphere, balanced character and background detail',
      },
      {
        id: 'negative',
        label: 'ネガティブ',
        purpose: '背景密度が上がった時の崩れを抑える版。',
        prompt:
          'low quality, cluttered composition, random objects, broken perspective, flat plants, noisy background, overexposed glass, text, watermark',
      },
    ],
  },
  {
    id: 'golden-hour-rooftop',
    title: '夕方の屋上',
    attribute: 'lighting',
    summary: '夕日、逆光、長い影を使ったドラマチックな光の束です。',
    tags: ['夕方', '屋上', '逆光', '青春'],
    variants: [
      {
        id: 'base',
        label: '基本',
        purpose: '夕方の光を中心に再現する版。',
        prompt:
          'a character standing on a school rooftop at golden hour, warm sunset light, long shadows, soft wind, emotional atmosphere, backlit hair, cinematic anime illustration',
      },
      {
        id: 'soft',
        label: '柔らかめ',
        purpose: '強すぎるドラマ性を抑えて日常寄りにする版。',
        prompt:
          'a quiet school rooftop in the evening, gentle golden light, soft breeze, relaxed character pose, subtle warm colors, peaceful slice-of-life mood, clean anime illustration',
      },
      {
        id: 'negative',
        label: 'ネガティブ',
        purpose: '逆光で顔や色が潰れるのを避ける版。',
        prompt:
          'low quality, harsh contrast, black face, blown highlights, muddy shadow, bad anatomy, extra fingers, distorted railing, text, watermark',
      },
    ],
  },
  {
    id: 'storybook-watercolor',
    title: '絵本風の水彩',
    attribute: 'style',
    summary: '柔らかい輪郭、紙の質感、淡い色を使う画風の束です。',
    tags: ['水彩', '絵本', '淡色', '紙質感'],
    variants: [
      {
        id: 'base',
        label: '基本',
        purpose: '水彩風の画面を作る標準版。',
        prompt:
          'storybook watercolor illustration, soft outlines, gentle pastel colors, visible paper texture, warm and whimsical mood, simple but charming details, hand-painted feeling',
      },
      {
        id: 'scene',
        label: '場面込み',
        purpose: '画風と小さな場面を同時に指定する版。',
        prompt:
          'a small character walking through a flower path, storybook watercolor illustration, soft outlines, pastel colors, paper texture, gentle light, warm whimsical atmosphere',
      },
      {
        id: 'negative',
        label: 'ネガティブ',
        purpose: '水彩風で避けたい硬さや過剰な描き込みを抑える版。',
        prompt:
          'photorealistic, hard plastic texture, overly sharp details, harsh contrast, noisy texture, low quality, muddy colors, text, watermark',
      },
    ],
  },
  {
    id: 'custom-free-prompt',
    title: '自由入力ベース',
    attribute: 'custom',
    summary: '固定 situation に当てはまらない画像生成プロンプトを一時編集する枠です。',
    tags: ['自由入力', '一時編集'],
    variants: [
      {
        id: 'blank',
        label: '空欄',
        purpose: 'その場で新しいプロンプトを書き始めるための枠。',
        prompt: '',
      },
      {
        id: 'scaffold',
        label: '下書き枠',
        purpose: 'situation、見た目、光、画風を埋めるための下書き。',
        prompt:
          'subject: \nscene: \ncomposition: \nlighting: \nstyle: \nquality: high quality illustration\nnegative: low quality, blurry, bad anatomy, text, watermark',
      },
    ],
  },
]

const wildcardGroups: WildcardGroup[] = canonicalWildcards

const storageKey = 'image-prompt-studio:v1:situations'

type StoredSituations = {
  version: 1
  situations: ImagePromptSituation[]
}

function normalizeSituations(situations: ImagePromptSituation[]) {
  return situations.map((situation) => ({
    ...situation,
    variants: situation.variants.map((variant) => {
      if (variant.id === 'negative' && !variant.negativePrompt) {
        return {
          ...variant,
          prompt: '',
          negativePrompt: variant.prompt,
        }
      }

      return {
        ...variant,
        negativePrompt: variant.negativePrompt ?? '',
      }
    }),
  }))
}

function loadSituations() {
  if (typeof window === 'undefined') {
    return normalizeSituations(imagePromptSituations)
  }

  try {
    const raw = window.localStorage.getItem(storageKey)
    if (!raw) {
      return normalizeSituations(imagePromptSituations)
    }

    const parsed = JSON.parse(raw) as Partial<StoredSituations>
    if (parsed.version !== 1 || !Array.isArray(parsed.situations)) {
      return normalizeSituations(imagePromptSituations)
    }

    return normalizeSituations(parsed.situations)
  } catch {
    return normalizeSituations(imagePromptSituations)
  }
}

function saveSituations(situations: ImagePromptSituation[]) {
  const payload: StoredSituations = {
    version: 1,
    situations,
  }
  window.localStorage.setItem(storageKey, JSON.stringify(payload))
}

function loadInitialState() {
  const situations = loadSituations()
  const situation = situations[0]
  const variant = situations[0].variants[0]
  return {
    situations,
    activeAttribute: situation.attribute,
    selectedSituationId: situation.id,
    selectedVariantId: variant.id,
    prompt: variant.prompt,
    negativePrompt: variant.negativePrompt ?? '',
  }
}

async function copyText(text: string) {
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
    throw new Error('Clipboard API が利用できませんでした。')
  }
}

function App() {
  const [initialState] = useState(loadInitialState)
  const [situations, setSituations] = useState(initialState.situations)
  const [activeAttribute, setActiveAttribute] = useState<ImagePromptAttribute>(initialState.activeAttribute)
  const [selectedSituationId, setSelectedSituationId] = useState(initialState.selectedSituationId)
  const [selectedVariantId, setSelectedVariantId] = useState(initialState.selectedVariantId)
  const [draftPrompt, setDraftPrompt] = useState(initialState.prompt)
  const [draftNegativePrompt, setDraftNegativePrompt] = useState(initialState.negativePrompt)
  const [status, setStatus] = useState('コピー待機中')
  const [errorMessage, setErrorMessage] = useState('')
  const [isCopying, setIsCopying] = useState(false)

  const visibleSituations = useMemo(
    () => situations.filter((situation) => situation.attribute === activeAttribute),
    [activeAttribute, situations],
  )

  const selectedSituation =
    situations.find((situation) => situation.id === selectedSituationId) ?? situations[0]

  const selectedVariant =
    selectedSituation?.variants.find((variant) => variant.id === selectedVariantId) ??
    selectedSituation?.variants[0]

  useEffect(() => {
    if (selectedSituation?.attribute !== activeAttribute) {
      const nextSituation = visibleSituations[0]

      if (nextSituation) {
        setSelectedSituationId(nextSituation.id)
        setSelectedVariantId(nextSituation.variants[0].id)
        setDraftPrompt(nextSituation.variants[0].prompt)
        setDraftNegativePrompt(nextSituation.variants[0].negativePrompt ?? '')
        setErrorMessage('')
        setStatus(`「${nextSituation.title}」を選択中`)
      }
    }
  }, [activeAttribute, selectedSituation?.attribute, visibleSituations])

  const handleSelectSituation = (situation: ImagePromptSituation) => {
    const nextVariant = situation.variants[0]
    setSelectedSituationId(situation.id)
    setSelectedVariantId(nextVariant.id)
    setDraftPrompt(nextVariant.prompt)
    setDraftNegativePrompt(nextVariant.negativePrompt ?? '')
    setErrorMessage('')
    setStatus(`「${situation.title}」を選択中`)
  }

  const handleSelectVariant = (variant: ImagePromptVariant) => {
    setSelectedVariantId(variant.id)
    setDraftPrompt(variant.prompt)
    setDraftNegativePrompt(variant.negativePrompt ?? '')
    setErrorMessage('')
    setStatus(`「${variant.label}」を編集中`)
  }

  const handleCopy = async () => {
    setIsCopying(true)
    setErrorMessage('')

    try {
      await copyText(draftPrompt)
      setStatus('クリップボードにコピーしました')
    } catch (error) {
      setErrorMessage(
        error instanceof Error
          ? error.message
          : 'コピーに失敗しました。手動コピーを試してください。',
      )
      setStatus('コピー失敗')
    } finally {
      setIsCopying(false)
    }
  }

  const handleCopyNegativePrompt = async () => {
    setIsCopying(true)
    setErrorMessage('')

    try {
      await copyText(draftNegativePrompt)
      setStatus('ネガティブプロンプトをコピーしました')
    } catch (error) {
      setErrorMessage(
        error instanceof Error
          ? error.message
          : 'コピーに失敗しました。手動コピーを試してください。',
      )
      setStatus('コピー失敗')
    } finally {
      setIsCopying(false)
    }
  }

  const handleCopyWildcardToken = async (group: WildcardGroup) => {
    setIsCopying(true)
    setErrorMessage('')

    try {
      await copyText(group.token)
      setStatus(`「${group.token}」をコピーしました`)
    } catch (error) {
      setErrorMessage(
        error instanceof Error
          ? error.message
          : 'コピーに失敗しました。手動コピーを試してください。',
      )
      setStatus('コピー失敗')
    } finally {
      setIsCopying(false)
    }
  }

  const handleReset = () => {
    if (!selectedVariant) {
      return
    }

    setDraftPrompt(selectedVariant.prompt)
    setDraftNegativePrompt(selectedVariant.negativePrompt ?? '')
    setStatus('選択中のプロンプトに戻しました')
    setErrorMessage('')
  }

  const handleCopySituation = async () => {
    if (!selectedSituation) {
      return
    }

    const bundleText = selectedSituation.variants
      .map((variant) => {
        const parts = [`[${variant.label}]`]
        if (variant.prompt) {
          parts.push(`prompt:\n${variant.prompt}`)
        }
        if (variant.negativePrompt) {
          parts.push(`negative prompt:\n${variant.negativePrompt}`)
        }
        return parts.join('\n')
      })
      .join('\n\n')

    setIsCopying(true)
    setErrorMessage('')

    try {
      await copyText(bundleText)
      setStatus('situation 全体をコピーしました')
    } catch (error) {
      setErrorMessage(
        error instanceof Error
          ? error.message
          : 'コピーに失敗しました。手動コピーを試してください。',
      )
      setStatus('コピー失敗')
    } finally {
      setIsCopying(false)
    }
  }

  const handleSaveVariant = () => {
    if (!selectedVariant) {
      return
    }

    const nextSituations = situations.map((situation) => {
      if (situation.id !== selectedSituationId) {
        return situation
      }

      return {
        ...situation,
        variants: situation.variants.map((variant) =>
          variant.id === selectedVariantId
            ? {
                ...variant,
                prompt: draftPrompt,
                negativePrompt: draftNegativePrompt,
              }
            : variant,
        ),
      }
    })

    setSituations(nextSituations)
    saveSituations(nextSituations)
    setStatus('選択中の版を保存しました')
    setErrorMessage('')
  }

  const handleResetStorage = () => {
    const nextSituations = normalizeSituations(imagePromptSituations)
    window.localStorage.removeItem(storageKey)
    setSituations(nextSituations)
    setActiveAttribute(nextSituations[0].attribute)
    setSelectedSituationId(nextSituations[0].id)
    setSelectedVariantId(nextSituations[0].variants[0].id)
    setDraftPrompt(nextSituations[0].variants[0].prompt)
    setDraftNegativePrompt(nextSituations[0].variants[0].negativePrompt ?? '')
    setStatus('保存データを初期状態に戻しました')
    setErrorMessage('')
  }

  if (!selectedSituation || !selectedVariant) {
    return (
      <main className="app-shell">
        <section className="empty-state" role="alert">
          <h1>読み込める situation がありません</h1>
          <p>保存データを初期化してから再度開いてください。</p>
          <button type="button" className="primary-button" onClick={handleResetStorage}>
            初期状態に戻す
          </button>
        </section>
      </main>
    )
  }

  return (
    <main className="app-shell">
      <section className="app-masthead" aria-label="アプリ概要">
        <div>
          <p className="eyebrow">Image Prompt Studio</p>
          <h1>Situation を選び、生成用プロンプトへ整える。</h1>
          <p className="masthead-text">
            場面の束、派生版、ワイルドカード候補を一つの作業面で扱います。
          </p>
        </div>
        <div className="mode-strip" aria-label="作業領域">
          <span className="mode-pill active">Prompt Studio</span>
          <span className="mode-pill">Wildcard Library</span>
          <span className="mode-pill">Builder</span>
        </div>
      </section>

      <section className="studio-summary" aria-label="現在の作業状態">
        <div>
          <span className="summary-label">選択中</span>
          <strong>{selectedSituation.title}</strong>
        </div>
        <div>
          <span className="summary-label">属性</span>
          <strong>{attributeLabels[selectedSituation.attribute]}</strong>
        </div>
        <div>
          <span className="summary-label">variant</span>
          <strong>{selectedSituation.variants.length} 件</strong>
        </div>
        <div>
          <span className="summary-label">wildcard</span>
          <strong>{wildcardGroups.length} groups / {skippedCanonicalWildcards.length} skipped</strong>
        </div>
        <div>
          <span className="summary-label">保存</span>
          <strong>localStorage</strong>
        </div>
      </section>

      <section className="workspace-panel">
        <aside className="sidebar" aria-label="situation 選択">
          <div className="sidebar-block">
            <p className="sidebar-title">属性タブ</p>
            <div className="category-list" role="tablist" aria-label="situation 属性">
              {(Object.keys(attributeLabels) as ImagePromptAttribute[]).map((attribute) => (
                <button
                  key={attribute}
                  type="button"
                  className={attribute === activeAttribute ? 'category-button active' : 'category-button'}
                  onClick={() => setActiveAttribute(attribute)}
                >
                  {attributeLabels[attribute]}
                </button>
              ))}
            </div>
          </div>

          <div className="sidebar-block">
            <p className="sidebar-title">situation</p>
            <div className="template-list">
              {visibleSituations.length > 0 ? (
                visibleSituations.map((situation) => (
                  <button
                    key={situation.id}
                    type="button"
                    className={situation.id === selectedSituationId ? 'template-card selected' : 'template-card'}
                    onClick={() => handleSelectSituation(situation)}
                  >
                    <span className="template-name">{situation.title}</span>
                    <span className="template-summary">{situation.summary}</span>
                    <span className="tag-list" aria-label={`${situation.title} のタグ`}>
                      {situation.tags.map((tag) => (
                        <span key={tag} className="tag-chip">
                          {tag}
                        </span>
                      ))}
                    </span>
                  </button>
                ))
              ) : (
                <div className="template-card custom-note">
                  <span className="template-name">未登録</span>
                  <span className="template-summary">
                    この属性の situation はまだありません。
                  </span>
                </div>
              )}
            </div>
          </div>
        </aside>

        <section className="editor-panel">
          <header className="editor-header">
            <div>
              <p className="editor-label">編集中の situation</p>
              <h2>{selectedSituation.title}</h2>
              <p className="situation-summary">{selectedSituation.summary}</p>
              <div className="editor-meta" aria-label="選択中タグ">
                {selectedSituation.tags.map((tag) => (
                  <span key={tag} className="tag-chip">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
            <div className="status-box" aria-live="polite">
              <span className={isCopying ? 'status-dot busy' : 'status-dot'}></span>
              {isCopying ? 'コピー中...' : status}
            </div>
          </header>

          <section className="variant-panel" aria-label="プロンプト版">
            <p className="field-label">プロンプト版</p>
            <div className="variant-list">
              {selectedSituation.variants.map((variant) => (
                <button
                  key={variant.id}
                  type="button"
                  className={variant.id === selectedVariantId ? 'variant-button active' : 'variant-button'}
                  onClick={() => handleSelectVariant(variant)}
                >
                  <span>{variant.label}</span>
                  <small>{variant.purpose}</small>
                </button>
              ))}
            </div>
          </section>

          <label className="editor-field">
            <span className="field-label">生成ツールへ渡す文面</span>
            <textarea
              value={draftPrompt}
              onChange={(event) => setDraftPrompt(event.target.value)}
              placeholder="ここに画像生成用プロンプトを入力します。"
              rows={10}
            />
          </label>

          <label className="editor-field compact-field">
            <span className="field-label">ネガティブプロンプト</span>
            <textarea
              value={draftNegativePrompt}
              onChange={(event) => setDraftNegativePrompt(event.target.value)}
              placeholder="避けたい要素や破綻しやすい要素を入力します。"
              rows={5}
            />
          </label>

          <div className="action-row">
            <button type="button" className="primary-button" onClick={handleCopy} disabled={isCopying}>
              {isCopying ? 'コピー中...' : 'この文面をコピー'}
            </button>
            <button type="button" className="secondary-button" onClick={handleCopyNegativePrompt} disabled={isCopying}>
              ネガティブをコピー
            </button>
            <button type="button" className="secondary-button" onClick={handleSaveVariant} disabled={isCopying}>
              選択中の版を保存
            </button>
            <button type="button" className="secondary-button" onClick={handleCopySituation} disabled={isCopying}>
              situation 全体をコピー
            </button>
            <button type="button" className="secondary-button" onClick={handleReset} disabled={isCopying}>
              選択中の版に戻す
            </button>
            <button type="button" className="secondary-button" onClick={handleResetStorage} disabled={isCopying}>
              保存データを初期化
            </button>
          </div>

          {errorMessage ? (
            <p className="error-banner" role="alert">
              {errorMessage}
            </p>
          ) : null}

          <section className="wildcard-panel" aria-label="ワイルドカード">
            <div className="wildcard-header">
              <div>
                <p className="editor-label">Wildcard</p>
                <h3>正本由来の差し替え候補</h3>
              </div>
              <div className="wildcard-source" aria-label="ワイルドカード取り込み元">
                <span>source</span>
                <code>{canonicalWildcardsSource}</code>
              </div>
              <div className="wildcard-import-summary" aria-label="ワイルドカード取り込み状況">
                <span>{wildcardGroups.length} groups imported</span>
                {skippedCanonicalWildcards.map((item) => (
                  <span key={item.reason}>
                    {item.reason}: {item.count}
                  </span>
                ))}
              </div>
            </div>
            <div className="wildcard-grid">
              {wildcardGroups.map((group) => (
                <article key={group.id} className="wildcard-card">
                  <div className="wildcard-card-header">
                    <div>
                      <p className="wildcard-token">{group.token}</p>
                      <h4>{group.label}</h4>
                    </div>
                    <button
                      type="button"
                      className="wildcard-copy-button"
                      onClick={() => handleCopyWildcardToken(group)}
                      disabled={isCopying}
                    >
                      構文をコピー
                    </button>
                  </div>
                  <div className="wildcard-card-meta">
                    <span>{group.sourceFileName}</span>
                    <span>{group.totalOptions} candidates</span>
                  </div>
                  {group.description ? <p className="wildcard-description">{group.description}</p> : null}
                  <div className="wildcard-options">
                    {group.options.map((option) => (
                      <span key={option} className="wildcard-option">
                        {option}
                      </span>
                    ))}
                  </div>
                </article>
              ))}
            </div>
          </section>
        </section>
      </section>
    </main>
  )
}

export default App
