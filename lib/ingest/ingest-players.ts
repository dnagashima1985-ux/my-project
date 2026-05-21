/**
 * Player ingestion from TheStatsAPI → Supabase.
 * Run via: npx tsx lib/ingest/ingest-players.ts
 * Or called from /api/cron/update-stats
 */

import { createClient } from '@supabase/supabase-js';
import { searchPlayers } from '@/lib/stats-api/client';
import { classifyProfile } from '@/lib/classify-profile';
import { calculateInjuryRiskScore, getPlayerSidelined } from '@/lib/api-football/client';

function getSupabase() {
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!
  );
}

const TARGET_LEAGUES = [
  'Premier League', 'La Liga', 'Bundesliga', 'Serie A', 'Ligue 1',
  'Eredivisie', 'Primeira Liga', 'Championship', 'Pro League',
  'J1 League', 'MLS',
];

const TARGET_POSITIONS = ['GK', 'CB', 'LB', 'RB', 'CDM', 'CM', 'CAM', 'LW', 'RW', 'ST', 'CF'];

export async function ingestPlayers() {
  const supabase = getSupabase();
  console.log('[ingest] Starting player ingestion...');
  let total = 0;

  for (const league of TARGET_LEAGUES) {
    for (const position of TARGET_POSITIONS) {
      try {
        const { players } = await searchPlayers({ league, position, page: 1 });
        console.log(`[ingest] ${league} / ${position}: ${players.length} players`);

        for (const p of players) {
          // Upsert player
          const { data: player, error } = await supabase
            .from('players')
            .upsert({
              source_id: p.id,
              name: p.name,
              age: p.age,
              nationality: p.nationality,
              current_club: p.current_club,
              league: p.league,
              position: p.position,
              stats: p.stats,
              last_updated_at: new Date().toISOString(),
            }, { onConflict: 'source_id' })
            .select('id')
            .single();

          if (error || !player) continue;

          // Classify play style profile
          const classification = classifyProfile({
            position: p.position,
            stats: p.stats,
          });

          await supabase
            .from('player_style_profiles')
            .upsert({
              player_id: player.id,
              primary_profile_id: classification.primary,
              secondary_profile_id: classification.secondary ?? null,
              profile_scores: classification.scores,
              confidence_level: classification.confidence,
              data_caveats: classification.caveats,
              last_updated_at: new Date().toISOString(),
            }, { onConflict: 'player_id' });

          total++;
        }

        // Rate limit: stay well under 500k requests/mo
        await sleep(200);
      } catch (err) {
        console.error(`[ingest] Error ${league}/${position}:`, err);
      }
    }
  }

  console.log(`[ingest] Done. Ingested ${total} players.`);
  return total;
}

export async function ingestInjuries(playerApiFootballIdMap: Record<string, number>) {
  const supabase = getSupabase();
  console.log('[ingest] Starting injury ingestion...');
  let total = 0;

  const { data: players } = await supabase
    .from('players')
    .select('id, source_id')
    .limit(1000);

  if (!players) return 0;

  for (const player of players) {
    const apiFootballId = playerApiFootballIdMap[player.source_id ?? ''];
    if (!apiFootballId) continue;

    try {
      const { response: history } = await getPlayerSidelined(apiFootballId);
      const { score, grade } = calculateInjuryRiskScore(history);

      const current = history.find((h) => !h.end);

      await supabase
        .from('player_injuries')
        .upsert({
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
          total_missed_games: history.length * 3, // rough estimate
          last_updated_at: new Date().toISOString(),
        }, { onConflict: 'player_id' });

      total++;
      await sleep(500); // API-Football free tier: 100 requests/day
    } catch (err) {
      console.error(`[ingest] Injury error for player ${player.id}:`, err);
    }
  }

  console.log(`[ingest] Injury ingestion done. ${total} players updated.`);
  return total;
}

function sleep(ms: number) {
  return new Promise((r) => setTimeout(r, ms));
}
