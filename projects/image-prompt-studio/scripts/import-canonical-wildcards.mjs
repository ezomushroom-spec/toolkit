import { promises as fs } from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const projectRoot = path.resolve(__dirname, '..')
const canonicalWildcardsDir = 'E:\\自作アプリ集\\新しいフォルダー (2)\\data\\wildcards'
const outputDir = path.join(projectRoot, 'src', 'generated')
const outputFile = path.join(outputDir, 'canonicalWildcards.ts')
const maxPreviewOptions = 80
const allowedTextFiles = new Set([
  'school komono.txt',
  'tipo_location.txt',
  'view.txt',
])

function normalizeWildcardName(fileName) {
  return path.basename(fileName, path.extname(fileName)).replace(/^__(.+)__$/, '$1')
}

function toToken(name) {
  return `__${name}__`
}

function parseWildcardText(raw) {
  const lines = raw
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)

  const descriptionLine = lines.find((line) => line.startsWith('#'))
  const options = lines.filter((line) => !line.startsWith('#'))

  return {
    description: descriptionLine ? descriptionLine.replace(/^#\s*/, '') : '',
    options,
  }
}

async function loadWildcardFiles() {
  const entries = await fs.readdir(canonicalWildcardsDir, { withFileTypes: true })
  const imported = []
  const skippedSummary = new Map()

  for (const entry of entries) {
    if (!entry.isFile()) {
      continue
    }

    const ext = path.extname(entry.name).toLowerCase()
    const sourcePath = path.join(canonicalWildcardsDir, entry.name)
    const stat = await fs.stat(sourcePath)

    if (ext !== '.txt') {
      const reason = 'txt以外のため初回除外'
      skippedSummary.set(reason, (skippedSummary.get(reason) ?? 0) + 1)
      continue
    }

    if (!allowedTextFiles.has(entry.name)) {
      const reason = '汎用候補の確認が未完了のため初回除外'
      skippedSummary.set(reason, (skippedSummary.get(reason) ?? 0) + 1)
      continue
    }

    const raw = await fs.readFile(sourcePath, 'utf8')
    const name = normalizeWildcardName(entry.name)
    const parsed = parseWildcardText(raw)

    imported.push({
      id: name,
      token: toToken(name),
      label: name,
      description: parsed.description,
      sourceFileName: entry.name,
      sourceSize: stat.size,
      totalOptions: parsed.options.length,
      options: parsed.options.slice(0, maxPreviewOptions),
    })
  }

  imported.sort((left, right) => left.label.localeCompare(right.label, 'ja'))
  const skipped = Array.from(skippedSummary, ([reason, count]) => ({ reason, count }))

  return { imported, skipped }
}

async function writeOutput() {
  const { imported, skipped } = await loadWildcardFiles()
  const skippedFileCount = skipped.reduce((total, item) => total + item.count, 0)
  const content = `export type CanonicalWildcardGroup = {
  id: string
  token: string
  label: string
  description: string
  sourceFileName: string
  sourceSize: number
  totalOptions: number
  options: string[]
}

export type SkippedCanonicalWildcardSummary = {
  reason: string
  count: number
}

export const canonicalWildcardsSource = ${JSON.stringify(canonicalWildcardsDir)} as const

export const canonicalWildcards = ${JSON.stringify(imported, null, 2)} satisfies CanonicalWildcardGroup[]

export const skippedCanonicalWildcards = ${JSON.stringify(skipped, null, 2)} satisfies SkippedCanonicalWildcardSummary[]
`

  await fs.mkdir(outputDir, { recursive: true })
  await fs.writeFile(outputFile, content, 'utf8')
  console.log(`Imported ${imported.length} canonical wildcard groups -> ${outputFile}`)
  console.log(`Skipped ${skippedFileCount} canonical wildcard files across ${skipped.length} reasons`)
}

writeOutput().catch((error) => {
  console.error(error)
  process.exitCode = 1
})
