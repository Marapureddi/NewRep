import { useEffect, useMemo, useState } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

function App() {
  const [goals, setGoals] = useState([])
  const [loadingGoals, setLoadingGoals] = useState(false)
  const [error, setError] = useState('')
  const [plan, setPlan] = useState(null)

  const [goalForm, setGoalForm] = useState({
    title: '',
    description: '',
    priority: 3,
    weekly_hours_target: 2,
    target_date: '',
  })

  const [availableHours, setAvailableHours] = useState(10)

  const totalPlannedHours = useMemo(() => {
    if (!plan) return 0
    return (plan.plan.sessions.reduce((sum, s) => sum + s.duration_minutes, 0) / 60).toFixed(1)
  }, [plan])

  async function fetchGoals() {
    setLoadingGoals(true)
    setError('')
    try {
      const response = await fetch(`${API_URL}/goals`)
      if (!response.ok) throw new Error('Failed to load goals')
      const data = await response.json()
      setGoals(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoadingGoals(false)
    }
  }

  useEffect(() => {
    fetchGoals()
  }, [])

  async function handleGoalSubmit(e) {
    e.preventDefault()
    setError('')

    try {
      const payload = {
        title: goalForm.title,
        description: goalForm.description,
        priority: Number(goalForm.priority),
        weekly_hours_target: Number(goalForm.weekly_hours_target),
        target_date: goalForm.target_date || null,
      }

      const response = await fetch(`${API_URL}/goals`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        const details = await response.json().catch(() => ({}))
        throw new Error(details?.detail || 'Could not save goal')
      }

      setGoalForm({ title: '', description: '', priority: 3, weekly_hours_target: 2, target_date: '' })
      await fetchGoals()
    } catch (e) {
      setError(e.message)
    }
  }

  async function handleGeneratePlan(e) {
    e.preventDefault()
    setError('')
    try {
      const response = await fetch(`${API_URL}/plans/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ available_hours: Number(availableHours) }),
      })

      const data = await response.json()
      if (!response.ok) throw new Error(data?.detail || 'Plan generation failed')
      setPlan(data)
    } catch (e) {
      setError(e.message)
    }
  }

  return (
    <div className="page">
      <header className="hero">
        <p className="eyebrow">AI Study Planner</p>
        <h1>Turn goals into a weekly execution map.</h1>
        <p>Create goals, set available hours, and generate a balanced study schedule for the week.</p>
      </header>

      {error && <div className="error">{error}</div>}

      <section className="grid">
        <article className="card">
          <h2>Add Goal</h2>
          <form onSubmit={handleGoalSubmit} className="form">
            <label>
              Goal Title
              <input
                required
                value={goalForm.title}
                onChange={(e) => setGoalForm((f) => ({ ...f, title: e.target.value }))}
                placeholder="e.g. Master Linear Algebra"
              />
            </label>
            <label>
              Description
              <textarea
                value={goalForm.description}
                onChange={(e) => setGoalForm((f) => ({ ...f, description: e.target.value }))}
                placeholder="Optional context"
              />
            </label>
            <div className="row">
              <label>
                Priority (1-5)
                <input
                  type="number"
                  min="1"
                  max="5"
                  value={goalForm.priority}
                  onChange={(e) => setGoalForm((f) => ({ ...f, priority: e.target.value }))}
                />
              </label>
              <label>
                Target Hours/Week
                <input
                  type="number"
                  min="0.5"
                  step="0.5"
                  value={goalForm.weekly_hours_target}
                  onChange={(e) => setGoalForm((f) => ({ ...f, weekly_hours_target: e.target.value }))}
                />
              </label>
            </div>
            <label>
              Target Date (optional)
              <input
                type="date"
                value={goalForm.target_date}
                onChange={(e) => setGoalForm((f) => ({ ...f, target_date: e.target.value }))}
              />
            </label>
            <button type="submit">Save Goal</button>
          </form>
        </article>

        <article className="card">
          <h2>Generate Weekly Plan</h2>
          <form onSubmit={handleGeneratePlan} className="form">
            <label>
              Available Hours This Week
              <input
                type="number"
                min="1"
                max="80"
                step="0.5"
                value={availableHours}
                onChange={(e) => setAvailableHours(e.target.value)}
              />
            </label>
            <button type="submit">Generate Plan</button>
          </form>

          <h3>Current Goals</h3>
          {loadingGoals ? (
            <p>Loading goals...</p>
          ) : goals.length === 0 ? (
            <p>No goals yet.</p>
          ) : (
            <ul className="goal-list">
              {goals.map((goal) => (
                <li key={goal.id}>
                  <strong>{goal.title}</strong>
                  <span>P{goal.priority} • {goal.weekly_hours_target}h/week</span>
                </li>
              ))}
            </ul>
          )}
        </article>
      </section>

      {plan && (
        <section className="plan card">
          <div className="plan-header">
            <h2>Weekly Plan</h2>
            <p>{totalPlannedHours} planned hours ({plan.plan.sessions.length} sessions)</p>
          </div>
          <div className="days">
            {plan.days.map((day) => (
              <div key={day.day_of_week} className="day-column">
                <h3>{DAY_NAMES[day.day_of_week]}</h3>
                <p>{(day.total_minutes / 60).toFixed(1)}h</p>
                {day.sessions.length === 0 ? (
                  <small>No sessions</small>
                ) : (
                  day.sessions.map((session) => (
                    <article key={session.id} className="session">
                      <strong>{session.goal_title}</strong>
                      <span>{session.duration_minutes} mins</span>
                      <p>{session.title}</p>
                    </article>
                  ))
                )}
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  )
}

export default App
