import { useState, useEffect, useCallback } from 'react'
import { getAnalyticsSummary, getLearningInsights } from '../api/client'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
} from 'recharts'
import { TrendingUp, RefreshCw } from 'lucide-react'

const STATUS_COLORS = {
  pending:   '#854d0e',
  planning:  '#1d4ed8',
  executing: '#7e22ce',
  completed: '#166534',
  failed:    '#991b1b',
}

export default function Analytics() {
  const [summary, setSummary] = useState(null)
  const [insights, setInsights] = useState(null)
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const [{ data: s }, { data: i }] = await Promise.all([
        getAnalyticsSummary(),
        getLearningInsights(),
      ])
      setSummary(s)
      setInsights(i)
    } catch {
      // ignore
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  if (loading) return <div className="card"><p className="text-gray-500">Loading analytics…</p></div>
  if (!summary) return null

  const goalChartData = Object.entries(summary.goals_by_status).map(([name, value]) => ({ name, value }))
  const taskChartData = Object.entries(summary.tasks_by_status).map(([name, value]) => ({ name, value }))

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-cortex-400 flex items-center gap-2">
          <TrendingUp size={20} /> Performance Analytics
        </h2>
        <button onClick={load} className="btn-secondary flex items-center gap-1 text-sm py-1 px-3">
          <RefreshCw size={14} /> Refresh
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
        {[
          { label: 'Total Goals',   value: summary.total_goals },
          { label: 'Total Tasks',   value: summary.total_tasks },
          { label: 'Total Actions', value: summary.total_actions },
          { label: 'Success Rate',  value: `${(summary.success_rate * 100).toFixed(1)}%` },
        ].map(({ label, value }) => (
          <div key={label} className="bg-gray-800 rounded-lg p-4 text-center">
            <p className="text-3xl font-bold text-cortex-400">{value}</p>
            <p className="text-gray-400 text-xs mt-1">{label}</p>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div>
          <h3 className="text-sm font-semibold text-gray-400 mb-3">Goals by Status</h3>
          <ResponsiveContainer width="100%" height={160}>
            <BarChart data={goalChartData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
              <XAxis dataKey="name" tick={{ fill: '#9ca3af', fontSize: 11 }} />
              <YAxis tick={{ fill: '#9ca3af', fontSize: 11 }} allowDecimals={false} />
              <Tooltip contentStyle={{ background: '#111827', border: '1px solid #374151', borderRadius: 8 }} />
              <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                {goalChartData.map((entry) => (
                  <Cell key={entry.name} fill={STATUS_COLORS[entry.name] || '#6366f1'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div>
          <h3 className="text-sm font-semibold text-gray-400 mb-3">Tasks by Status</h3>
          <ResponsiveContainer width="100%" height={160}>
            <BarChart data={taskChartData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
              <XAxis dataKey="name" tick={{ fill: '#9ca3af', fontSize: 11 }} />
              <YAxis tick={{ fill: '#9ca3af', fontSize: 11 }} allowDecimals={false} />
              <Tooltip contentStyle={{ background: '#111827', border: '1px solid #374151', borderRadius: 8 }} />
              <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                {taskChartData.map((entry) => (
                  <Cell key={entry.name} fill={STATUS_COLORS[entry.name] || '#6366f1'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Learning insights */}
      {insights && (
        <div>
          <h3 className="text-sm font-semibold text-gray-400 mb-3">Learning Insights</h3>
          {insights.strategy_suggestions?.length > 0 ? (
            <div className="space-y-2">
              {insights.strategy_suggestions.map((s, i) => (
                <div key={i} className="bg-yellow-900/30 border border-yellow-700/50 rounded p-3 text-sm">
                  <span className="text-yellow-300 font-semibold">{s.tool}</span>
                  <span className="text-gray-300 ml-2">{s.recommendation}</span>
                  <span className="text-gray-500 ml-2 text-xs">({s.reason})</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-sm">No strategy adjustments suggested yet.</p>
          )}

          {Object.keys(insights.tool_performance || {}).length > 0 && (
            <div className="mt-4 overflow-x-auto">
              <table className="w-full text-xs text-gray-400">
                <thead>
                  <tr className="text-gray-500 uppercase">
                    <th className="text-left py-1 px-2">Tool</th>
                    <th className="text-left py-1 px-2">Calls</th>
                    <th className="text-left py-1 px-2">Success Rate</th>
                    <th className="text-left py-1 px-2">Avg Duration</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(insights.tool_performance).map(([tool, stats]) => (
                    <tr key={tool} className="border-t border-gray-800">
                      <td className="py-1 px-2 text-gray-300">{tool}</td>
                      <td className="py-1 px-2">{stats.total_calls}</td>
                      <td className="py-1 px-2">{(stats.success_rate * 100).toFixed(0)}%</td>
                      <td className="py-1 px-2">
                        {stats.avg_duration_seconds != null
                          ? `${stats.avg_duration_seconds.toFixed(3)}s`
                          : '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
