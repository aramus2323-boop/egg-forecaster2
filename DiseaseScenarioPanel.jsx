import { useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function DiseaseScenarioPanel({ onApply, loading, diseaseScenario }) {
  const [severity, setSeverity] = useState('moderate')
  const [recovery, setRecovery] = useState(6)

  const handleApply = (e) => {
    e.preventDefault()
    onApply(severity, recovery)
  }

  const severityInfo = {
    mild: { multiplier: 1.1, color: 'bg-yellow-50', desc: 'Mild outbreak - 10% price impact' },
    moderate: { multiplier: 1.3, color: 'bg-orange-50', desc: 'Moderate outbreak - 30% price impact' },
    severe: { multiplier: 1.5, color: 'bg-red-50', desc: 'Severe outbreak - 50% price impact' }
  }

  const chartData = diseaseScenario?.forecast || []

  return (
    <div className="space-y-6">
      {/* Scenario Controls */}
      <form onSubmit={handleApply} className={`card ${severityInfo[severity].color}`}>
        <h2 className="text-xl font-bold text-secondary mb-4">🦠 Disease Outbreak Scenario</h2>
        <p className="text-sm text-gray-600 mb-4">{severityInfo[severity].desc}</p>

        <div className="grid md:grid-cols-3 gap-6 mb-6">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-3">
              Outbreak Severity
            </label>
            <div className="space-y-2">
              {['mild', 'moderate', 'severe'].map(sev => (
                <label key={sev} className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="radio"
                    value={sev}
                    checked={severity === sev}
                    onChange={(e) => setSeverity(e.target.value)}
                    className="w-4 h-4 cursor-pointer"
                  />
                  <span className="capitalize text-sm">{sev} ({severityInfo[sev].multiplier}x)</span>
                </label>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Recovery Period (Months)
            </label>
            <input
              type="range"
              min="3"
              max="12"
              value={recovery}
              onChange={(e) => setRecovery(parseInt(e.target.value))}
              className="w-full h-2 bg-gray-300 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>3</span>
              <span className="font-semibold text-primary">{recovery} months</span>
              <span>12</span>
            </div>
          </div>

          <div className="flex items-end">
            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? '⏳ Calculating...' : '📊 Apply Scenario'}
            </button>
          </div>
        </div>

        {/* Info Box */}
        <div className="bg-white border-l-4 border-primary p-4 rounded text-sm text-gray-700">
          <p><strong>Impact:</strong> Shows how egg prices would be affected if an outbreak occurred starting immediately.</p>
          <p className="mt-2"><strong>Recovery:</strong> Model assumes prices gradually return to normal over the specified period.</p>
        </div>
      </form>

      {/* Disease Impact Chart */}
      {diseaseScenario && chartData.length > 0 && (
        <div className="card">
          <h2 className="text-xl font-bold text-secondary mb-4">📈 Price Impact Analysis</h2>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey="date"
                tickFormatter={(date) => new Date(date).toLocaleDateString('en-US', { month: 'short' })}
              />
              <YAxis label={{ value: 'Price ($)', angle: -90, position: 'insideLeft' }} />
              <Tooltip
                formatter={(value) => `$${value.toFixed(2)}`}
                contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc', borderRadius: '8px' }}
              />
              <Legend />
              <Bar dataKey="original_price" fill="#8884d8" name="Original Price" />
              <Bar dataKey="disease_adjusted_price" fill="#EF6B00" name="With Disease Impact" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Impact Summary Table */}
      {diseaseScenario && chartData.length > 0 && (
        <div className="card overflow-x-auto">
          <h2 className="text-xl font-bold text-secondary mb-4">📋 Impact Summary</h2>
          
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200 bg-gray-50">
                <th className="px-4 py-2 text-left font-semibold">Month</th>
                <th className="px-4 py-2 text-right font-semibold">Original Price</th>
                <th className="px-4 py-2 text-right font-semibold">With Disease</th>
                <th className="px-4 py-2 text-right font-semibold">Price Impact</th>
                <th className="px-4 py-2 text-right font-semibold">% Change</th>
              </tr>
            </thead>
            <tbody>
              {chartData.map((point, idx) => {
                const pctChange = ((point.disease_adjusted_price - point.original_price) / point.original_price * 100).toFixed(1)
                return (
                  <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="px-4 py-2">{point.date}</td>
                    <td className="px-4 py-2 text-right">${point.original_price.toFixed(2)}</td>
                    <td className="px-4 py-2 text-right font-semibold text-primary">${point.disease_adjusted_price.toFixed(2)}</td>
                    <td className="px-4 py-2 text-right text-red-600">
                      +${point.price_impact.toFixed(2)}
                    </td>
                    <td className="px-4 py-2 text-right text-red-600 font-semibold">
                      +{pctChange}%
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
