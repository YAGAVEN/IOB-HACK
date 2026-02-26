import { useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext.jsx'

const NAV_ITEMS = [
  { path: '/chronos', label: 'CHRONOS', icon: '🕐', color: 'text-[#00ff87] border-[#00ff87]' },
  { path: '/autosar', label: 'Auto-SAR', icon: '📋', color: 'text-orange-400 border-orange-400' },
  { path: '/hydra', label: 'HYDRA', icon: '🐍', color: 'text-red-400 border-red-400' },
  { path: '/mule', label: 'Mule', icon: '🐴', color: 'text-purple-400 border-purple-400' },
]

export default function Navbar({ pageTitle, pageTitleColor = 'text-[#00ff87]', pageIcon }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <nav className="bg-[#1a1a2e]/80 backdrop-blur-sm border-b border-[#00ff87]/20 sticky top-0 z-50">
      <div className="max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-4">
            <h1
              className="text-2xl font-bold bg-gradient-to-r from-[#00ff87] to-[#00d4ff] bg-clip-text text-transparent cursor-pointer"
              onClick={() => navigate('/chronos')}
            >
              TriNetra
            </h1>
            <span className="text-gray-400 hidden sm:block">|</span>
            <h2 className={`text-xl font-semibold hidden sm:block ${pageTitleColor}`}>
              {pageIcon} {pageTitle}
            </h2>
          </div>

          {/* Navigation links */}
          <div className="hidden md:flex items-center space-x-1">
            {NAV_ITEMS.map(({ path, label, icon, color }) => {
              const isActive = location.pathname === path
              return (
                <button
                  key={path}
                  onClick={() => navigate(path)}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-200 border
                    ${isActive
                      ? `${color} bg-white/10`
                      : 'text-gray-400 border-transparent hover:text-white hover:bg-white/5'
                    }`}
                >
                  {icon} {label}
                </button>
              )
            })}
          </div>

          <div className="flex items-center space-x-3">
            {user && (
              <span className="text-gray-300 text-sm hidden sm:block">Welcome, {user}</span>
            )}
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors text-sm"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  )
}
