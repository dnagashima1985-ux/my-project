/**
 * EQ analysis ingestion via NewsAPI → Claude API → Supabase.
 * Run via cron or manually.
 */

import { createClient } from '@supabase/supabase-js';
import { analyzeEQ } from '@/lib/claude/client';

function getSupabase() {
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!
  );
}

const NEWS_API_KEY = process.env.NEWS_API_KEY!;
const GNEWS_API_KEY = process.env.GNEWS_API_KEY!;

interface Article {
  title: string;
  date: string;
  source: string;
  url: string;
  content: string;
}

async function fetchArticlesNewsAPI(playerName: string): Promise<Article[]> {
  const url = `https://newsapi.org/v2/everything?q=${encodeURIComponent(`"${playerName}"`)}&language=en&sortBy=publishedAt&pageSize=20&apiKey=${NEWS_API_KEY}`;
  const res = await fetch(url);
  if (!res.ok) return [];
  const data = await res.json();

  return (data.articles ?? []).map((a: Record<string, unknown>) => ({
    title: String(a.title ?? ''),
    date: String(a.publishedAt ?? '').slice(0, 10),
    source: String((a.source as Record<string, string>)?.name ?? ''),
    url: String(a.url ?? ''),
    content: String(a.description ?? a.content ?? ''),
  }));
}

async function fetchArticlesGNews(playerName: string): Promise<Article[]> {
  if (!GNEWS_API_KEY) return [];
  const url = `https://gnews.io/api/v4/search?q=${encodeURIComponent(`"${playerName}"`)}&lang=en&max=10&token=${GNEWS_API_KEY}`;
  const res = await fetch(url);
  if (!res.ok) return [];
  const data = await res.json();

  return (data.articles ?? []).map((a: Record<string, unknown>) => ({
    title: String(a.title ?? ''),
    date: String(a.publishedAt ?? '').slice(0, 10),
    source: String((a.source as Record<string, string>)?.name ?? ''),
    url: String((a as Record<string, unknown>).url ?? ''),
    content: String(a.description ?? a.content ?? ''),
  }));
}

export async function ingestEQForPlayer(playerId: string, playerName: string): Promise<void> {
  const supabase = getSupabase();
  const [newsApiArticles, gnewsArticles] = await Promise.all([
    fetchArticlesNewsAPI(playerName),
    fetchArticlesGNews(playerName),
  ]);

  // Deduplicate by title
  const seen = new Set<string>();
  const articles: Article[] = [];
  for (const a of [...newsApiArticles, ...gnewsArticles]) {
    if (!seen.has(a.title)) {
      seen.add(a.title);
      articles.push(a);
    }
  }

  if (articles.length < 5) {
    await supabase.from('eq_analyses').upsert({
      player_id: playerId,
      article_count: articles.length,
      total_score: 0,
      grade: 'UNKNOWN',
      dimensions: null,
      verdict: 'Insufficient data — minimum 5 articles required',
      analysed_at: new Date().toISOString(),
    }, { onConflict: 'player_id' });
    return;
  }

  const result = await analyzeEQ(playerName, articles);

  const grade =
    result.total_score >= 75 ? 'HIGH' :
    result.total_score >= 50 ? 'MEDIUM' :
    result.total_score >= 25 ? 'LOW' : 'UNKNOWN';

  await supabase.from('eq_analyses').upsert({
    player_id: playerId,
    article_count: articles.length,
    total_score: result.total_score,
    grade,
    dimensions: result.dimensions,
    verdict: result.verdict,
    analysed_at: new Date().toISOString(),
  }, { onConflict: 'player_id' });
}

export async function ingestEQBatch(limit = 50): Promise<number> {
  const supabase = getSupabase();
  // Prioritise shortlisted players first, then any without EQ data
  const { data: shortlisted } = await supabase
    .from('shortlists')
    .select('player_id, players(id, name)')
    .limit(limit);

  const players = (shortlisted ?? [])
    .map((s: Record<string, unknown>) => (s.players as { id: string; name: string } | null))
    .filter(Boolean) as { id: string; name: string }[];

  if (players.length < limit) {
    const { data: extras } = await supabase
      .from('players')
      .select('id, name')
      .not('id', 'in', `(${players.map((p) => `'${p.id}'`).join(',') || 'null'})`)
      .limit(limit - players.length);
    players.push(...(extras ?? []));
  }

  let done = 0;
  for (const player of players) {
    try {
      await ingestEQForPlayer(player.id, player.name);
      done++;
      await new Promise((r) => setTimeout(r, 1000)); // respect NewsAPI rate limit
    } catch (err) {
      console.error(`[EQ] Error for ${player.name}:`, err);
    }
  }

  return done;
}
