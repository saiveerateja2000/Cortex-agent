import { useState } from 'react'
import GoalInput from '../components/GoalInput'
import TaskMonitor from '../components/TaskMonitor'
import MemoryLogs from '../components/MemoryLogs'
import Analytics from '../components/Analytics'
import SystemStatus from '../components/SystemStatus'
import { Brain } from 'lucide-react'

const TABS = ['Goals', 'Monitor', 'Memory', 'Analytics', 'Status']

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('Goals')
  const [refreshKey, setRefreshKey] = useState(0)

  const handleGoalCreated = () => {
    setRefreshKey((k) => k + 1)
    setActiveTab('Monitor')
  }

  return (
    <div className="min-h-screen bg-gray-950">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center gap-3">
          <Brain size={28} className="text-cortex-400" />
          <div>
            <h1 className="text-xl font-bold text-white">Cortex Agent</h1>
            <p className="text-xs text-gray-500">Personal Autonomous AI Decision Agent</p>
          </div>
        </div>

        {/* Tabs */}
        <div className="max-w-7xl mx-auto px-4">
          <nav className="flex gap-1">
            {TABS.map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab
                    ? 'border-cortex-500 text-cortex-400'
                    : 'border-transparent text-gray-400 hover:text-white'
                }`}
              >
                {tab}
              </button>
            ))}
          </nav>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        {activeTab === 'Goals' && (
          <div className="max-w-2xl">
            <GoalInput onGoalCreated={handleGoalCreated} />
          </div>
        )}
        {activeTab === 'Monitor' && <TaskMonitor refreshTrigger={refreshKey} />}
        {activeTab === 'Memory' && <MemoryLogs />}
        {activeTab === 'Analytics' && <Analytics />}
        {activeTab === 'Status' && (
          <div className="max-w-md">
            <SystemStatus />
          </div>
        )}
      </main>
    </div>
  )
}
