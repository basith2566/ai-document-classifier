import { useEffect, useState } from 'react'
import { Link, Navigate, useNavigate, useParams } from 'react-router-dom'
import { Copy, Trash2 } from 'lucide-react'
import { deleteDocument, getDocument, listDocuments } from '../api/client.js'
import { Alert, CategoryBadge, ConfidenceBar, EmptyState, PageHeader, Spinner } from '../components/ui.jsx'
import { categoryColor, formatBytes, formatDate, percent } from '../utils/format.js'

const PREVIEW_CHARS = 1500

function ExtractedText({ text }) {
  const [expanded, setExpanded] = useState(false)
  const [copied, setCopied] = useState(false)
  const long = text.length > PREVIEW_CHARS
  const shown = expanded || !long ? text : `${text.slice(0, PREVIEW_CHARS)}…`

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    } catch { /* clipboard unavailable */ }
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between border-b border-navy-100 px-5 py-3">
        <h2 className="font-medium">Extracted text</h2>
        <button onClick={copy} className="btn-secondary !px-3 !py-1.5"><Copy className="h-3.5 w-3.5" /> {copied ? 'Copied' : 'Copy'}</button>
      </div>
      <pre className="max-h-[28rem] overflow-auto whitespace-pre-wrap break-words p-5 font-sans text-sm leading-relaxed text-navy-800">{shown}</pre>
      {long && (
        <div className="border-t border-navy-100 px-5 py-3">
          <button onClick={() => setExpanded(!expanded)} className="text-sm font-medium text-brand hover:underline">
            {expanded ? 'Show preview only' : `Show full text (${text.length.toLocaleString()} characters)`}
          </button>
        </div>
      )}
    </div>
  )
}

// /results (no id) opens the most recent document.
function LatestRedirect() {
  const [target, setTarget] = useState(undefined)
  const [error, setError] = useState('')
  useEffect(() => {
    listDocuments({ pageSize: 1 })
      .then((r) => setTarget(r.items[0]?.id ?? null))
      .catch((e) => setError(e.message))
  }, [])
  if (error) return <><PageHeader title="Results" /><Alert title="Could not load results">{error}</Alert></>
  if (target === undefined) return <Spinner />
  if (target === null) {
    return (
      <>
        <PageHeader title="Results" />
        <div className="card">
          <EmptyState title="Nothing to show yet" action={<Link to="/upload" className="btn-primary">Upload a document</Link>}>
            Classification results appear here after you upload a document.
          </EmptyState>
        </div>
      </>
    )
  }
  return <Navigate to={`/results/${target}`} replace />
}

export default function Results() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [doc, setDoc] = useState(null)
  const [error, setError] = useState('')
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    if (!id) return
    setDoc(null)
    setError('')
    getDocument(id).then(setDoc).catch((e) => setError(e.message))
  }, [id])

  if (!id) return <LatestRedirect />
  if (error) return <><PageHeader title="Results" /><Alert title="Could not load this document">{error}</Alert><div className="mt-4"><Link to="/history" className="btn-secondary">Back to history</Link></div></>
  if (!doc) return <Spinner />

  const remove = async () => {
    if (!window.confirm(`Delete "${doc.filename}" from your history?`)) return
    setDeleting(true)
    try {
      await deleteDocument(doc.id)
      navigate('/history')
    } catch (e) {
      setError(e.message)
      setDeleting(false)
    }
  }

  return (
    <>
      <PageHeader
        title={doc.filename}
        subtitle={`Classified ${formatDate(doc.created_at)}`}
        actions={<button className="btn-danger" onClick={remove} disabled={deleting}><Trash2 className="h-4 w-4" /> Delete</button>}
      />

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="card p-5 lg:col-span-2">
          <p className="text-sm text-navy-500">Predicted category</p>
          <div className="mt-2"><CategoryBadge doc={doc} size="lg" /></div>

          {doc.needs_review && (
            <div className="mt-4">
              <Alert type="warning" title="This result is not reliable enough to use automatically">
                {doc.review_reason} Closest match: <strong>{doc.category}</strong> ({percent(doc.confidence)}). Please check the document yourself.
              </Alert>
            </div>
          )}

          <p className="mt-6 text-sm text-navy-500">Confidence</p>
          <div className="mt-1.5 max-w-md"><ConfidenceBar value={doc.confidence} muted={doc.needs_review} /></div>

          <p className="mt-6 text-sm text-navy-500">Score for every category</p>
          <ul className="mt-2 space-y-2">
            {doc.probabilities.map((p) => (
              <li key={p.category} className="grid grid-cols-[8rem_1fr_3rem] items-center gap-3 text-sm">
                <span className="truncate">{p.category}</span>
                <div className="h-2 overflow-hidden rounded-full bg-navy-100">
                  <div className="h-full rounded-full" style={{ width: `${p.probability * 100}%`, backgroundColor: categoryColor(p.category) }} />
                </div>
                <span className="text-right tabular-nums text-navy-600">{percent(p.probability)}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="card h-fit p-5">
          <h2 className="font-medium">Document details</h2>
          <dl className="mt-4 space-y-3 text-sm">
            {[
              ['File type', doc.file_type.toUpperCase()],
              ['File size', formatBytes(doc.file_size)],
              ['Word count', doc.word_count.toLocaleString()],
              ['Status', doc.needs_review ? 'Needs manual review' : 'Classified'],
            ].map(([k, v]) => (
              <div key={k} className="flex justify-between gap-4"><dt className="text-navy-500">{k}</dt><dd className="font-medium">{v}</dd></div>
            ))}
          </dl>
        </div>

        <div className="lg:col-span-3"><ExtractedText text={doc.extracted_text} /></div>
      </div>
    </>
  )
}
