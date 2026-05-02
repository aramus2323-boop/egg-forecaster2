import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function HistoricalChart({ historical }) {
  if (!historical?.data) return null

  const data = historical.data.map(point => ({
    date: new Date(point.date).toLocaleDateString('en-US', { month: 'short', year: '2-digit' }),
    price: point.price,
    cpi: point.cpi,
    production: point.production ? point.production / 1000000 : null // Scale down for visibility
  }))

  const stats = historical.statistics

  return (
    <div className="space-y-6">
      {/* Statistics Cards */}
      <div className="grid md:grid-cols-5 gap-4">
        <div className="card">
          <p className="metric-label">Current Price</p>
          <p className="metric-value">${stats.latest_price.toFixed(2)}</p>
        </div>
        <div className="card">
          <p className="metric-label">Average</p>
          <p className="metric-value">${stats.avg_price.toFixed(2)}</p>
        </div>
        <div className="card">
          <p className="metric-label">Min Price</p>
          <p className="metric-value">${stats.min_price.toFixed(2)}</p>
        </div>
        <div className="card">
          <p className="metric-label">Max Price</p>
          <p className="metric-value">${stats.max_price.toFixed(2)}</p>
        </div>
        <div className="card">
          <p className="metric-label">Volatility</p>
          <p className="metric-value">{(stats.volatility * 100).toFixed(1)}%</p>
        </div>
      </div>

      {/* Price History Chart */}
      <div className="card">
        <h2 className="text-xl font-bold text-secondary mb-4">📈 Price History</h2>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="date" />
            <YAxis 
              yAxisId="left"
              label={{ value: 'Price ($)', angle: -90, position: 'insideLeft' }}
            />
            <YAxis 
              yAxisId="right"
              orientation="right"
              label={{ value: 'CPI', angle: 90, position: 'insideRight' }}
            />
            <Tooltip 
              contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc', borderRadius: '8px' }}
              formatter={(value, name) => {
                if (name === 'Price') return [`$${value.toFixed(2)}`, 'Price']
                return [value.toFixed(2), name]
              }}
            />
            <Legend />
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="price"
              stroke="#EF6B00"
              dot={false}
              name="Egg Price"
              strokeWidth={2}
            />
            {data[0].cpi && (
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="cpi"
                stroke="#8B5CF6"
                dot={false}
                name="CPI"
                strokeWidth={2}
                strokeDasharray="5 5"
              />
            )}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Historical Data Table */}
      <div className="card overflow-x-auto">
        <h2 className="text-xl font-bold text-secondary mb-4">📋 Historical Data</h2>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200 bg-gray-50">
              <th className="px-4 py-2 text-left font-semibold">Date</th>
              <th className="px-4 py-2 text-right font-semibold">Price</th>
              {historical.data[0].cpi !== null && (
                <th className="px-4 py-2 text-right font-semibold">CPI</th>
              )}
              {historical.data[0].production !== null && (
                <th className="px-4 py-2 text-right font-semibold">Production</th>
              )}
            </tr>
          </thead>
          <tbody>
            {historical.data.slice().reverse().map((point, idx) => (
              <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="px-4 py-2">{point.date}</td>
                <td className="px-4 py-2 text-right font-semibold text-primary">${point.price.toFixed(2)}</td>
                {point.cpi !== null && (
                  <td className="px-4 py-2 text-right text-gray-600">{point.cpi.toFixed(2)}</td>
                )}
                {point.production !== null && (
                  <td className="px-4 py-2 text-right text-gray-600">{point.production.toFixed(0)}</td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
