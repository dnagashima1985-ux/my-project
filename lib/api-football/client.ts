// API-Football client for injury data

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
