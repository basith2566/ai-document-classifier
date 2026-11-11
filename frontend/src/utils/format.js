export const NEEDS_REVIEW = 'Needs Manual Review'

export function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

// Timestamps are stored in UTC without a "Z"; add it so the browser converts to local time.
export function formatDate(iso) {
  const date = new Date(iso.endsWith('Z') || iso.includes('+') ? iso : `${iso}Z`)
  return date.toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' })
}

export const percent = (value) => `${Math.round(value * 100)}%`

const KNOWN = {
  Resume: '#2f5bea',
  Invoice: '#0f9d8a',
  'Research Paper': '#7c4dcc',
  'Legal Document': '#b45309',
  Email: '#0891b2',
  Report: '#4d6a9a',
  Other: '#8b97a8',
  [NEEDS_REVIEW]: '#d97706',
}
const FALLBACK = ['#be185d', '#15803d', '#a21caf', '#0369a1', '#a16207', '#4338ca']

// New categories added by retraining get a stable colour derived from their name.
export function categoryColor(name) {
  if (KNOWN[name]) return KNOWN[name]
  let hash = 0
  for (const ch of name) hash = (hash * 31 + ch.charCodeAt(0)) >>> 0
  return FALLBACK[hash % FALLBACK.length]
}
