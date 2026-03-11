import { useState, useEffect, useCallback } from 'react'
import { listMemory, deleteMemoryEntry } from '../api/client'
import { Brain, Trash2, RefreshCw } from 'lucide-react'

function EntryCard({ entry, onDelete }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="border border-gray-800 rounded-lg p-4 hover:border-gray-700 transition-colors">
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="badge bg-cortex-900 text-cortex-300">{entry.entry_type}</span>
            {entry.tags?.map((tag) => (
              <span key={tag} className="badge bg-gray-800 text-gray-400">{tag}</span>
            ))}
          </div>
          <p className="text-gray-400 text-xs">
            Goal ID: {entry.goal_id ?? '—'} · {new Date(entry.created_at).toLocaleString()}
          </p>
        </div>
        <div className="flex gap-2 ml-2">
          <button
            onClick={() => setExpanded((v) => !v)}
            className="text-gray-400 hover:text-white text-xs px-2 py-1 rounded bg-gray-800"
          >
            {expanded ? 'Hide' : 'Show'}
          </button>
          <button
            onClick={() => onDelete(entry.id)}
            className="text-red-500 hover:text-red-400 p-1 rounded"
          >
            <Trash2 size={14} />
          </button>
        </div>
      </div>

      {expanded && (
        <pre className="mt-3 bg-gray-950 rounded p-3 text-xs text-gray-300 overflow-x-auto whitespace-pre-wrap">
          {JSON.stringify(entry.content, null, 2)}
        </pre>
      )}
    </div>
  )
}

export default function MemoryLogs() {
  const [entries, setEntries] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('')

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const { data } = await listMemory({ limit: 100 })
      setEntries(data)
    } catch {
      // ignore
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this memory entry?')) return
    try {
      await deleteMemoryEntry(id)
      setEntries((prev) => prev.filter((e) => e.id !== id))
    } catch {
      // ignore
    }
  }

  const filtered = filter
    ? entries.filter(
        (e) =>
          e.entry_type.includes(filter) ||
          e.tags?.some((t) => t.includes(filter)) ||
          JSON.stringify(e.content).toLowerCase().includes(filter.toLowerCase())
      )
    : entries

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-cortex-400 flex items-center gap-2">
          <Brain size={20} /> Memory Logs
        </h2>
        <button onClick={load} className="btn-secondary flex items-center gap-1 text-sm py-1 px-3">
          <RefreshCw size={14} /> Refresh
        </button>
      </div>

      <input
        type="text"
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
        placeholder="Filter by type, tag or content…"
        className="w-full mb-4 bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-cortex-500"
      />

      {loading ? (
        <p className="text-gray-500 text-sm">Loading memory…</p>
      ) : filtered.length === 0 ? (
        <p className="text-gray-500 text-sm">No memory entries found.</p>
      ) : (
        <div className="space-y-3 max-h-96 overflow-y-auto pr-1">
          {filtered.map((e) => (
            <EntryCard key={e.id} entry={e} onDelete={handleDelete} />
          ))}
        </div>
      )}
    </div>
  )
}
