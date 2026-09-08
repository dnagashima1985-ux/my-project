// API-Football client

const BASE_URL = 'https://v3.football.api-sports.io';
const API_KEY = process.env.API_FOOTBALL_KEY!;

async function request<T>(path: string, params: Record<string, string> = {}): Promise<T> {
  const url = new URL(`${BASE_URL}${path}`);
  Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));

  const res = await fetch(url.toString(), {
    headers: { 'x-apisports-key': API_KEY },
    next: { revalidate: 3600 },
  });

  if (!res.ok) throw new Error(`API-Football error: ${res.status} ${path}`);
  return res.json();
}

// ── Player stats ──────────────────────────────────────────────────────────────

export interface APIFootballPlayerResponse {
  player: {
    id: number;
    name: string;
    age: number;
    birth: { date: string; country: string };
    nationality: string;
    height: string | null; // "178 cm"
    weight: string | null;
    photo: string;
  };
  statistics: Array<{
    team: { id: number; name: string };
    league: { id: number; name: string; season: number };
    games: { appearences: number | null; minutes: number | null; position: string };
    goals: { total: number | null; assists: number | null };
    shots: { total: number | null; on: number | null };
    passes: { total: number | null; key: number | null; accuracy: string | number | null };
    tackles: { total: number | null; interceptions: number | null };
    duels: { total: number | null; won: number | null };
    dribbles: { attempts: number | null; success: number | null };
    cards: { yellow: number | null; red: number | null };
  }>;
}

export interface NormalisedPlayerStats {
  api_football_id: number;
  name: string;
  age: number;
  nationality: string;
  height_cm: number | undefined;
  current_club: string;
  league: string;
  position: string;
  stats: {
    goals: number;
    assists: number;
    xg?: number;
    npxg?: number;
    xa?: number;
    shots: number;
    shots_on_target: number;
    pass_count: number;
    pass_accuracy: number;
    key_passes: number;
    dribble_success: number;
    dribble_success_rate: number;
    tackles: number;
    interceptions: number;
    aerial_duel_win_pct?: number;
    yellow_cards: number;
    red_cards: number;
    appearances: number;
    minutes_played: number;
  };
}

function normalise(r: APIFootballPlayerResponse): NormalisedPlayerStats | null {
  const s = r.statistics[0];
  if (!s) return null;

  const heightCm = r.player.height
    ? parseInt(r.player.height.replace(/\D/g, ''), 10) || null
    : null;

  const passAcc = typeof s.passes.accuracy === 'string'
    ? parseFloat(s.passes.accuracy)
    : (s.passes.accuracy ?? 0);

  const dribbleAttempts = s.dribbles.attempts ?? 0;
  const dribbleSuccess = s.dribbles.success ?? 0;

  const duelTotal = s.duels.total ?? 0;
  const duelWon = s.duels.won ?? 0;

  return {
    api_football_id: r.player.id,
    name: r.player.name,
    age: r.player.age,
    nationality: r.player.nationality,
    height_cm: heightCm ?? undefined,
    current_club: s.team.name,
    league: s.league.name,
    position: s.games.position,
    stats: {
      goals: s.goals.total ?? 0,
      assists: s.goals.assists ?? 0,
      shots: s.shots.total ?? 0,
      shots_on_target: s.shots.on ?? 0,
      pass_count: s.passes.total ?? 0,
      pass_accuracy: passAcc,
      key_passes: s.passes.key ?? 0,
      dribble_success: dribbleSuccess,
      dribble_success_rate: dribbleAttempts > 0 ? (dribbleSuccess / dribbleAttempts) * 100 : 0,
      tackles: s.tackles.total ?? 0,
      interceptions: s.tackles.interceptions ?? 0,
      aerial_duel_win_pct: duelTotal > 0 ? (duelWon / duelTotal) * 100 : undefined,
      yellow_cards: s.cards.yellow ?? 0,
      red_cards: s.cards.red ?? 0,
      appearances: s.games.appearences ?? 0,
      minutes_played: s.games.minutes ?? 0,
    },
  };
}

export async function searchPlayerByName(
  name: string,
  season: number
): Promise<NormalisedPlayerStats[]> {
  const data = await request<{ response: APIFootballPlayerResponse[] }>(
    '/players',
    { search: name, season: String(season) }
  );
  return data.response.flatMap((r) => {
    const n = normalise(r);
    return n ? [n] : [];
  });
}

export async function getPlayerStatsByApiId(
  apiFootballId: number,
  season: number
): Promise<NormalisedPlayerStats | null> {
  const data = await request<{ response: APIFootballPlayerResponse[] }>(
    '/players',
    { id: String(apiFootballId), season: String(season) }
  );
  const first = data.response[0];
  return first ? normalise(first) : null;
}

export interface APIFootballInjury {
  player: { id: number; name: string };
  team: { id: number; name: string };
  fixture: { id: number; date: string };
  league: { id: number; name: string; season: number };
  type: string;
  reason: string;
}

export interface APIFootballSidelined {
  type: string;
  start: string;
  end: string | null;
}

export async function getCurrentInjuries(
  leagueId: number,
  season: number
): Promise<{ response: APIFootballInjury[] }> {
  return request('/injuries', {
    league: String(leagueId),
    season: String(season),
  });
}

export async function getPlayerSidelined(
  playerId: number
): Promise<{ response: APIFootballSidelined[] }> {
  return request('/sidelined', { player: String(playerId) });
}

export function calculateInjuryRiskScore(history: APIFootballSidelined[]): {
  score: number;
  grade: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
} {
  const now = new Date();
  const threeYearsAgo = new Date(now.getFullYear() - 3, now.getMonth(), now.getDate());

  const recent = history.filter((h) => new Date(h.start) >= threeYearsAgo);

  // Frequency (35%)
  const freq = recent.length;
  const freqScore = freq === 0 ? 0 : freq === 1 ? 15 : freq === 2 ? 35 : 50;

  // Longest absence (30%)
  let maxDays = 0;
  for (const h of recent) {
    if (h.end) {
      const days = (new Date(h.end).getTime() - new Date(h.start).getTime()) / 86400000;
      if (days > maxDays) maxDays = days;
    }
  }
  const absenceScore = maxDays < 28 ? 0 : maxDays < 56 ? 15 : maxDays < 112 ? 25 : 30;

  // Injury type (20%)
  const typeScores: Record<string, number> = {
    Muscle: 10, Muscular: 10,
    Ligament: 15,
    Fracture: 18,
    Meniscus: 20,
  };
  let typeScore = 0;
  for (const h of recent) {
    const key = Object.keys(typeScores).find((k) =>
      h.type.toLowerCase().includes(k.toLowerCase())
    );
    const s = key ? typeScores[key] : 5;
    if (s > typeScore) typeScore = s;
  }

  // Current season (15%)
  const currentYear = now.getFullYear();
  const currentSeason = history.filter((h) => new Date(h.start).getFullYear() === currentYear);
  const currentScore = currentSeason.length === 0 ? 0 :
    currentSeason.some((h) => !h.end) ? 15 : 8;

  const total = freqScore + absenceScore + typeScore + currentScore;

  const grade = total <= 25 ? 'LOW' :
    total <= 50 ? 'MEDIUM' :
    total <= 75 ? 'HIGH' : 'CRITICAL';

  return { score: Math.min(100, total), grade };
}
