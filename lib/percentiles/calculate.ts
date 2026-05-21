/**
 * League-relative percentile calculation.
 * Given a player's stats and a set of all players in the same league+position,
 * returns a map of stat → percentile (0–100).
 */

import { createClient } from '@supabase/supabase-js';
import type { PlayerStats } from '@/types';

const PERCENTILE_STATS: (keyof PlayerStats)[] = [
  'goals', 'assists', 'xg', 'xa', 'shots', 'pass_accuracy',
  'key_passes', 'dribble_success_rate', 'tackles',
  'interceptions', 'aerial_duel_win_pct',
];

function percentileRank(value: number, population: number[]): number {
  if (!population.length) return 50;
  const below = population.filter((v) => v < value).length;
  return Math.round((below / population.length) * 100);
}

export async function calculatePercentilesForPlayer(
  playerId: string,
  supabaseUrl: string,
  supabaseServiceKey: string
): Promise<void> {
  const supabase = createClient(supabaseUrl, supabaseServiceKey);

  const { data: player } = await supabase
    .from('players')
    .select('position, league, stats')
    .eq('id', playerId)
    .single();

  if (!player?.stats || !player.position || !player.league) return;

  const { data: peers } = await supabase
    .from('players')
    .select('stats')
    .eq('position', player.position)
    .eq('league', player.league)
    .neq('id', playerId)
    .limit(500);

  if (!peers?.length) return;

  const season = new Date().getFullYear().toString();

  for (const stat of PERCENTILE_STATS) {
    const playerVal = (player.stats as PlayerStats)[stat];
    if (playerVal === undefined || playerVal === null) continue;

    const population = peers
      .map((p) => (p.stats as PlayerStats)[stat])
      .filter((v): v is number => v !== undefined && v !== null);

    if (!population.length) continue;

    const percentile = percentileRank(Number(playerVal), population.map(Number));

    await supabase.from('league_percentiles').upsert({
      player_id: playerId,
      league_id: player.league,
      season,
      stat_name: stat,
      percentile,
    }, { onConflict: 'player_id,league_id,season,stat_name' });
  }
}

export async function calculatePercentilesForAll(
  supabaseUrl: string,
  supabaseServiceKey: string
): Promise<number> {
  const supabase = createClient(supabaseUrl, supabaseServiceKey);

  const { data: players } = await supabase
    .from('players')
    .select('id')
    .limit(2000);

  if (!players) return 0;

  let done = 0;
  for (const player of players) {
    try {
      await calculatePercentilesForPlayer(player.id, supabaseUrl, supabaseServiceKey);
      done++;
    } catch {
      // continue
    }
  }

  return done;
}
