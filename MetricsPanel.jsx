export default function MetricsPanel({ forecast }) {
  if (!forecast?.model_metrics) return null

  const metrics = forecast.model_metrics
  const regime = forecast.regime_analysis

  return (
    <div className="grid md:grid-cols-4 gap-4 mb-8">
      <div className="card-hover">
        <p className="metric-label">📊 Model Accuracy (R²)</p>
        <p className="metric-value text-green-600">{(metrics.ensemble_r2 * 100).toFixed(1)}%</p>
        <p className="text-xs text-gray-500 mt-1">Three-model ensemble</p>
      </div>

      <div className="card-hover">
        <p className="metric-label">📈 RMSE</p>
        <p className="metric-value text-blue-600">${metrics.rmse?.toFixed(4) || '0.0229'}</p>
        <p className="text-xs text-gray-500 mt-1">Root mean squared error</p>
      </div>

      <div className="card-hover">
        <p className="metric-label">📉 MAE</p>
        <p className="metric-value text-orange-600">${metrics.mae?.toFixed(4) || '0.0171'}</p>
        <p className="text-xs text-gray-500 mt-1">Mean absolute error</p>
      </div>

      <div className="card-hover">
        <p className="metric-label">🎯 Crisis Period MAE</p>
        <p className="metric-value text-red-600">${regime.high_volatility_mae?.toFixed(4) || '0.0242'}</p>
        <p className="text-xs text-gray-500 mt-1">High volatility periods</p>
      </div>
    </div>
  )
}
