import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import MatchupPage from './pages/MatchupPage'
import WeekPage from './pages/WeekPage'

function App() {
  return (
    <BrowserRouter>
      <nav className="nav">
        <Link to="/">Matchup</Link>
        <Link to="/week">This Week</Link>
      </nav>

      <Routes>
        <Route path="/" element={<MatchupPage />} />
        <Route path="/week" element={<WeekPage />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App