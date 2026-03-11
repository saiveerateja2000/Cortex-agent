import { useState } from 'react'
import { createGoal, runGoalPipeline } from '../api/client'
import { Zap } from 'lucide-react'

export default function GoalInput({ onGoalCreated }) {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [priority, setPriority] = useState(5)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [lastResult, setLastResult] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!title.trim()) return
    setLoading(true)
    setError(null)
    setLastResult(null)

    try {
      const { data: goal } = await createGoal({ title, description, priority: Number(priority) })
      const { data: pipeline } = await runGoalPipeline(goal.id)
      setLastResult(pipeline)
      setTitle('')
      setDescription('')
      setPriority(5)
      if (onGoalCreated) onGoalCreated(pipeline)
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <h2 className="text-xl font-bold text-cortex-400 mb-4 flex items-center gap-2">
        <Zap size={20} /> Goal Input
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-400 mb-1">Goal Title *</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g. Invest 1000 units in a simulated stock trading strategy"
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-cortex-500"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-400 mb-1">Description</label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Optional: add more context…"
            rows={3}
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-cortex-500 resize-none"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-400 mb-1">
            Priority: <span className="text-cortex-400 font-bold">{priority}</span>
          </label>
          <input
            type="range"
            min={1}
            max={10}
            value={priority}
            onChange={(e) => setPriority(e.target.value)}
            className="w-full accent-cortex-500"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>Low (1)</span>
            <span>High (10)</span>
          </div>
        </div>

        <button type="submit" disabled={loading || !title.trim()} className="btn-primary w-full">
          {loading ? 'Processing…' : '🚀 Submit Goal & Run Pipeline'}
        </button>
      </form>

      {error && (
        <div className="mt-4 p-3 bg-red-900/50 border border-red-700 rounded-lg text-red-300 text-sm">
          {error}
        </div>
      )}

      {lastResult && (
        <div className="mt-4 p-3 bg-green-900/50 border border-green-700 rounded-lg text-green-300 text-sm">
          <p className="font-semibold">✅ {lastResult.message}</p>
          <p className="text-gray-400 text-xs mt-1">Goal ID: {lastResult.goal?.id}</p>
        </div>
      )}
    </div>
  )
}
