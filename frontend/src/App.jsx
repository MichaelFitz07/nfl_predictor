import { useState, useEffect } from 'react'


function App() {
  const [teams, setTeams] = useState([])
  const [homeTeam, setHomeTeam] = useState('')
  const [awayTeam, setAwayTeam] = useState('')
  const [result, setResult] = useState(null)

  // grab the team list once when the page loads
  useEffect(() => {
    fetch('http://127.0.0.1:8000/teams')
      .then((response) => response.json())
      .then((data) => setTeams(data.teams))
  }, [])

  // called when the predict button is clicked - hits our api and stores the answer
  const handlePredict = () => {
    fetch(`http://127.0.0.1:8000/predict?home_team=${homeTeam}&away_team=${awayTeam}`)
      .then((response) => response.json())
      .then((data) => setResult(data))
  }

  return (
    <div>
      <h1>NFL Game Predictor</h1>

      <div>
        <label>Home team: </label>
        <select value={homeTeam} onChange={(e) => setHomeTeam(e.target.value)}>
          <option value="">-- pick a team --</option>
          {teams.map((team) => (
            <option key={team} value={team}>{team}</option>
          ))}
        </select>
      </div>

      <div>
        <label>Away team: </label>
        <select value={awayTeam} onChange={(e) => setAwayTeam(e.target.value)}>
          <option value="">-- pick a team --</option>
          {teams.map((team) => (
            <option key={team} value={team}>{team}</option>
          ))}
        </select>
      </div>

      <button onClick={handlePredict}>Predict</button>

      {/* only show the result once we actually have one */}
      {result && (
        <div>
          <h2>Prediction</h2>
          <p>
            {result.home_team} (home) win chance: {(result.home_win_probability * 100).toFixed(1)}%
          </p>
        </div>
      )}
    </div>
  )
}

export default App