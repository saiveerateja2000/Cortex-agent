import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

// Goals
export const createGoal = (data) => api.post('/goals/', data)
export const runGoalPipeline = (id) => api.post(`/goals/${id}/run`)
export const listGoals = (params) => api.get('/goals/', { params })
export const getGoal = (id) => api.get(`/goals/${id}`)
export const deleteGoal = (id) => api.delete(`/goals/${id}`)

// Tasks
export const listTasks = (params) => api.get('/tasks/', { params })
export const getGoalTasks = (goalId) => api.get(`/tasks/goal/${goalId}`)
export const getTaskActions = (taskId) => api.get(`/tasks/${taskId}/actions`)

// Memory
export const listMemory = (params) => api.get('/memory/', { params })
export const createMemoryEntry = (data) => api.post('/memory/', data)
export const deleteMemoryEntry = (id) => api.delete(`/memory/${id}`)

// Analytics
export const getAnalyticsSummary = () => api.get('/analytics/summary')
export const getMetrics = (params) => api.get('/analytics/metrics', { params })
export const getLearningInsights = () => api.get('/analytics/learning')

// System
export const getHealth = () => api.get('/health', { baseURL: '' })

export default api
