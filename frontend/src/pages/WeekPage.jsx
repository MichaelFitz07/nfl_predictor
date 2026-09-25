import { useState, useEffect } from 'react'
import '../App.css'

function WeekPage() {
  const [week, setWeek] = useState(3)        // default to current week
  const [games, setGames] = useState([])

  // fetch the selected week's games whenever the week changes
  useEffect(() => {
    fetch(`http://127.0.0.1:8000/week?week_number=${week}`)
      .then((response) => response.json())
      .then((data) => setGames(data.games))
  }, [week])

  return (
    <div className="card wide">
      <h1>Week <span>{week}</span></h1>

      {/* week selector */}
      <div className="picker">
        <label>Week</label>
        <select value={week} onChange={(e) => setWeek(Number(e.target.value))}>
          {Array.from({ length: 18 }, (_, i) => i + 1).map((w) => (
            <option key={w} value={w}>Week {w}</option>
          ))}
        </select>
      </div>

      {/* list of game predictions */}
      {games.map((g, i) => {
        const homeFav = g.home_win_probability > g.away_win_probability
        const favTeam = homeFav ? g.home_team : g.away_team
        const favPct = Math.round((homeFav ? g.home_win_probability : g.away_win_probability) * 100)

        // for played games, did our pick win?
        let correct = null
        if (g.played) {
          const homeWon = g.home_score > g.away_score
          correct = homeWon === homeFav
        }

        return (
          <div className="game-row" key={i}>
            <div className="game-teams">
              {g.away_team} @ {g.home_team}
            </div>
            <div className="game-pred">
              {favTeam} {favPct}%
            </div>
            {g.played && (
              <div className="game-actual">
                {g.away_score}-{g.home_score} {correct ? '✅' : '❌'}
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}

export default WeekPage