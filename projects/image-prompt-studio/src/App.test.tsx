import { cleanup, render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it } from 'vitest'
import App from './App'

afterEach(() => {
  cleanup()
  window.localStorage.clear()
})

describe('App', () => {
  it('restores the selected image prompt variant after editing', async () => {
    const user = userEvent.setup()
    render(<App />)

    const textarea = screen.getByLabelText('生成ツールへ渡す文面')
    await user.clear(textarea)
    await user.type(textarea, 'テスト用プロンプト')
    await user.click(screen.getByRole('button', { name: '選択中の版に戻す' }))

    expect(screen.getByDisplayValue(/a quiet girl reading a book by the window/)).toBeInTheDocument()
    expect(screen.getByText('選択中のプロンプトに戻しました')).toBeInTheDocument()
  })

  it('separates negative prompt from the main prompt', async () => {
    const user = userEvent.setup()
    render(<App />)

    const variantPanel = screen.getByLabelText('プロンプト版')
    await user.click(within(variantPanel).getByRole('button', { name: /ネガティブ/ }))

    expect(screen.getByLabelText('生成ツールへ渡す文面')).toHaveValue('')
    expect(screen.getByLabelText('ネガティブプロンプト')).toHaveValue(
      'low quality, blurry, bad anatomy, extra fingers, missing fingers, distorted hands, messy background, harsh shadow, overexposed face, text, watermark',
    )
  })

  it('saves the selected variant to localStorage', async () => {
    const user = userEvent.setup()
    const { unmount } = render(<App />)

    const textarea = screen.getByLabelText('生成ツールへ渡す文面')
    await user.clear(textarea)
    await user.type(textarea, 'saved prompt text')
    await user.clear(screen.getByLabelText('ネガティブプロンプト'))
    await user.type(screen.getByLabelText('ネガティブプロンプト'), 'saved negative text')
    await user.click(screen.getByRole('button', { name: '選択中の版を保存' }))
    expect(screen.getByText('選択中の版を保存しました')).toBeInTheDocument()

    unmount()
    render(<App />)

    expect(screen.getByLabelText('生成ツールへ渡す文面')).toHaveValue('saved prompt text')
    expect(screen.getByLabelText('ネガティブプロンプト')).toHaveValue('saved negative text')
  })

  it('switches situations when the attribute tab changes', async () => {
    const user = userEvent.setup()
    render(<App />)

    const attributeTabs = screen.getByRole('tablist', { name: 'situation 属性' })

    await user.click(within(attributeTabs).getByRole('button', { name: '場所' }))
    await user.click(screen.getByRole('button', { name: /午後の温室/ }))

    expect(screen.getByRole('heading', { level: 2, name: '午後の温室' })).toBeInTheDocument()
    expect(screen.getByDisplayValue(/inside a quiet greenhouse in the afternoon/)).toBeInTheDocument()
  })

  it('switches prompt variants inside the selected situation', async () => {
    const user = userEvent.setup()
    render(<App />)

    const variantPanel = screen.getByLabelText('プロンプト版')
    await user.click(within(variantPanel).getByRole('button', { name: /光重視/ }))

    expect(screen.getByDisplayValue(/sunbeams through thin curtains/)).toBeInTheDocument()
    expect(screen.getByText('「光重視」を編集中')).toBeInTheDocument()
  })

  it('renders wildcard groups', () => {
    render(<App />)

    const wildcardPanel = screen.getByLabelText('ワイルドカード')

    expect(wildcardPanel).toBeInTheDocument()
    expect(within(wildcardPanel).getByText('__tipo_location__')).toBeInTheDocument()
    expect(within(wildcardPanel).getByText('indoors')).toBeInTheDocument()
    expect(within(wildcardPanel).getByText('E:\\自作アプリ集\\新しいフォルダー (2)\\data\\wildcards')).toBeInTheDocument()
    expect(within(wildcardPanel).getByText('汎用候補の確認が未完了のため初回除外: 15')).toBeInTheDocument()
    expect(within(wildcardPanel).getAllByRole('button', { name: '構文をコピー' })).toHaveLength(3)
  })
})
