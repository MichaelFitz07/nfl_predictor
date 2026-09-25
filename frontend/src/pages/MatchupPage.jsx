import { useState, useEffect } from 'react'
import '../App.css'

const TEAM_NAMES = {
  ARI: 'Arizona Cardinals', ATL: 'Atlanta Falcons', BAL: 'Baltimore Ravens',
  BUF: 'Buffalo Bills', CAR: 'Carolina Panthers', CHI: 'Chicago Bears',
  CIN: 'Cincinnati Bengals', CLE: 'Cleveland Browns', DAL: 'Dallas Cowboys',
  DEN: 'Denver Broncos', DET: 'Detroit Lions', GB: 'Green Bay Packers',
  HOU: 'Houston Texans', IND: 'Indianapolis Colts', JAX: 'Jacksonville Jaguars',
  KC: 'Kansas City Chiefs', LA: 'Los Angeles Rams', LAC: 'Los Angeles Chargers',
  LV: 'Las Vegas Raiders', MIA: 'Miami Dolphins', MIN: 'Minnesota Vikings',
  NE: 'New England Patriots', NO: 'New Orleans Saints', NYG: 'New York Giants',
  NYJ: 'New York Jets', PHI: 'Philadelphia Eagles', PIT: 'Pittsburgh Steelers',
  SEA: 'Seattle Seahawks', SF: 'San Francisco 49ers', TB: 'Tampa Bay Buccaneers',
  TEN: 'Tennessee Titans', WAS: 'Washington Commanders',
}


const logoUrl = (team) => {
  const map = { LA: 'lar', LAC: 'lac', LV: 'lv', WAS: 'wsh', JAX: 'jax' }
  const code = (map[team] || team).toLowerCase()
  return `https://a.espncdn.com/i/teamlogos/nfl/500/${code}.png`
}

function MatchupPage() {
  const [teams, setTeams] = useState([])
  const [homeTeam, setHomeTeam] = useState('')
  const [awayTeam, setAwayTeam] = useState('')
  const [result, setResult] = useState(null)

  const confidenceLabel = (prob) => {
    const edge = Math.abs(prob - 0.5)
    if (edge < 0.05) return 'Toss-up'
    if (edge < 0.15) return 'Slight edge'
    if (edge < 0.25) return 'Solid pick'
    return 'Strong pick'
  }

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
            <option key={team} value={team} disabled={team === awayTeam}>
              {TEAM_NAMES[team]}
            </option>
          ))}
        </select>
      </div>

      <div className="picker">
        <label>Away team</label>
        <select value={awayTeam} onChange={(e) => setAwayTeam(e.target.value)}>
          <option value="">-- pick a team --</option>
          {teams.map((team) => (
            <option key={team} value={team} disabled={team === homeTeam}>
              {TEAM_NAMES[team]}
            </option>
          ))}
        </select>
      </div>

      <button onClick={handlePredict}>Predict</button>

      {result && !result.error && (
        <div className="result">
          <h2>
            {result.home_win_probability > result.away_win_probability
              ? `${TEAM_NAMES[result.home_team]} favoured`
              : `${TEAM_NAMES[result.away_team]} favoured`}
          </h2>
          <p className="confidence">{confidenceLabel(result.home_win_probability)}</p>

          <div className="bar">
            <div className="bar-home" style={{ width: `${result.home_win_probability * 100}%` }}>
              {(result.home_win_probability * 100).toFixed(0)}%
            </div>
            <div className="bar-away" style={{ width: `${result.away_win_probability * 100}%` }}>
              {(result.away_win_probability * 100).toFixed(0)}%
            </div>
          </div>

            <div className="matchup">
            <div>
              <img className="logo-big" src={logoUrl(result.home_team)} alt={result.home_team} />
              <div className="team-code">{result.home_team}</div>
              <div className="team-rating">Elo {result.home_rating}</div>
              <div className="team-label">HOME</div>
            </div>
            <div className="vs">vs</div>
            <div>
              <img className="logo-big" src={logoUrl(result.away_team)} alt={result.away_team} />
              <div className="team-code">{result.away_team}</div>
              <div className="team-rating">Elo {result.away_rating}</div>
              <div className="team-label">AWAY</div>
            </div>
          </div>

          <div className="score">
            {result.predicted_margin > 0
              ? `${result.home_team} by ~${result.predicted_margin}`
              : result.predicted_margin < 0
              ? `${result.away_team} by ~${Math.abs(result.predicted_margin)}`
              : 'Too close to call'}
          </div>
        </div>
      )}

      {result && result.error && (
        <div className="result">
          <p>{result.error}</p>
        </div>
      )}
    </div>
  )
}

export default MatchupPage