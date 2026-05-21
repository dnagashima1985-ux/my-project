/**
 * Market Intelligence: daily transfer signal collection.
 * Fetches news articles → Claude API extracts signals → Supabase.
 */

import { createClient } from '@supabase/supabase-js';
import { extractTransferSignals } from '@/lib/claude/client';

function getSupabase() {
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!
  );
}

const NEWS_API_KEY = process.env.NEWS_API_KEY!;

const TRANSFER_QUERIES = [
  'football transfer rumour linked',
  'premier league transfer window bid',
  'bundesliga transfer target scout',
  'la liga transfer interest offer',
  'serie a transfer deal agreed',
  'ligue 1 transfer negotiate',
  'eredivisie transfer linked',
  'j1 league transfer import',
];

interface RawArticle {
  title: string;
  date: string;
  source: string;
  content: string;
}

async function fetchTransferNews(): Promise<RawArticle[]> {
  const articles: RawArticle[] = [];
  const seen = new Set<string>();

  for (const q of TRANSFER_QUERIES) {
    try {
      const url = `https://newsapi.org/v2/everything?q=${encodeURIComponent(q)}&language=en&sortBy=publishedAt&pageSize=20&apiKey=${NEWS_API_KEY}`;
      const res = await fetch(url);
      if (!res.ok) continue;
      const data = await res.json();

      for (const a of data.articles ?? []) {
        if (!seen.has(a.title)) {
          seen.add(a.title);
          articles.push({
            title: a.title ?? '',
            date: a.publishedAt?.slice(0, 10) ?? '',
            source: a.source?.name ?? '',
            content: `${a.title ?? ''} ${a.description ?? ''} ${a.content ?? ''}`.trim(),
          });
        }
      }

      await new Promise((r) => setTimeout(r, 300));
    } catch {
      // continue on individual query failure
    }
  }

  return articles;
}

export async function runMarketIntelligence(): Promise<number> {
  const supabase = getSupabase();
  console.log('[MI] Starting market intelligence ingestion...');

  const articles = await fetchTransferNews();
  console.log(`[MI] Fetched ${articles.length} articles`);

  if (!articles.length) return 0;

  // Get all elite users' clubs
  const { data: userClubs } = await supabase
    .from('user_clubs')
    .select('user_id, club_name, league, tier, budget_range, style')
    .limit(100);

  const registeredClubs = (userClubs ?? []).map((c: Record<string, string>) => c.club_name);

  // Process in batches of 20 articles
  const batchSize = 20;
  let totalSignals = 0;

  for (let i = 0; i < articles.length; i += batchSize) {
    const batch = articles.slice(i, i + batchSize);
    const clubContext = registeredClubs.length ? registeredClubs[0] : 'a professional club';

    try {
      const signals = await extractTransferSignals(batch, clubContext) as TransferSignal[];

      for (const signal of signals) {
        if (!signal.target_player || !signal.interested_club) continue;

        await supabase.from('transfer_signals').insert({
          interested_club: signal.interested_club,
          target_player: signal.target_player,
          target_club: signal.target_club ?? '',
          position: signal.position ?? '',
          heat: signal.heat ?? 'early',
          confidence: signal.confidence ?? 'speculation',
          source: signal.source ?? '',
          quote: signal.quote ?? '',
          detected_at: new Date().toISOString(),
        });

        totalSignals++;
      }
    } catch (err) {
      console.error('[MI] Extraction error:', err);
    }

    await new Promise((r) => setTimeout(r, 1000));
  }

  // Generate MI recommendations for each elite user
  if (userClubs?.length && totalSignals > 0) {
    await generateRecommendations(userClubs as UserClub[]);
  }

  console.log(`[MI] Done. ${totalSignals} signals stored.`);
  return totalSignals;
}

async function generateRecommendations(userClubs: UserClub[]) {
  const supabase = getSupabase();
  const { data: recentSignals } = await supabase
    .from('transfer_signals')
    .select('*')
    .gte('detected_at', new Date(Date.now() - 86400000).toISOString())
    .order('detected_at', { ascending: false })
    .limit(50);

  if (!recentSignals?.length) return;

  for (const userClub of userClubs) {
    for (const signal of recentSignals as TransferSignal[]) {
      // Find similar alternative players by position
      const { data: alternatives } = await supabase
        .from('players')
        .select('id, name, position, current_club, league, stats')
        .eq('position', signal.position ?? '')
        .neq('current_club', signal.target_club ?? '')
        .limit(5);

      if (!alternatives?.length) continue;

      const fitScores: Record<string, number> = {};
      alternatives.forEach((p: Record<string, unknown>, i: number) => {
        fitScores[p.id as string] = Math.max(50, 90 - i * 10);
      });

      await supabase.from('mi_recommendations').insert({
        user_id: userClub.user_id,
        signal_id: (signal as unknown as Record<string, string>).id,
        alt_player_ids: alternatives.map((p: Record<string, unknown>) => p.id),
        fit_scores: fitScores,
        created_at: new Date().toISOString(),
      });
    }
  }
}

interface TransferSignal {
  interested_club: string;
  target_player: string;
  target_club?: string;
  position?: string;
  heat?: string;
  confidence?: string;
  source?: string;
  quote?: string;
}

interface UserClub {
  user_id: string;
  club_name: string;
  league: string;
  tier: string;
  budget_range: string;
  style: string;
}
