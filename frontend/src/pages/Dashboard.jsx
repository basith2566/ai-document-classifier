import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Bar, BarChart, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { getModelInfo, getStats } from '../api/client.js'
import { Alert, CategoryBadge, EmptyState, PageHeader, Spinner, StatCard } from '../components/ui.jsx'
import { categoryColor, formatDate, percent } from '../utils/format.js'

function ModelCard({ model }) {
  const m = model?.metrics
  return (
    <div className="card p-5">
      <h2 className="font-medium text-navy-900">Model evaluation</h2>
      {!model?.ready || !m ? (
        <p className="mt-3 text-sm text-navy-500">No trained model found. Run <code>python -m ml.train</code> in the backend.</p>
      ) : (
        <>
          <dl className="mt-4 grid grid-cols-2 gap-4 text-sm sm:grid-cols-4">
            <div><dt className="text-navy-500">Test accuracy</dt><dd className="text-lg font-semibold">{percent(m.test_accuracy)}</dd></div>
            <div><dt className="text-navy-500">Macro F1</dt><dd className="text-lg font-semibold">{percent(m.test_macro_f1)}</dd></div>
            <div><dt className="text-navy-500">Cross-validation</dt><dd className="text-lg font-semibold">{percent(m.cv_accuracy_mean)}</dd></div>
            <div><dt className="text-navy-500">Training set</dt><dd className="text-lg font-semibold">{m.n_train} docs</dd></div>
          </dl>
          <p className="mt-4 text-xs leading-relaxed text-navy-500">
            Measured on {m.n_test} held-out documents from <code>{m.dataset_file}</code>. The starter dataset is synthetic, so these
            scores are optimistic. Real-world accuracy will be lower. Results below{' '}
            {percent(model.confidence_threshold)} confidence are sent to manual review.
          </p>
        </>
      )}
    </div>
  )
}

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [model, setModel] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([getStats(), getModelInfo()])
      .then(([s, m]) => { setStats(s); setModel(m) })
      .catch((e) => setError(e.message))
  }, [])

  if (error) return <><PageHeader title="Dashboard" /><Alert title="Could not load the dashboard">{error}</Alert></>
  if (!stats) return <Spinner />

  const empty = stats.total_documents === 0

  return (
    <>
      <PageHeader
        title="Dashboard"
        subtitle="An overview of everything classified so far."
        actions={<Link to="/upload" className="btn-primary">Upload documents</Link>}
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Total documents" value={stats.total_documents} />
        <StatCard label="Classified automatically" value={stats.auto_classified} hint="Confidence above threshold" />
        <StatCard label="Needs manual review" value={stats.needs_review} hint="Low confidence or too short" />
        <StatCard label="Average confidence" value={stats.average_confidence == null ? '–' : percent(stats.average_confidence)} />
      </div>

      {empty ? (
        <div className="card mt-6">
          <EmptyState
            title="No documents yet"
            action={<Link to="/upload" className="btn-primary">Upload your first document</Link>}
          >
            Charts and recent activity will appear here after you classify a document.
          </EmptyState>
        </div>
      ) : (
        <div className="mt-6 grid gap-6 lg:grid-cols-5">
          <div className="card p-5 lg:col-span-2">
            <h2 className="font-medium">Category distribution</h2>
            <div className="mt-2 h-56">
              <ResponsiveContainer>
                <PieChart>
                  <Pie data={stats.category_distribution} dataKey="count" nameKey="category" innerRadius={55} outerRadius={85} paddingAngle={2}>
                    {stats.category_distribution.map((d) => <Cell key={d.category} fill={categoryColor(d.category)} />)}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <ul className="mt-2 space-y-1.5 text-sm">
              {stats.category_distribution.map((d) => (
                <li key={d.category} className="flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <span className="h-2.5 w-2.5 rounded-sm" style={{ backgroundColor: categoryColor(d.category) }} />
                    {d.category}
                  </span>
                  <span className="tabular-nums text-navy-600">{d.count}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="card p-5 lg:col-span-3">
            <h2 className="font-medium">Documents per day (last 7 days, UTC)</h2>
            <div className="mt-4 h-64">
              <ResponsiveContainer>
                <BarChart data={stats.daily_activity}>
                  <XAxis dataKey="date" tickFormatter={(d) => d.slice(5)} tick={{ fontSize: 12 }} stroke="#97aac5" />
                  <YAxis allowDecimals={false} tick={{ fontSize: 12 }} stroke="#97aac5" width={28} />
                  <Tooltip cursor={{ fill: '#f1f4f9' }} />
                  <Bar dataKey="count" name="Documents" fill="#12203a" radius={[3, 3, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="card lg:col-span-5">
            <div className="flex items-center justify-between border-b border-navy-100 px-5 py-4">
              <h2 className="font-medium">Recent activity</h2>
              <Link to="/history" className="text-sm font-medium text-brand hover:underline">View all</Link>
            </div>
            <ul className="divide-y divide-navy-100">
              {stats.recent_activity.map((doc) => (
                <li key={doc.id}>
                  <Link to={`/results/${doc.id}`} className="flex flex-wrap items-center justify-between gap-2 px-5 py-3 hover:bg-navy-50">
                    <span className="min-w-0 truncate text-sm font-medium">{doc.filename}</span>
                    <span className="flex items-center gap-3">
                      <CategoryBadge doc={doc} />
                      <span className="hidden text-xs text-navy-400 sm:inline">{formatDate(doc.created_at)}</span>
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      <div className="mt-6"><ModelCard model={model} /></div>
    </>
  )
}
