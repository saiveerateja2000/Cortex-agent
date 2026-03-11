import { useState, useEffect, useCallback } from 'react'
import { listGoals, getGoalTasks, runGoalPipeline, deleteGoal } from '../api/client'
import { RefreshCw, Play, Trash2, ChevronDown, ChevronRight } from 'lucide-react'

function StatusBadge({ status }) {
  return <span className={`badge badge-${status}`}>{status}</span>
}

function TaskRow({ task }) {
  return (
    <tr className="border-t border-gray-800">
      <td className="py-2 px-3 text-gray-300 text-sm">{task.order}. {task.name}</td>
      <td className="py-2 px-3"><StatusBadge status={task.status} /></td>
      <td className="py-2 px-3 text-gray-500 text-xs">{task.action_type}</td>
      <td className="py-2 px-3 text-gray-400 text-xs truncate max-w-xs">
        {task.error_message || (task.result ? '✓ result stored' : '—')}
      </td>
    </tr>
  )
}

function GoalRow({ goal, onRefresh }) {
  const [expanded, setExpanded] = useState(false)
  const [tasks, setTasks] = useState([])
  const [loadingTasks, setLoadingTasks] = useState(false)
  const [running, setRunning] = useState(false)

  const loadTasks = useCallback(async () => {
    setLoadingTasks(true)
    try {
      const { data } = await getGoalTasks(goal.id)
      setTasks(data)
    } catch {
      // ignore
    } finally {
      setLoadingTasks(false)
    }
  }, [goal.id])

  const toggle = () => {
    setExpanded((v) => !v)
    if (!expanded) loadTasks()
  }

  const handleRun = async (e) => {
    e.stopPropagation()
    setRunning(true)
    try {
      await runGoalPipeline(goal.id)
      onRefresh()
    } catch {
      // ignore
    } finally {
      setRunning(false)
    }
  }

  const handleDelete = async (e) => {
    e.stopPropagation()
    if (!window.confirm('Delete this goal?')) return
    try {
      await deleteGoal(goal.id)
      onRefresh()
    } catch {
      // ignore
    }
  }

  return (
    <>
      <tr
        className="border-t border-gray-800 hover:bg-gray-800/50 cursor-pointer"
        onClick={toggle}
      >
        <td className="py-3 px-3">
          {expanded ? <ChevronDown size={14} className="text-gray-400" /> : <ChevronRight size={14} className="text-gray-400" />}
        </td>
        <td className="py-3 px-3 text-white font-medium text-sm">{goal.title}</td>
        <td className="py-3 px-3"><StatusBadge status={goal.status} /></td>
        <td className="py-3 px-3 text-gray-400 text-sm">{goal.priority}</td>
        <td className="py-3 px-3 text-gray-500 text-xs">
          {new Date(goal.created_at).toLocaleString()}
        </td>
        <td className="py-3 px-3 flex gap-2">
          {['pending', 'failed'].includes(goal.status) && (
            <button
              onClick={handleRun}
              disabled={running}
              className="text-cortex-400 hover:text-cortex-300 p-1 rounded transition-colors"
              title="Run pipeline"
            >
              <Play size={14} />
            </button>
          )}
          <button
            onClick={handleDelete}
            className="text-red-500 hover:text-red-400 p-1 rounded transition-colors"
            title="Delete goal"
          >
            <Trash2 size={14} />
          </button>
        </td>
      </tr>
      {expanded && (
        <tr>
          <td colSpan={6} className="bg-gray-950 px-6 py-3">
            {loadingTasks ? (
              <p className="text-gray-500 text-sm">Loading tasks…</p>
            ) : tasks.length === 0 ? (
              <p className="text-gray-500 text-sm">No tasks yet.</p>
            ) : (
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-gray-500 text-xs uppercase">
                    <th className="text-left py-1 px-3">Task</th>
                    <th className="text-left py-1 px-3">Status</th>
                    <th className="text-left py-1 px-3">Action Type</th>
                    <th className="text-left py-1 px-3">Notes</th>
                  </tr>
                </thead>
                <tbody>
                  {tasks.map((t) => <TaskRow key={t.id} task={t} />)}
                </tbody>
              </table>
            )}
          </td>
        </tr>
      )}
    </>
  )
}

export default function TaskMonitor({ refreshTrigger }) {
  const [goals, setGoals] = useState([])
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const { data } = await listGoals({ limit: 30 })
      setGoals(data)
    } catch {
      // ignore
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load, refreshTrigger])

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-cortex-400">Task Execution Monitor</h2>
        <button onClick={load} className="btn-secondary flex items-center gap-1 text-sm py-1 px-3">
          <RefreshCw size={14} /> Refresh
        </button>
      </div>

      {loading ? (
        <p className="text-gray-500 text-sm">Loading goals…</p>
      ) : goals.length === 0 ? (
        <p className="text-gray-500 text-sm">No goals yet. Submit one above!</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-gray-500 text-xs uppercase">
                <th className="py-2 px-3 w-6"></th>
                <th className="text-left py-2 px-3">Goal</th>
                <th className="text-left py-2 px-3">Status</th>
                <th className="text-left py-2 px-3">Priority</th>
                <th className="text-left py-2 px-3">Created</th>
                <th className="text-left py-2 px-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {goals.map((g) => (
                <GoalRow key={g.id} goal={g} onRefresh={load} />
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
