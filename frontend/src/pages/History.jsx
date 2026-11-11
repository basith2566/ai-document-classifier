import { useCallback, useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Search, Trash2 } from 'lucide-react'
import { deleteDocument, getModelInfo, listDocuments } from '../api/client.js'
import { Alert, CategoryBadge, ConfidenceBar, EmptyState, PageHeader, Spinner } from '../components/ui.jsx'
import { formatBytes, formatDate, NEEDS_REVIEW } from '../utils/format.js'

const PAGE_SIZE = 15

export default function History() {
  const navigate = useNavigate()
  const [search, setSearch] = useState('')
  const [query, setQuery] = useState('')
  const [category, setCategory] = useState('')
  const [page, setPage] = useState(1)
  const [labels, setLabels] = useState([])
  const [data, setData] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => { getModelInfo().then((m) => setLabels(m.labels)).catch(() => {}) }, [])

  // Wait 300 ms after typing stops before searching.
  useEffect(() => {
    const timer = setTimeout(() => { setQuery(search); setPage(1) }, 300)
    return () => clearTimeout(timer)
  }, [search])

  const load = useCallback(() => {
    setError('')
    listDocuments({ search: query, category, page, pageSize: PAGE_SIZE })
      .then(setData)
      .catch((e) => setError(e.message))
  }, [query, category, page])

  useEffect(load, [load])

  const remove = async (doc) => {
    if (!window.confirm(`Delete "${doc.filename}" from your history?`)) return
    try {
      await deleteDocument(doc.id)
      // Step back a page if we just removed the last row on this one.
      if (data.items.length === 1 && page > 1) setPage(page - 1)
      else load()
    } catch (e) {
      setError(e.message)
    }
  }

  const totalPages = data ? Math.max(1, Math.ceil(data.total / PAGE_SIZE)) : 1
  const filtering = Boolean(query || category)

  return (
    <>
      <PageHeader title="History" subtitle="Search, filter and manage previous classifications." />

      <div className="mb-4 flex flex-col gap-3 sm:flex-row">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-2.5 h-4 w-4 text-navy-300" />
          <input
            className="input pl-9"
            placeholder="Search by file name, category or document text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            aria-label="Search history"
          />
        </div>
        <select
          className="input sm:w-56"
          value={category}
          onChange={(e) => { setCategory(e.target.value); setPage(1) }}
          aria-label="Filter by category"
        >
          <option value="">All categories</option>
          {labels.map((l) => <option key={l} value={l}>{l}</option>)}
          <option value={NEEDS_REVIEW}>{NEEDS_REVIEW}</option>
        </select>
      </div>

      {error && <div className="mb-4"><Alert title="Something went wrong">{error}</Alert></div>}

      <div className="card overflow-hidden">
        {!data && !error ? (
          <Spinner />
        ) : data && data.items.length === 0 ? (
          <EmptyState
            title={filtering ? 'No matching documents' : 'No documents yet'}
            action={!filtering && <Link to="/upload" className="btn-primary">Upload a document</Link>}
          >
            {filtering ? 'Try a different search or clear the category filter.' : 'Classified documents will be listed here.'}
          </EmptyState>
        ) : data ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-navy-100 bg-navy-50 text-navy-500">
                <tr>
                  <th className="px-4 py-3 font-medium">Document</th>
                  <th className="px-4 py-3 font-medium">Category</th>
                  <th className="hidden w-40 px-4 py-3 font-medium md:table-cell">Confidence</th>
                  <th className="hidden px-4 py-3 font-medium lg:table-cell">Classified</th>
                  <th className="w-12 px-4 py-3"><span className="sr-only">Actions</span></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-navy-100">
                {data.items.map((doc) => (
                  <tr key={doc.id} className="cursor-pointer hover:bg-navy-50" onClick={() => navigate(`/results/${doc.id}`)}>
                    <td className="max-w-[16rem] px-4 py-3">
                      <Link to={`/results/${doc.id}`} onClick={(e) => e.stopPropagation()} className="block truncate font-medium hover:text-brand">{doc.filename}</Link>
                      <span className="text-xs text-navy-400">{doc.file_type.toUpperCase()} · {formatBytes(doc.file_size)}</span>
                    </td>
                    <td className="px-4 py-3"><CategoryBadge doc={doc} /></td>
                    <td className="hidden px-4 py-3 md:table-cell"><ConfidenceBar value={doc.confidence} muted={doc.needs_review} /></td>
                    <td className="hidden whitespace-nowrap px-4 py-3 text-navy-500 lg:table-cell">{formatDate(doc.created_at)}</td>
                    <td className="px-4 py-3 text-right">
                      <button
                        onClick={(e) => { e.stopPropagation(); remove(doc) }}
                        aria-label={`Delete ${doc.filename}`}
                        className="rounded p-1.5 text-navy-400 hover:bg-red-50 hover:text-red-600"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : null}

        {data && data.total > PAGE_SIZE && (
          <div className="flex items-center justify-between border-t border-navy-100 px-4 py-3 text-sm">
            <span className="text-navy-500">Page {page} of {totalPages} · {data.total} documents</span>
            <div className="flex gap-2">
              <button className="btn-secondary !py-1.5" disabled={page <= 1} onClick={() => setPage(page - 1)}>Previous</button>
              <button className="btn-secondary !py-1.5" disabled={page >= totalPages} onClick={() => setPage(page + 1)}>Next</button>
            </div>
          </div>
        )}
      </div>
    </>
  )
}
