export {}

declare global {
  interface Window {
    intentLabelDesktop?: {
      writeClipboardText: (text: string) => Promise<void>
    }
  }
}
