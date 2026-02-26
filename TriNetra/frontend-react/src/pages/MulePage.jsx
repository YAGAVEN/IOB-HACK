import { useState } from 'react'
import Navbar from '../components/Layout/Navbar.jsx'
import NotificationToast, { notify } from '../components/shared/NotificationToast.jsx'
import MuleRiskPanel from '../components/Mule/MuleRiskPanel.jsx'
import MuleNetworkView from '../components/Mule/MuleNetworkView.jsx'

export default function MulePage() {
  const [accountId, setAccountId] = useState('')
  const [loading, setLoading] = useState(false)
  const [riskData, setRiskData] = useState(null)
  const [networkData, setNetworkData] = useState(null)
  const [layeringData, setLayeringData] = useState(null)
  const [sarGenerating, setSarGenerating] = useState(false)
  const [highRiskAccounts, setHighRiskAccounts] = useState([])
  const [highRiskLoading, setHighRiskLoading] = useState(false)

  const analyseAccount = async () => {
    if (!accountId.trim()) {
      notify('Please enter an Account ID', 'warning')
      return
    }
    setLoading(true)
    setRiskData(null)
    setNetworkData(null)
    setLayeringData(null)
    try {
      const api = (await import('../services/api.js')).default
      const [risk, network, layering] = await Promise.all([
        api.getMuleRisk(accountId.trim()),
        api.getNetworkMetrics(accountId.trim()),
        api.getLayeringDetection(accountId.trim()),
      ])
      setRiskData(risk)
      setNetworkData(network)
      setLayeringData(layering)
      notify(`Analysis complete for ${accountId}`, 'success')
    } catch (err) {
      notify(`Analysis failed: ${err.message}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  const generateSAR = async () => {
    if (!riskData) { notify('Run an analysis first', 'warning'); return }
    setSarGenerating(true)
    try {
      const api = (await import('../services/api.js')).default
      await api.generateMuleSAR(accountId.trim(), riskData)
      notify('Mule SAR report generated!', 'success')
    } catch {
      notify('SAR generation failed', 'error')
    } finally {
      setSarGenerating(false)
    }
  }

  const loadHighRisk = async () => {
    setHighRiskLoading(true)
    try {
      const api = (await import('../services/api.js')).default
      const result = await api.getHighRiskAccounts(70)
      setHighRiskAccounts(result?.accounts ?? [])
      notify('High-risk accounts loaded', 'success')
    } catch {
      notify('Failed to load high-risk accounts', 'error')
    } finally {
      setHighRiskLoading(false)
    }
  }

  const selectHighRisk = (id) => {
    setAccountId(id)
    notify(`Account ${id} loaded – click Analyse to continue`, 'info')
  }

  return (
    <div className="text-white">
      <Navbar pageTitle="Mule Detection" pageIcon="🐴" pageTitleColor="text-purple-400" />
      <NotificationToast />

      <main className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="w-24 h-24 mx-auto mb-6 bg-gradient-to-br from-purple-600 to-pink-500 rounded-full flex items-center justify-center text-4xl animate-[glow_2s_ease-in-out_infinite_alternate]">
            🐴
          </div>
          <h1 className="text-4xl md:text-6xl font-bold mb-4 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
            Mule Detection Engine
          </h1>
          <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto">
            AI-powered money mule profiling combining behavioural analysis, network graph intelligence,
            and layering pattern detection.
          </p>
        </div>

        {/* Search bar */}
        <div className="bg-[#1a1a2e]/80 border border-white/10 rounded-2xl p-6 mb-8">
          <h2 className="text-white font-semibold mb-4 text-lg">Account Risk Analysis</h2>
          <div className="flex flex-col sm:flex-row gap-3">
            <input
              type="text"
              value={accountId}
              onChange={(e) => setAccountId(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && analyseAccount()}
              placeholder="Enter Account ID (e.g. ACC_001)"
              className="flex-1 p-4 bg-black/30 border-2 border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-purple-400 transition-all"
            />
            <button
              onClick={analyseAccount}
              disabled={loading}
              className="px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-500 text-white font-semibold rounded-xl hover:opacity-90 hover:scale-105 transition-all duration-300 disabled:opacity-50"
            >
              {loading ? '🔄 Analysing…' : '🔍 Analyse'}
            </button>
            <button
              onClick={generateSAR}
              disabled={sarGenerating || !riskData}
              className="px-6 py-4 bg-orange-600 hover:bg-orange-500 text-white font-semibold rounded-xl transition-all disabled:opacity-40"
            >
              {sarGenerating ? 'Generating…' : '📋 Generate SAR'}
            </button>
          </div>
        </div>

        {/* Main content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left: risk panel */}
          <div className="lg:col-span-1">
            <MuleRiskPanel
              riskData={riskData}
              networkData={networkData}
              layeringData={layeringData}
              loading={loading}
            />
          </div>

          {/* Right: network graph + high risk */}
          <div className="lg:col-span-2 space-y-8">
            <MuleNetworkView
              accountId={accountId.trim() || 'TARGET'}
              networkData={riskData ? networkData : null}
            />

            {/* High-risk accounts panel */}
            <div className="bg-[#1a1a2e]/80 border border-white/10 rounded-2xl p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-white font-semibold text-lg">High-Risk Accounts</h3>
                <button
                  onClick={loadHighRisk}
                  disabled={highRiskLoading}
                  className="px-4 py-2 bg-red-600/80 hover:bg-red-500 text-white text-sm rounded-xl transition-all disabled:opacity-40"
                >
                  {highRiskLoading ? 'Loading…' : '🚨 Load Top Risks'}
                </button>
              </div>

              {highRiskAccounts.length > 0 ? (
                <div className="space-y-2">
                  {highRiskAccounts.map((acc) => (
                    <div
                      key={acc.account_id}
                      onClick={() => selectHighRisk(acc.account_id)}
                      className="flex items-center justify-between p-3 bg-white/5 hover:bg-white/10 rounded-xl cursor-pointer transition-all"
                    >
                      <span className="font-mono text-sm text-white">{acc.account_id}</span>
                      <span
                        className={`text-sm font-bold px-3 py-1 rounded-full ${
                          acc.risk_score >= 90
                            ? 'bg-red-500/20 text-red-400'
                            : acc.risk_score >= 70
                            ? 'bg-orange-500/20 text-orange-400'
                            : 'bg-yellow-500/20 text-yellow-400'
                        }`}
                      >
                        {Math.round(acc.risk_score)}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-sm">
                  Click "Load Top Risks" to see accounts with risk score ≥ 70.
                </p>
              )}
            </div>

            {/* Stats cards */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              {[
                { icon: '🎯', label: 'Detection Method', value: 'ML + Graph' },
                { icon: '🔗', label: 'Analysis Engines', value: '4 Active' },
                { icon: '⚡', label: 'Risk Dimensions', value: 'Behavioural · Network · Layering · Velocity' },
                { icon: '📊', label: 'Compliance', value: 'AML / FinCEN' },
              ].map(({ icon, label, value }) => (
                <div key={label} className="bg-white/5 border border-white/10 rounded-xl p-4">
                  <div className="text-2xl mb-2">{icon}</div>
                  <div className="text-gray-400 text-xs mb-1">{label}</div>
                  <div className="text-white text-sm font-semibold">{value}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
