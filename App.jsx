import { useState, useEffect } from 'react'
import axios from 'axios'
import ForecastChart from './ForecastChart'
import HistoricalChart from './HistoricalChart'
import MetricsPanel from './MetricsPanel'
import ForecastControls from './ForecastControls'
import DiseaseScenarioPanel from './DiseaseScenarioPanel'

const API_URL = ''  // Use Vite proxy (relative paths)

export default function App() {
  const [forecast, setForecast] = useState(null)
  const [historical, setHistorical] = useState(null)
  const [modelInfo, setModelInfo] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('forecast')
  const [diseaseScenario, setDiseaseScenario] = useState(null)

  // Fetch model info on mount
  useEffect(() => {
    const fetchModelInfo = async () => {
      try {
        const res = await axios.get(`${API_URL}/api/model-info`)
        setModelInfo(res.data)
      } catch (err) {
        console.error('Error fetching model info:', err)
      }
    }
    fetchModelInfo()
    generateForecast({ months_ahead: 6, include_disease_risk: true })
    loadHistorical({ months_back: 24 })
  }, [])

  const generateForecast = async (params) => {
    setLoading(true)
    setError(null)
    try {
      const res = await axios.post(`${API_URL}/api/forecast`, params)
      setForecast(res.data)
      setDiseaseScenario(null)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate forecast')
      console.error('Forecast error:', err)
    } finally {
      setLoading(false)
    }
  }

  const loadHistorical = async (params) => {
    try {
      const res = await axios.post(`${API_URL}/api/historical`, params)
      setHistorical(res.data)
    } catch (err) {
      console.error('Historical data error:', err)
    }
  }

  const handleDiseaseScenario = async (severity, recoveryMonths) => {
    setLoading(true)
    try {
      const res = await axios.post(`${API_URL}/api/disease-scenario`, {
        outbreak_severity: severity,
        recovery_months: recoveryMonths
      })
      setDiseaseScenario(res.data)
      setActiveTab('disease')
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate disease scenario')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-white to-yellow-50">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="text-4xl">🐔</div>
              <div>
                <h1 className="text-3xl font-bold text-secondary">Egg Price Forecaster</h1>
                <p className="text-sm text-gray-600">AI-Powered Market Prediction</p>
              </div>
            </div>
            <div className="text-right text-sm text-gray-600">
              {modelInfo && <p>v{modelInfo.version}</p>}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error Alert */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            <p className="font-semibold">Error</p>
            <p className="text-sm">{error}</p>
          </div>
        )}

        {/* Metrics Panel */}
        {forecast && <MetricsPanel forecast={forecast} />}

        {/* Tabs */}
        <div className="mb-6 flex gap-2 border-b border-gray-200">
          <button
            onClick={() => setActiveTab('forecast')}
            className={`px-4 py-2 font-semibold border-b-2 transition-colors ${
              activeTab === 'forecast'
                ? 'border-primary text-primary'
                : 'border-transparent text-gray-600 hover:text-gray-800'
            }`}
          >
            📊 Forecast
          </button>
          <button
            onClick={() => setActiveTab('historical')}
            className={`px-4 py-2 font-semibold border-b-2 transition-colors ${
              activeTab === 'historical'
                ? 'border-primary text-primary'
                : 'border-transparent text-gray-600 hover:text-gray-800'
            }`}
          >
            📈 Historical
          </button>
          <button
            onClick={() => setActiveTab('disease')}
            className={`px-4 py-2 font-semibold border-b-2 transition-colors ${
              activeTab === 'disease'
                ? 'border-primary text-primary'
                : 'border-transparent text-gray-600 hover:text-gray-800'
            }`}
          >
            🦠 Disease Scenario
          </button>
          <button
            onClick={() => setActiveTab('about')}
            className={`px-4 py-2 font-semibold border-b-2 transition-colors ${
              activeTab === 'about'
                ? 'border-primary text-primary'
                : 'border-transparent text-gray-600 hover:text-gray-800'
            }`}
          >
            ℹ️ About Model
          </button>
        </div>

        {/* Tab Content */}
        {activeTab === 'forecast' && (
          <div className="space-y-6">
            <ForecastControls
              onForecast={generateForecast}
              loading={loading}
            />
            {forecast && <ForecastChart forecast={forecast} />}
          </div>
        )}

        {activeTab === 'historical' && (
          <div className="space-y-6">
            <div className="card">
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                Historical Data Range
              </label>
              <select
                onChange={(e) => loadHistorical({ months_back: parseInt(e.target.value) })}
                defaultValue="24"
                className="w-full sm:w-48 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="12">Last 12 months</option>
                <option value="24">Last 24 months (2 years)</option>
                <option value="60">Last 5 years</option>
                <option value="120">Last 10 years</option>
              </select>
            </div>
            {historical && <HistoricalChart historical={historical} />}
          </div>
        )}

        {activeTab === 'disease' && (
          <DiseaseScenarioPanel
            onApply={handleDiseaseScenario}
            loading={loading}
            diseaseScenario={diseaseScenario}
          />
        )}

        {activeTab === 'about' && modelInfo && (
          <div className="card space-y-4">
            <h2 className="text-2xl font-bold text-secondary">About This Model</h2>
            
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h3 className="font-semibold text-lg mb-2">Model Type</h3>
                <p className="text-gray-700">{modelInfo.model_type}</p>
              </div>
              <div>
                <h3 className="font-semibold text-lg mb-2">Performance</h3>
                <p className="text-gray-700">R² Score: {modelInfo.ensemble_r2}</p>
              </div>
            </div>

            <div>
              <h3 className="font-semibold text-lg mb-2">Key Features ({modelInfo.features} total)</h3>
              <ul className="grid md:grid-cols-2 gap-2">
                {modelInfo.improvements.map((imp, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-gray-700">
                    <span className="text-primary font-bold">✓</span>
                    <span>{imp}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-sm text-gray-700">
                <strong>Note:</strong> This model is trained on {modelInfo.training_years} years of historical egg price data with CPI integration, production data, and disease outbreak analysis.
              </p>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-16 bg-gray-900 text-white py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-3 gap-8 mb-8">
            <div>
              <h3 className="font-bold mb-2">About</h3>
              <p className="text-sm text-gray-400">
                Professional egg price forecasting with advanced machine learning
              </p>
            </div>
            <div>
              <h3 className="font-bold mb-2">Data</h3>
              <p className="text-sm text-gray-400">
                18 years of historical prices + CPI + production data
              </p>
            </div>
            <div>
              <h3 className="font-bold mb-2">Accuracy</h3>
              <p className="text-sm text-gray-400">
                96% accuracy with regime-specific validation
              </p>
            </div>
          </div>
          <div className="border-t border-gray-800 pt-4 text-center text-sm text-gray-400">
            <p>© 2026 Egg Price Forecaster • Powered by Advanced Machine Learning</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
