import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [teams, setTeams] = useState([])
  const [homeTeam, setHomeTeam] = useState('')
  const [awayTeam, setAwayTeam] = useState('')
  const [result, setResult] = useState(null)

  useEffect(() => {
    fetch('http://127.0.0.1:8000/teams')
      .then((response) => response.json())
      .then((data) => setTeams(data.teams))
  }, [])

  const handlePredict = () => {
    fetch(`http://127.0.0.1:8000/predict?home_team=${homeTeam}&away_team=${awayTeam}`)
      .then((response) => response.json())
      .then((data) => setResult(data))
  }

  return (
    <div className="card">
      <h1>NFL <span>Predictor</span></h1>

      <div className="picker">
        <label>Home team</label>
        <select value={homeTeam} onChange={(e) => setHomeTeam(e.target.value)}>
          <option value="">-- pick a team --</option>
          {teams.map((team) => (
            <option key={team} value={team}>{team}</option>
          ))}
        </select>
      </div>

      <div className="picker">
        <label>Away team</label>
        <select value={awayTeam} onChange={(e) => setAwayTeam(e.target.value)}>
          <option value="">-- pick a team --</option>
          {teams.map((team) => (
            <option key={team} value={team}>{team}</option>
          ))}
        </select>
      </div>

      <button onClick={handlePredict}>Predict</button>

      {result && (
        <div className="result">
          <h2>{result.home_team} home win chance</h2>
          <div className="big-number">
            {(result.home_win_probability * 100).toFixed(1)}%
          </div>
        </div>
      )}
    </div>
  )
}

export default App