import { useState } from 'react'

export default function ForecastControls({ onForecast, loading }) {
  const [months, setMonths] = useState(6)
  const [includeDisease, setIncludeDisease] = useState(true)

  const handleSubmit = (e) => {
    e.preventDefault()
    onForecast({
      months_ahead: months,
      include_disease_risk: includeDisease
    })
  }

  return (
    <form onSubmit={handleSubmit} className="card">
      <h2 className="text-xl font-bold text-secondary mb-4">🔧 Forecast Parameters</h2>
      
      <div className="grid md:grid-cols-3 gap-6">
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Forecast Period (Months)
          </label>
          <input
            type="range"
            min="1"
            max="24"
            value={months}
            onChange={(e) => setMonths(parseInt(e.target.value))}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>1</span>
            <span className="font-semibold text-lg text-primary">{months} months</span>
            <span>24</span>
          </div>
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Confidence Level
          </label>
          <select
            defaultValue="medium"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="low">Low (Wider Intervals)</option>
            <option value="medium">Medium (Standard)</option>
            <option value="high">High (Narrow Intervals)</option>
          </select>
        </div>

        <div className="flex items-end">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={includeDisease}
              onChange={(e) => setIncludeDisease(e.target.checked)}
              className="w-4 h-4 cursor-pointer"
            />
            <span className="text-sm font-semibold text-gray-700">Include Disease Risk</span>
          </label>
        </div>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="btn-primary mt-6 w-full md:w-auto disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? '⏳ Generating...' : '🚀 Generate Forecast'}
      </button>
    </form>
  )
}
