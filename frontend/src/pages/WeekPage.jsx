import { useState, useEffect } from 'react'
import '../App.css'

// espn logo urls - most match the team code lowercased, a few need mapping
const logoUrl = (team) => {
  const map = { LA: 'lar', LAC: 'lac', LV: 'lv', WAS: 'wsh', JAX: 'jax' }
  const code = (map[team] || team).toLowerCase()
  return `https://a.espncdn.com/i/teamlogos/nfl/500/${code}.png`
}

function WeekPage() {
  const [week, setWeek] = useState(3)
  const [games, setGames] = useState([])

  useEffect(() => {
    fetch(`http://127.0.0.1:8000/week?week_number=${week}`)
      .then((r) => r.json())
      .then((data) => setGames(data.games))
  }, [week])

  return (
    <div className="week-wrap">
      <div className="week-head">
        <h1 className="week-title">WEEK {week}</h1>
        <select className="week-select" value={week} onChange={(e) => setWeek(Number(e.target.value))}>
          {Array.from({ length: 18 }, (_, i) => i + 1).map((w) => (
            <option key={w} value={w}>Week {w}</option>
          ))}
        </select>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px', width: '100%' }}>
        {games.map((g, i) => {
          const homePct = Math.round(g.home_win_probability * 100)
          const awayPct = 100 - homePct
          const homeFav = homePct >= awayPct
          let correct = null
          if (g.played) correct = (g.home_score > g.away_score) === homeFav

          return (
            <div className="gcard" key={i}>
              <div className="gcard-teams">
                <img className="logo" src={logoUrl(g.home_team)} alt={g.home_team} />
                <span className={homeFav ? 'tm fav' : 'tm'}>{g.home_team}</span>
                <span className="at">vs</span>
                <span className={!homeFav ? 'tm fav' : 'tm'}>{g.away_team}</span>
                <img className="logo" src={logoUrl(g.away_team)} alt={g.away_team} />
              </div>

              <div className="split">
                <div className="split-home" style={{ width: `${homePct}%` }}>
                  <span className="pct">{homePct}</span>
                </div>
                <div className="split-away" style={{ width: `${awayPct}%` }}>
                  <span className="pct">{awayPct}</span>
                </div>
              </div>

              <div className="gcard-foot">
                {g.played ? (
                  <span className={correct ? 'res hit' : 'res miss'}>
                    {g.home_score}–{g.away_score} {correct ? 'HIT' : 'MISS'}
                  </span>
                ) : (
                  <span className="res upcoming">UPCOMING</span>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default WeekPage