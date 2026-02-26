import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import Navbar from '../components/Layout/Navbar.jsx'
import ProgressFlow from '../components/shared/ProgressFlow.jsx'
import NotificationToast, { notify } from '../components/shared/NotificationToast.jsx'
import TimelineView from '../components/Chronos/TimelineView.jsx'
import PlaybackControls from '../components/Chronos/PlaybackControls.jsx'
import AIInsightsPanel from '../components/Chronos/AIInsightsPanel.jsx'

export default function ChronosPage() {
  const navigate = useNavigate()
  const timelineRef = useRef(null)

  const [speed, setSpeed] = useState(1)
  const [viewMode, setViewMode] = useState('timeline')
  const [insights, setInsights] = useState([])
  const [insightsLoading, setInsightsLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')

  /* ── Handlers ── */
  const handleTimeQuantumChange = async (e) => {
    await timelineRef.current?.setTimeQuantum(e.target.value)
  }

  const handleSpeedChange = (val) => {
    setSpeed(val)
    timelineRef.current?.setPlaybackSpeed(val)
  }

  const handleSearch = async () => {
    if (!searchTerm.trim()) return
    try {
      const results = await timelineRef.current?.searchTransactions(searchTerm, 'all')
      if (results) notify(`Found ${results.length} results`, 'success')
    } catch {
      notify('Search failed', 'error')
    }
  }

  const handleViewSwitch = (mode) => {
    setViewMode(mode)
    timelineRef.current?.switchView(mode)
  }

  const handleGenerateInsights = async () => {
    setInsightsLoading(true)
    try {
      const { default: geminiAPI } = await import('../services/gemini-api.js')
      const api = (await import('../services/api.js')).default
      const data = await api.getTimelineData('all', '1m')
      const transactions = data?.data ?? []

      // Build analysis data from transactions
      const suspiciousCount = transactions.filter(t => (t.suspicious_score || 0) > 0.5).length
      const totalAmount = transactions.reduce((s, t) => s + (t.amount || 0), 0)
      const patterns = [...new Set(transactions.map(t => t.pattern_type).filter(Boolean))]
      const analysisData = {
        totalTransactions: transactions.length,
        suspiciousCount,
        totalAmount,
        patterns
      }

      const result = await geminiAPI.enhanceFinancialAnalysis(analysisData)

      // Format the result as HTML insight cards
      const insightHtml = `
        <div class="space-y-4 text-gray-300">
          <p>📊 <strong class="text-[#00ff87]">${transactions.length}</strong> transactions analysed</p>
          <p>🚨 <strong class="text-red-400">${suspiciousCount}</strong> suspicious patterns detected</p>
          <p>💰 Total exposure: <strong class="text-[#00d4ff]">₹${totalAmount.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</strong></p>
          <p>⚠️ Risk Level: <strong class="text-yellow-400">${result?.riskAssessment || 'MEDIUM'}</strong> (${result?.confidence || 80}% confidence)</p>
          <p>🔍 Techniques: ${(result?.techniques || patterns).join(', ')}</p>
          ${result?.enhancedInsights ? `<p class="mt-2 text-sm">${result.enhancedInsights}</p>` : ''}
          ${result?.recommendations ? `<div class="mt-3"><strong class="text-[#00ff87]">Recommendations:</strong><ul class="list-disc list-inside mt-1 text-sm">${result.recommendations.map(r => `<li>${r}</li>`).join('')}</ul></div>` : ''}
        </div>
      `
      setInsights([insightHtml])
    } catch {
      setInsights(['<p class="text-gray-300">AI analysis unavailable in demo mode.</p>'])
    } finally {
      setInsightsLoading(false)
    }
  }

  const handleExport = () => {
    timelineRef.current?.exportReport()
  }

  return (
    <div className="text-white">
      <Navbar pageTitle="CHRONOS" pageIcon="🕐" pageTitleColor="text-[#00ff87]" />
      <NotificationToast />

      <main className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="w-24 h-24 mx-auto mb-6 bg-gradient-to-br from-[#00ff87] to-[#00d4ff] rounded-full flex items-center justify-center text-4xl animate-[glow_2s_ease-in-out_infinite_alternate]">
            🕐
          </div>
          <h1 className="text-4xl md:text-6xl font-bold mb-4 bg-gradient-to-r from-[#00ff87] to-[#00d4ff] bg-clip-text text-transparent">
            CHRONOS Timeline
          </h1>
          <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto">
            Visualize financial crime patterns through time. Analyze transaction flows, detect suspicious activities,
            and uncover hidden connections in real-time.
          </p>
          <ProgressFlow activeStep="chronos" />
        </div>

        {/* Controls */}
        <div className="bg-[#1a1a2e]/60 backdrop-blur-sm rounded-2xl p-8 mb-8 border border-[#00ff87]/20">
          <h3 className="text-2xl font-semibold mb-6 text-[#00ff87]">Timeline Controls</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">

            {/* Time Quantum */}
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-300">Time Period</label>
              <select
                onChange={handleTimeQuantumChange}
                className="w-full bg-[#0a0a0f]/80 border border-gray-600 rounded-lg px-3 py-2 text-white focus:border-[#00ff87] focus:ring-1 focus:ring-[#00ff87]"
              >
                <option value="1m">1 Month</option>
                <option value="6m">6 Months</option>
                <option value="1y">1 Year</option>
                <option value="3y">3 Years</option>
              </select>
            </div>

            {/* Search */}
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-300">Search Transactions</label>
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                  placeholder="Enter search term..."
                  className="flex-1 bg-[#0a0a0f]/80 border border-gray-600 rounded-lg px-3 py-2 text-white focus:border-[#00ff87] focus:ring-1 focus:ring-[#00ff87]"
                />
                <button
                  onClick={handleSearch}
                  className="px-4 py-2 bg-[#00ff87] hover:bg-[#00ff87]/80 text-[#0a0a0f] font-semibold rounded-lg transition-colors"
                >
                  🔍
                </button>
              </div>
            </div>

            {/* Playback */}
            <PlaybackControls
              speed={speed}
              onSpeedChange={handleSpeedChange}
              onPlay={() => timelineRef.current?.play()}
              onPause={() => timelineRef.current?.pause()}
              onReset={() => timelineRef.current?.reset()}
            />

            {/* View Mode */}
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-300">View Mode</label>
              <div className="flex space-x-2">
                <button
                  onClick={() => handleViewSwitch('timeline')}
                  className={`flex-1 px-3 py-2 rounded-lg transition-colors ${viewMode === 'timeline' ? 'bg-[#00ff87] text-[#0a0a0f] font-semibold' : 'bg-[#0a0a0f]/80 text-gray-300 border border-gray-600 hover:border-[#00ff87]/50'}`}
                >
                  📈 Timeline
                </button>
                <button
                  onClick={() => handleViewSwitch('network')}
                  className={`flex-1 px-3 py-2 rounded-lg transition-colors ${viewMode === 'network' ? 'bg-[#00ff87] text-[#0a0a0f] font-semibold' : 'bg-[#0a0a0f]/80 text-gray-300 border border-gray-600 hover:border-[#00ff87]/50'}`}
                >
                  🕸️ Network
                </button>
              </div>
            </div>

            {/* Export */}
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-300">Export</label>
              <button
                onClick={handleExport}
                className="w-full px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
              >
                📄 Export PDF
              </button>
            </div>
          </div>
        </div>

        {/* Timeline Visualization */}
        <div className="bg-[#1a1a2e]/60 backdrop-blur-sm rounded-2xl p-8 mb-8 border border-[#00ff87]/20">
          <TimelineView ref={timelineRef} containerId="chronos-timeline" />
          <div id="timeline-info" className="mt-6 p-6 bg-[#0a0a0f]/40 rounded-lg" />
        </div>

        {/* AI Insights */}
        <AIInsightsPanel
          insights={insights}
          loading={insightsLoading}
          onGenerate={handleGenerateInsights}
        />

        {/* Navigation */}
        <div className="flex justify-between items-center">
          <button
            onClick={() => navigate('/login')}
            className="px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
          >
            ← Back to Login
          </button>
          <button
            onClick={() => navigate('/autosar')}
            className="px-8 py-3 bg-gradient-to-r from-[#00ff87] to-[#00d4ff] text-[#0a0a0f] font-bold rounded-lg hover:shadow-lg transform hover:scale-105 transition-all"
          >
            Proceed to Auto-SAR →
          </button>
        </div>
      </main>
    </div>
  )
}

function generateFallbackInsight(transactions) {
  const total = transactions.length
  const high = transactions.filter((t) => t.suspicious_score > 0.8).length
  return `
    <div class="space-y-2 text-gray-300">
      <p>📊 <strong class="text-[#00ff87]">${total}</strong> transactions analysed</p>
      <p>🚨 <strong class="text-red-400">${high}</strong> high-risk patterns detected</p>
      <p>⚠️ Structuring and layering behaviour observed across multiple accounts</p>
    </div>
  `
}
