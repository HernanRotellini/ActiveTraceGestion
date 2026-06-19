import fs from 'node:fs'
import path from 'node:path'
import { describe, expect, it } from 'vitest'

function collectFiles(root: string): string[] {
  return fs.readdirSync(root, { withFileTypes: true }).flatMap((entry) => {
    const fullPath = path.join(root, entry.name)
    if (entry.isDirectory()) {
      return collectFiles(fullPath)
    }
    return fullPath.endsWith('.ts') || fullPath.endsWith('.tsx') ? [fullPath] : []
  })
}

describe('shared api route conventions', () => {
  it('does not duplicate the /api prefix inside services that use the shared api client', () => {
    const featuresRoot = path.resolve(process.cwd(), 'src/features')
    const srcRoot = path.resolve(process.cwd(), 'src')

    const offenders = collectFiles(featuresRoot)
      .filter((file) => file.includes(`${path.sep}services${path.sep}`))
      .filter((file) => {
        const source = fs.readFileSync(file, 'utf8')
        return source.includes("import api from '@/shared/services/api'") && /['"`]\/api\//.test(source)
      })
      .map((file) => path.relative(srcRoot, file))

    expect(offenders).toEqual([])
  })
})
