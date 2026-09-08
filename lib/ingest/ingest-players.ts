/**
 * Player stats ingestion from API-Football → Supabase.
 * Updates all players in the DB that have an api_football_id stored as source_id.
 * Called from /api/cron/update-stats (runs daily at 3am UTC via vercel.json).
 */

import { createClient } from '@supabase/supabase-js';
import {
  getPlayerStatsByApiId,
  searchPlayerByName,
  calculateInjuryRiskScore,
  getPlayerSidelined,
  type NormalisedPlayerStats,
} from '@/lib/api-football/client';
import { classifyProfile } from '@/lib/classify-profile';

function getSupabase() {
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!
  );
}

function currentSeason(): number {
  const now = new Date();
  // Football seasons: if before July, season started previous year
  return now.getMonth() < 6 ? now.getFullYear() - 1 : now.getFullYear();
}

async function upsertPlayer(
  supabase: ReturnType<typeof createClient>,
  p: NormalisedPlayerStats
): Promise<string | null> {
  const { data: player, error } = await supabase
    .from('players')
    .upsert(
      {
        source_id: String(p.api_football_id),
        name: p.name,
        age: p.age,
        nationality: p.nationality,
        height_cm: p.height_cm,
        current_club: p.current_club,
        league: p.league,
        position: p.position,
        stats: p.stats,
        last_updated_at: new Date().toISOString(),
      },
      { onConflict: 'source_id' }
    )
    .select('id')
    .single();

  if (error || !player) {
    console.error('[ingest] upsert error:', error?.message);
    return null;
  }

  const classification = classifyProfile({ position: p.position, stats: p.stats });
  await supabase
    .from('player_style_profiles')
    .upsert(
      {
        player_id: player.id,
        primary_profile_id: classification.primary,
        secondary_profile_id: classification.secondary ?? null,
        profile_scores: classification.scores,
        confidence_level: classification.confidence,
        data_caveats: classification.caveats,
        last_updated_at: new Date().toISOString(),
      },
      { onConflict: 'player_id' }
    );

  return player.id as string;
}

/** Daily cron: refresh stats for all tracked players (source_id = API-Football ID). */
export async function ingestPlayers(): Promise<number> {
  const supabase = getSupabase();
  const season = currentSeason();
  console.log(`[ingest] Refreshing player stats for season ${season}...`);

  const { data: tracked } = await supabase
    .from('players')
    .select('id, source_id, name')
    .not('source_id', 'is', null);

  if (!tracked?.length) {
    console.log('[ingest] No tracked players found.');
    return 0;
  }

  let updated = 0;
  for (const row of tracked) {
    const apiId = parseInt(row.source_id, 10);
    if (isNaN(apiId)) continue; // skip demo players with non-numeric source_id

    try {
      const stats = await getPlayerStatsByApiId(apiId, season);
      if (!stats) {
        console.warn(`[ingest] No stats for player ${row.name} (id ${apiId})`);
        continue;
      }
      await upsertPlayer(supabase, stats);
      updated++;
      await sleep(500); // stay within 100 req/day free tier
    } catch (err) {
      console.error(`[ingest] Error for ${row.name}:`, err);
    }
  }

  console.log(`[ingest] Done. Updated ${updated}/${tracked.length} players.`);
  return updated;
}

/**
 * Add a new player by name (one-off, called from the UI).
 * Searches API-Football, saves the best match, returns the Supabase player ID.
 */
export async function addPlayerByName(name: string): Promise<string | null> {
  const supabase = getSupabase();
  const season = currentSeason();

  const results = await searchPlayerByName(name, season);
  if (!results.length) return null;

  // Pick the result with the most minutes played as the best match
  const best = results.reduce((a, b) =>
    (a.stats.minutes_played ?? 0) >= (b.stats.minutes_played ?? 0) ? a : b
  );

  return upsertPlayer(supabase, best);
}

export async function ingestInjuries(): Promise<number> {
  const supabase = getSupabase();
  const { data: players } = await supabase
    .from('players')
    .select('id, source_id')
    .not('source_id', 'is', null);

  if (!players?.length) return 0;

  let total = 0;
  for (const player of players) {
    const apiId = parseInt(player.source_id, 10);
    if (isNaN(apiId)) continue;

    try {
      const { response: history } = await getPlayerSidelined(apiId);
      const { score, grade } = calculateInjuryRiskScore(history);
      const current = history.find((h) => !h.end);

      await supabase
        .from('player_injuries')
        .upsert(
          {
            player_id: player.id,
            status: current ? 'injured' : 'available',
            current_injury_type: current?.type ?? null,
            current_injury_since: current?.start ?? null,
            risk_score: score,
            risk_grade: grade,
            injury_history: history.map((h) => ({
              type: h.type,
              from: h.start,
              to: h.end,
              games_missed: 0,
            })),
            total_missed_games: history.length * 3,
            last_updated_at: new Date().toISOString(),
          },
          { onConflict: 'player_id' }
        );

      total++;
      await sleep(500);
    } catch (err) {
      console.error(`[ingest] Injury error for ${player.id}:`, err);
    }
  }

  return total;
}

function sleep(ms: number) {
  return new Promise((r) => setTimeout(r, ms));
}
