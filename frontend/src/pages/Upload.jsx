import { useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { FileText, Loader2, UploadCloud, X } from 'lucide-react'
import { uploadDocuments } from '../api/client.js'
import { Alert, CategoryBadge, ConfidenceBar, PageHeader } from '../components/ui.jsx'
import { formatBytes } from '../utils/format.js'

const ALLOWED = ['.pdf', '.docx', '.txt']
const MAX_MB = 10

function validate(file) {
  const ext = file.name.slice(file.name.lastIndexOf('.')).toLowerCase()
  if (!ALLOWED.includes(ext)) return 'Unsupported type. Use PDF, DOCX or TXT.'
  if (file.size === 0) return 'The file is empty.'
  if (file.size > MAX_MB * 1024 * 1024) return `Larger than ${MAX_MB} MB.`
  return null
}

export default function Upload() {
  const [files, setFiles] = useState([])
  const [dragging, setDragging] = useState(false)
  const [phase, setPhase] = useState('idle') // idle | uploading | processing | done
  const [progress, setProgress] = useState(0)
  const [results, setResults] = useState([])
  const [error, setError] = useState('')
  const inputRef = useRef(null)

  const addFiles = (list) => {
    const incoming = Array.from(list).map((file) => ({ file, problem: validate(file) }))
    setFiles((current) => {
      const known = new Set(current.map((f) => `${f.file.name}:${f.file.size}`))
      return [...current, ...incoming.filter((f) => !known.has(`${f.file.name}:${f.file.size}`))]
    })
  }

  const removeFile = (index) => setFiles((current) => current.filter((_, i) => i !== index))
  const valid = files.filter((f) => !f.problem)
  const busy = phase === 'uploading' || phase === 'processing'

  const submit = async () => {
    setError('')
    setProgress(0)
    setPhase('uploading')
    try {
      const response = await uploadDocuments(valid.map((f) => f.file), (p) => {
        setProgress(p)
        if (p >= 100) setPhase('processing')
      })
      setResults(response.results)
      setPhase('done')
    } catch (e) {
      setError(e.message)
      setPhase('idle')
    }
  }

  const reset = () => { setFiles([]); setResults([]); setPhase('idle'); setProgress(0); setError('') }

  const succeeded = results.filter((r) => r.success).length
  const failed = results.length - succeeded

  return (
    <>
      <PageHeader title="Upload documents" subtitle="PDF, DOCX or TXT files, up to 10 MB each. You can upload several at once." />

      {phase !== 'done' && (
        <>
          <div
            onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
            onDragLeave={() => setDragging(false)}
            onDrop={(e) => { e.preventDefault(); setDragging(false); if (!busy) addFiles(e.dataTransfer.files) }}
            onClick={() => !busy && inputRef.current?.click()}
            onKeyDown={(e) => { if ((e.key === 'Enter' || e.key === ' ') && !busy) inputRef.current?.click() }}
            role="button"
            tabIndex={0}
            className={`flex cursor-pointer flex-col items-center rounded-lg border-2 border-dashed px-6 py-12 text-center transition-colors ${
              dragging ? 'border-brand bg-brand-soft' : 'border-navy-200 bg-white hover:border-navy-300'
            }`}
          >
            <UploadCloud className="h-9 w-9 text-navy-400" />
            <p className="mt-3 font-medium">Drag files here, or click to browse</p>
            <p className="mt-1 text-sm text-navy-500">Text-based documents only. Scanned images are not supported.</p>
            <input
              ref={inputRef}
              type="file"
              multiple
              accept=".pdf,.docx,.txt"
              className="hidden"
              onChange={(e) => { addFiles(e.target.files); e.target.value = '' }}
            />
          </div>

          {error && <div className="mt-4"><Alert title="Upload failed">{error}</Alert></div>}

          {files.length > 0 && (
            <div className="card mt-6">
              <ul className="divide-y divide-navy-100">
                {files.map(({ file, problem }, i) => (
                  <li key={`${file.name}-${i}`} className="flex items-center gap-3 px-4 py-3">
                    <FileText className="h-4 w-4 shrink-0 text-navy-400" />
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium">{file.name}</p>
                      <p className={`text-xs ${problem ? 'text-red-600' : 'text-navy-400'}`}>{problem || formatBytes(file.size)}</p>
                    </div>
                    {!busy && (
                      <button onClick={() => removeFile(i)} aria-label={`Remove ${file.name}`} className="rounded p-1 text-navy-400 hover:bg-navy-50 hover:text-navy-700">
                        <X className="h-4 w-4" />
                      </button>
                    )}
                  </li>
                ))}
              </ul>

              <div className="border-t border-navy-100 p-4">
                {busy ? (
                  <div role="status">
                    <div className="mb-2 flex items-center gap-2 text-sm text-navy-600">
                      <Loader2 className="h-4 w-4 animate-spin" />
                      {phase === 'uploading' ? `Uploading… ${progress}%` : 'Extracting text and classifying…'}
                    </div>
                    <div className="h-2 overflow-hidden rounded-full bg-navy-100">
                      <div
                        className={`h-full rounded-full bg-navy-900 transition-all ${phase === 'processing' ? 'w-full animate-pulse' : ''}`}
                        style={phase === 'uploading' ? { width: `${progress}%` } : undefined}
                      />
                    </div>
                  </div>
                ) : (
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <p className="text-sm text-navy-500">
                      {valid.length} of {files.length} file{files.length === 1 ? '' : 's'} ready
                    </p>
                    <div className="flex gap-2">
                      <button className="btn-secondary" onClick={reset}>Clear</button>
                      <button className="btn-primary" disabled={valid.length === 0} onClick={submit}>
                        Classify {valid.length || ''} document{valid.length === 1 ? '' : 's'}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </>
      )}

      {phase === 'done' && (
        <>
          <Alert
            type={failed === 0 ? 'success' : succeeded === 0 ? 'error' : 'warning'}
            title={`${succeeded} classified${failed ? `, ${failed} failed` : ''}`}
          >
            {failed > 0 && 'Files that failed were not saved. See the reason next to each file.'}
          </Alert>
          <div className="card mt-6">
            <ul className="divide-y divide-navy-100">
              {results.map((r, i) => (
                <li key={i} className="flex flex-wrap items-center justify-between gap-3 px-4 py-4">
                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium">{r.filename}</p>
                    {!r.success && <p className="mt-0.5 text-sm text-red-600">{r.error}</p>}
                  </div>
                  {r.success && (
                    <div className="flex flex-wrap items-center gap-4">
                      <CategoryBadge doc={r.document} />
                      <div className="w-32"><ConfidenceBar value={r.document.confidence} muted={r.document.needs_review} /></div>
                      <Link to={`/results/${r.document.id}`} className="text-sm font-medium text-brand hover:underline">View details</Link>
                    </div>
                  )}
                </li>
              ))}
            </ul>
          </div>
          <div className="mt-6 flex gap-2">
            <button className="btn-primary" onClick={reset}>Upload more</button>
            <Link to="/history" className="btn-secondary">Go to history</Link>
          </div>
        </>
      )}
    </>
  )
}
