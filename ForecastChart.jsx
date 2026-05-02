import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function ForecastChart({ forecast }) {
  if (!forecast?.forecast) return null

  const data = forecast.forecast.map(point => ({
    date: new Date(point.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    price: point.price,
    lower: point.lower_bound,
    upper: point.upper_bound,
    disease: point.disease_risk_score * 100
  }))

  return (
    <div className="space-y-6">
      {/* Price Forecast Chart */}
      <div className="card">
        <h2 className="text-xl font-bold text-secondary mb-4">📊 Price Forecast</h2>
        <ResponsiveContainer width="100%" height={400}>
          <AreaChart data={data}>
            <defs>
              <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#EF6B00" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#EF6B00" stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="colorRange" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#FCD34D" stopOpacity={0.2}/>
                <stop offset="95%" stopColor="#FCD34D" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="date" />
            <YAxis label={{ value: 'Price ($)', angle: -90, position: 'insideLeft' }} />
            <Tooltip 
              contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc', borderRadius: '8px' }}
              formatter={(value) => `$${value.toFixed(2)}`}
            />
            <Legend />
            <Area
              type="monotone"
              dataKey="upper"
              fill="#FCD34D"
              stroke="#F59E0B"
              name="Confidence Range (Upper)"
              fillOpacity={0.3}
            />
            <Area
              type="monotone"
              dataKey="price"
              fill="#EF6B00"
              stroke="#DC5C08"
              name="Forecast Price"
              fillOpacity={1}
            />
            <Area
              type="monotone"
              dataKey="lower"
              fill="#FCD34D"
              stroke="#F59E0B"
              name="Confidence Range (Lower)"
              fillOpacity={0.3}
            />
          </AreaChart>
        </ResponsiveContainer>
        <p className="text-xs text-gray-500 mt-2">Shaded areas represent confidence intervals based on market volatility</p>
      </div>

      {/* Disease Risk Chart */}
      <div className="card">
        <h2 className="text-xl font-bold text-secondary mb-4">🦠 Disease Risk Over Forecast Period</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="date" />
            <YAxis label={{ value: 'Risk (%)', angle: -90, position: 'insideLeft' }} />
            <Tooltip 
              formatter={(value) => `${value.toFixed(1)}%`}
              contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc', borderRadius: '8px' }}
            />
            <Line 
              type="monotone"
              dataKey="disease"
              stroke="#EF4444"
              dot={{ fill: '#EF4444', r: 4 }}
              activeDot={{ r: 6 }}
              name="Disease Risk (%)"
              strokeWidth={2}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Forecast Table */}
      <div className="card overflow-x-auto">
        <h2 className="text-xl font-bold text-secondary mb-4">📋 Detailed Forecast Data</h2>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200 bg-gray-50">
              <th className="px-4 py-2 text-left font-semibold">Date</th>
              <th className="px-4 py-2 text-right font-semibold">Price</th>
              <th className="px-4 py-2 text-right font-semibold">Lower Bound</th>
              <th className="px-4 py-2 text-right font-semibold">Upper Bound</th>
              <th className="px-4 py-2 text-right font-semibold">Disease Risk</th>
            </tr>
          </thead>
          <tbody>
            {forecast.forecast.map((point, idx) => (
              <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="px-4 py-2">{point.date}</td>
                <td className="px-4 py-2 text-right font-semibold text-primary">${point.price.toFixed(2)}</td>
                <td className="px-4 py-2 text-right text-gray-600">${point.lower_bound.toFixed(2)}</td>
                <td className="px-4 py-2 text-right text-gray-600">${point.upper_bound.toFixed(2)}</td>
                <td className="px-4 py-2 text-right">{(point.disease_risk_score * 100).toFixed(1)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
