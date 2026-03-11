import { useState, useEffect, useCallback } from 'react'
import { getHealth, getAnalyticsSummary } from '../api/client'
import { Activity, CheckCircle, XCircle } from 'lucide-react'

export default function SystemStatus() {
  const [health, setHealth] = useState(null)
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const [{ data: h }, { data: s }] = await Promise.all([
        getHealth(),
        getAnalyticsSummary(),
      ])
      setHealth(h)
      setSummary(s)
    } catch (err) {
      setHealth({ status: 'error', version: '—' })
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  const isOk = health?.status === 'ok'

  return (
    <div className="card">
      <h2 className="text-xl font-bold text-cortex-400 flex items-center gap-2 mb-4">
        <Activity size={20} /> System Status
      </h2>

      {loading ? (
        <p className="text-gray-500 text-sm">Checking…</p>
      ) : (
        <div className="space-y-3">
          <div className="flex items-center gap-3">
            {isOk
              ? <CheckCircle size={18} className="text-green-400" />
              : <XCircle size={18} className="text-red-400" />
            }
            <div>
              <p className="text-sm font-semibold text-white">
                Backend API &nbsp;
                <span className={isOk ? 'text-green-400' : 'text-red-400'}>
                  {isOk ? 'Online' : 'Offline'}
                </span>
              </p>
              <p className="text-xs text-gray-500">Version: {health?.version}</p>
            </div>
          </div>

          {summary && (
            <div className="grid grid-cols-2 gap-3 mt-2">
              {[
                { label: 'Goals', value: summary.total_goals },
                { label: 'Tasks', value: summary.total_tasks },
                { label: 'Actions', value: summary.total_actions },
                { label: 'Avg Tasks/Goal', value: summary.average_tasks_per_goal },
              ].map(({ label, value }) => (
                <div key={label} className="bg-gray-800 rounded p-3">
                  <p className="text-xl font-bold text-white">{value}</p>
                  <p className="text-xs text-gray-500">{label}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
