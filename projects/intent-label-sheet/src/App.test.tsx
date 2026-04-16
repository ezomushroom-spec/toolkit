import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'
import App from './App'

describe('Intent Label Sheet', () => {
  it('filters labels in the standalone sheet', async () => {
    const user = userEvent.setup()
    render(<App />)

    expect(screen.getByRole('region', { name: '意図ラベルシート' })).toBeInTheDocument()

    const input = screen.getByPlaceholderText('ラベル名や使用場面で絞り込む')
    await user.clear(input)
    await user.type(input, 'snapshot')

    expect(screen.getByText('snapshot')).toBeInTheDocument()
    expect(screen.queryByText('UI監査')).not.toBeInTheDocument()
  })
})
