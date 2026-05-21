// TheStatsAPI client

const BASE_URL = 'https://api.thestatsapi.com/v1';
const API_KEY = process.env.STATS_API_KEY!;

async function request<T>(path: string, params: Record<string, string> = {}): Promise<T> {
  const url = new URL(`${BASE_URL}${path}`);
  Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));

  const res = await fetch(url.toString(), {
    headers: { 'X-Auth-Token': API_KEY },
    next: { revalidate: 3600 }, // cache 1h
  });

  if (!res.ok) throw new Error(`TheStatsAPI error: ${res.status} ${path}`);
  return res.json();
}

export interface StatsAPIPlayer {
  id: string;
  name: string;
  age: number;
  nationality: string;
  current_club: string;
  league: string;
  position: string;
  stats: {
    goals: number;
    assists: number;
    xg: number;
    npxg: number;
    xa: number;
    shots: number;
    shots_on_target: number;
    pass_count: number;
    pass_accuracy: number;
    key_passes: number;
    dribble_success: number;
    dribble_success_rate: number;
    tackles: number;
    interceptions: number;
    aerial_duel_win_pct: number;
    yellow_cards: number;
    red_cards: number;
    appearances: number;
    minutes_played: number;
  };
}

export async function searchPlayers(params: {
  position?: string;
  league?: string;
  age_min?: number;
  age_max?: number;
  nationality?: string;
  page?: number;
}): Promise<{ players: StatsAPIPlayer[]; total: number }> {
  const query: Record<string, string> = {};
  if (params.position) query.position = params.position;
  if (params.league) query.league = params.league;
  if (params.age_min) query.age_min = String(params.age_min);
  if (params.age_max) query.age_max = String(params.age_max);
  if (params.nationality) query.nationality = params.nationality;
  if (params.page) query.page = String(params.page);

  return request('/players', query);
}

export async function getPlayer(id: string): Promise<StatsAPIPlayer> {
  return request(`/players/${id}`);
}

export async function getPlayerStats(id: string, season?: string): Promise<StatsAPIPlayer['stats']> {
  return request(`/players/${id}/stats`, season ? { season } : {});
}

export async function getLeaguePercentiles(
  playerId: string,
  leagueId: string,
  season: string
): Promise<Record<string, number>> {
  return request(`/players/${playerId}/percentiles`, { league: leagueId, season });
}
