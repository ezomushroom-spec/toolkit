import { cleanup, render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it } from 'vitest'
import App from './App'

afterEach(() => {
  cleanup()
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
    expect(within(wildcardPanel).getByText('__lighting__')).toBeInTheDocument()
    expect(within(wildcardPanel).getByText('soft morning light')).toBeInTheDocument()
    expect(within(wildcardPanel).getByText('__camera__')).toBeInTheDocument()
  })
})
