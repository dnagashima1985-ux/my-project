/**
 * Seed demo data for testing without external API keys.
 * Run: npx tsx lib/ingest/seed-demo.ts
 */

import { createClient } from '@supabase/supabase-js';

function getSupabase() {
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!
  );
}

const DEMO_PLAYERS = [
  {
    source_id: 'demo-001',
    name: 'Marcus Lindström',
    age: 24,
    height_cm: 182,
    nationality: 'Sweden',
    preferred_foot: 'Right',
    current_club: 'AIK',
    league: 'Allsvenskan',
    position: 'CM',
    stats: {
      goals: 7, assists: 9, xg: 6.2, npxg: 5.8, xa: 8.1,
      shots: 48, shots_on_target: 22,
      pass_count: 1840, pass_accuracy: 88,
      key_passes: 62,
      dribble_success: 38, dribble_success_rate: 71,
      tackles: 52, interceptions: 34,
      aerial_duel_win_pct: 44,
      yellow_cards: 3, red_cards: 0,
      appearances: 28, minutes_played: 2430,
    },
  },
  {
    source_id: 'demo-002',
    name: 'Yuki Tanaka',
    age: 22,
    height_cm: 175,
    nationality: 'Japan',
    preferred_foot: 'Left',
    current_club: 'Gamba Osaka',
    league: 'J1 League',
    position: 'CAM',
    stats: {
      goals: 11, assists: 14, xg: 9.7, npxg: 8.9, xa: 12.3,
      shots: 72, shots_on_target: 38,
      pass_count: 1560, pass_accuracy: 84,
      key_passes: 88,
      dribble_success: 61, dribble_success_rate: 78,
      tackles: 22, interceptions: 18,
      aerial_duel_win_pct: 32,
      yellow_cards: 2, red_cards: 0,
      appearances: 30, minutes_played: 2610,
    },
  },
  {
    source_id: 'demo-003',
    name: 'Rafael Dias',
    age: 27,
    height_cm: 189,
    nationality: 'Brazil',
    preferred_foot: 'Right',
    current_club: 'SC Braga',
    league: 'Primeira Liga',
    position: 'ST',
    stats: {
      goals: 18, assists: 5, xg: 16.4, npxg: 14.8, xa: 4.2,
      shots: 94, shots_on_target: 51,
      pass_count: 720, pass_accuracy: 74,
      key_passes: 28,
      dribble_success: 29, dribble_success_rate: 62,
      tackles: 14, interceptions: 9,
      aerial_duel_win_pct: 58,
      yellow_cards: 4, red_cards: 0,
      appearances: 32, minutes_played: 2760,
    },
  },
  {
    source_id: 'demo-004',
    name: 'Lasse Møller',
    age: 26,
    height_cm: 186,
    nationality: 'Denmark',
    preferred_foot: 'Right',
    current_club: 'FC Midtjylland',
    league: 'Superligaen',
    position: 'CDM',
    stats: {
      goals: 2, assists: 4, xg: 1.8, npxg: 1.6, xa: 3.4,
      shots: 22, shots_on_target: 10,
      pass_count: 2140, pass_accuracy: 91,
      key_passes: 24,
      dribble_success: 18, dribble_success_rate: 67,
      tackles: 84, interceptions: 71,
      aerial_duel_win_pct: 62,
      yellow_cards: 5, red_cards: 0,
      appearances: 29, minutes_played: 2550,
    },
  },
  {
    source_id: 'demo-005',
    name: 'Sébastien Aumont',
    age: 23,
    height_cm: 178,
    nationality: 'France',
    preferred_foot: 'Left',
    current_club: 'Stade Reims',
    league: 'Ligue 1',
    position: 'LW',
    stats: {
      goals: 9, assists: 11, xg: 7.9, npxg: 7.1, xa: 9.8,
      shots: 66, shots_on_target: 30,
      pass_count: 980, pass_accuracy: 81,
      key_passes: 54,
      dribble_success: 74, dribble_success_rate: 69,
      tackles: 28, interceptions: 22,
      aerial_duel_win_pct: 38,
      yellow_cards: 3, red_cards: 0,
      appearances: 27, minutes_played: 2340,
    },
  },
  {
    source_id: 'demo-006',
    name: 'Tomás Velázquez',
    age: 29,
    height_cm: 184,
    nationality: 'Argentina',
    preferred_foot: 'Right',
    current_club: 'Deportivo Alavés',
    league: 'La Liga',
    position: 'CB',
    stats: {
      goals: 2, assists: 1, xg: 1.4, npxg: 1.2, xa: 0.9,
      shots: 18, shots_on_target: 8,
      pass_count: 2380, pass_accuracy: 89,
      key_passes: 12,
      dribble_success: 8, dribble_success_rate: 57,
      tackles: 74, interceptions: 58,
      aerial_duel_win_pct: 71,
      yellow_cards: 6, red_cards: 1,
      appearances: 31, minutes_played: 2730,
    },
  },
  {
    source_id: 'demo-007',
    name: 'Kenji Watanabe',
    age: 25,
    height_cm: 181,
    nationality: 'Japan',
    preferred_foot: 'Right',
    current_club: 'Urawa Red Diamonds',
    league: 'J1 League',
    position: 'CB',
    stats: {
      goals: 3, assists: 2, xg: 2.1, npxg: 2.0, xa: 1.8,
      shots: 24, shots_on_target: 11,
      pass_count: 2210, pass_accuracy: 87,
      key_passes: 18,
      dribble_success: 11, dribble_success_rate: 61,
      tackles: 68, interceptions: 49,
      aerial_duel_win_pct: 67,
      yellow_cards: 4, red_cards: 0,
      appearances: 30, minutes_played: 2700,
    },
  },
  {
    source_id: 'demo-008',
    name: 'Nils Bergström',
    age: 21,
    height_cm: 180,
    nationality: 'Sweden',
    preferred_foot: 'Both',
    current_club: 'Malmö FF',
    league: 'Allsvenskan',
    position: 'RB',
    stats: {
      goals: 3, assists: 8, xg: 2.4, npxg: 2.1, xa: 7.2,
      shots: 28, shots_on_target: 14,
      pass_count: 1680, pass_accuracy: 83,
      key_passes: 32,
      dribble_success: 42, dribble_success_rate: 70,
      tackles: 48, interceptions: 36,
      aerial_duel_win_pct: 54,
      yellow_cards: 2, red_cards: 0,
      appearances: 26, minutes_played: 2280,
    },
  },
];

const DEMO_INJURIES = [
  { source_id: 'demo-001', status: 'available', risk_score: 18, risk_grade: 'LOW',  injury_history: [] },
  { source_id: 'demo-002', status: 'available', risk_score: 12, risk_grade: 'LOW',  injury_history: [] },
  { source_id: 'demo-003', status: 'available', risk_score: 42, risk_grade: 'MEDIUM', injury_history: [
    { type: 'Muscle', from: '2024-09-12', to: '2024-10-05', games_missed: 4 },
  ]},
  { source_id: 'demo-004', status: 'available', risk_score: 22, risk_grade: 'LOW',  injury_history: [] },
  { source_id: 'demo-005', status: 'injured',   risk_score: 58, risk_grade: 'HIGH', injury_history: [
    { type: 'Ligament', from: '2024-11-20', to: null, games_missed: 0 },
    { type: 'Muscle',   from: '2024-03-08', to: '2024-03-28', games_missed: 3 },
  ], current_injury_type: 'Ligament', current_injury_since: '2024-11-20', return_estimate: '2025-02-10' },
  { source_id: 'demo-006', status: 'available', risk_score: 35, risk_grade: 'MEDIUM', injury_history: [
    { type: 'Muscle', from: '2024-01-15', to: '2024-02-01', games_missed: 3 },
  ]},
  { source_id: 'demo-007', status: 'available', risk_score: 15, risk_grade: 'LOW',  injury_history: [] },
  { source_id: 'demo-008', status: 'available', risk_score: 8,  risk_grade: 'LOW',  injury_history: [] },
];

const DEMO_EQ = [
  {
    source_id: 'demo-001', total_score: 78, grade: 'HIGH',
    verdict: 'Consistently takes responsibility in post-match interviews. Respected by teammates and noted for leadership qualities.',
    evidence: {
      self_awareness:  ['Post-match interview vs Djurgården (2024-04-18, Aftonbladet) — credited teammates, did not deflect criticism after 1-0 loss'],
      self_regulation: ['No disciplinary sanctions across 28 appearances (Allsvenskan official records 2024)'],
      motivation:      ['Pre-season interview (2024-01-30, Fotbollskanalen) — expressed ambition to reach European level within two years'],
      empathy:         ['Captain\'s statement after Hammarby derby (2024-05-05, SVT Sport) — publicly praised young substitute\'s impact'],
      social_skills:   ['Teammate quotes in squad profile (2024-08-12, AIK official) — described as "calm head in tense moments"'],
    },
    flags: {},
  },
  {
    source_id: 'demo-002', total_score: 82, grade: 'HIGH',
    verdict: 'Strong motivation and self-awareness. No disciplinary issues. Positive media coverage across multiple sources.',
    evidence: {
      self_awareness:  ['Post-match quotes after J1 loss (2024-06-22, Sponichi) — acknowledged personal positioning error'],
      self_regulation: ['Zero bookings in 30 J1 League appearances (J.League official stats 2024)'],
      motivation:      ['Interview on European ambitions (2024-02-14, Goal Japan) — detailed training improvements made in off-season'],
      empathy:         ['Gamba Osaka team interview (2024-09-01, NHK Sports) — praised youth academy integration'],
      social_skills:   ['Three separate teammates cited him as team leader in end-of-season awards coverage (2024-12-01, Sportiva)'],
    },
    flags: {},
  },
  {
    source_id: 'demo-003', total_score: 55, grade: 'MEDIUM',
    verdict: 'Generally positive but occasional frustration on the pitch. No major incidents off the field.',
    evidence: {
      self_awareness:  ['Post-match comment after Porto loss (2024-10-03, Record) — acknowledged missed chances but attributed some to goalkeeper'],
      self_regulation: ['Yellow card for dissent vs Sporting CP (2024-11-09, Zerozero) — disputed referee decision publicly'],
      motivation:      ['Pre-season interview (2024-01-20, A Bola) — stated goal of 20 league goals'],
      empathy:         [],
      social_skills:   ['Described as "professional" by manager in press conference (2024-07-15, SC Braga official)'],
    },
    flags: {
      self_awareness: ['⚠ Single source claim that he argued with assistant coach — not corroborated (2024-09-28, anonymous forum post)'],
    },
  },
  {
    source_id: 'demo-006', total_score: 44, grade: 'MEDIUM',
    verdict: 'Some disciplinary concerns. Red card incident with disputed circumstances. Generally cooperative with media.',
    evidence: {
      self_awareness:  ['Post-red card interview (2024-03-17, Marca) — disputed the decision rather than accepting responsibility'],
      self_regulation: ['Red card vs Villarreal (2024-03-14, La Liga official) — straight red for violent conduct; later reduced on appeal'],
      motivation:      ['Training ground profile (2024-08-05, Alavés official) — described as dedicated and first to arrive'],
      empathy:         [],
      social_skills:   ['Generally positive media presence; no dressing room incidents reported'],
    },
    flags: {},
  },
];

const DEMO_PERCENTILES: Array<{
  source_id: string;
  league_id: string;
  stats: Record<string, number>;
}> = [
  {
    source_id: 'demo-001',
    league_id: 'Allsvenskan',
    stats: { goals: 72, assists: 84, xg: 68, xa: 79, pass_accuracy: 76, key_passes: 74, dribble_success_rate: 65, tackles: 58, interceptions: 55, aerial_duel_win_pct: 48 },
  },
  {
    source_id: 'demo-002',
    league_id: 'J1 League',
    stats: { goals: 79, assists: 91, xg: 84, xa: 93, pass_accuracy: 65, key_passes: 91, dribble_success_rate: 82, tackles: 34, interceptions: 28, aerial_duel_win_pct: 31 },
  },
  {
    source_id: 'demo-003',
    league_id: 'Primeira Liga',
    stats: { goals: 94, assists: 61, xg: 91, xa: 52, pass_accuracy: 48, key_passes: 44, dribble_success_rate: 58, tackles: 28, interceptions: 22, aerial_duel_win_pct: 74 },
  },
  {
    source_id: 'demo-004',
    league_id: 'Superligaen',
    stats: { goals: 28, assists: 44, xg: 22, xa: 38, pass_accuracy: 92, key_passes: 35, dribble_success_rate: 61, tackles: 91, interceptions: 88, aerial_duel_win_pct: 79 },
  },
  {
    source_id: 'demo-005',
    league_id: 'Ligue 1',
    stats: { goals: 71, assists: 84, xg: 72, xa: 87, pass_accuracy: 58, key_passes: 79, dribble_success_rate: 77, tackles: 44, interceptions: 38, aerial_duel_win_pct: 35 },
  },
  {
    source_id: 'demo-006',
    league_id: 'La Liga',
    stats: { goals: 44, assists: 31, xg: 38, xa: 24, pass_accuracy: 84, key_passes: 22, dribble_success_rate: 42, tackles: 84, interceptions: 77, aerial_duel_win_pct: 88 },
  },
  {
    source_id: 'demo-007',
    league_id: 'J1 League',
    stats: { goals: 51, assists: 42, xg: 47, xa: 36, pass_accuracy: 79, key_passes: 31, dribble_success_rate: 54, tackles: 77, interceptions: 68, aerial_duel_win_pct: 82 },
  },
  {
    source_id: 'demo-008',
    league_id: 'Allsvenskan',
    stats: { goals: 48, assists: 75, xg: 44, xa: 82, pass_accuracy: 62, key_passes: 58, dribble_success_rate: 72, tackles: 65, interceptions: 61, aerial_duel_win_pct: 66 },
  },
];

const DEMO_TRANSFER_SIGNALS = [
  {
    interested_club: 'FC Utrecht',
    target_player: 'Marcus Lindström',
    target_club: 'AIK',
    position: 'CM',
    heat: 'warm',
    confidence: 'rumour',
    source: 'Expressen',
    quote: 'FC Utrecht have scouted Lindström twice this season, according to sources close to the club.',
  },
  {
    interested_club: 'Eredivisie Club A',
    target_player: 'Yuki Tanaka',
    target_club: 'Gamba Osaka',
    position: 'CAM',
    heat: 'hot',
    confidence: 'confirmed',
    source: 'Goal Japan',
    quote: 'Multiple European clubs are actively tracking Tanaka. A summer move is increasingly likely.',
  },
  {
    interested_club: 'Championship Club',
    target_player: 'Rafael Dias',
    target_club: 'SC Braga',
    position: 'ST',
    heat: 'early',
    confidence: 'speculation',
    source: 'A Bola',
    quote: 'Dias has attracted interest from England following his impressive Primeira Liga campaign.',
  },
];

export async function seedDemo(): Promise<{ ok: boolean; errors: string[] }> {
  const supabase = getSupabase();
  const errors: string[] = [];
  console.log('[seed] Starting demo data seed...');

  // Insert players
  const playerIdMap: Record<string, string> = {};

  for (const p of DEMO_PLAYERS) {
    const { data, error } = await supabase
      .from('players')
      .upsert(p, { onConflict: 'source_id' })
      .select('id, source_id')
      .single();

    if (error) {
      const msg = `Player ${p.name}: ${error.message}`;
      console.error('[seed]', msg);
      errors.push(msg);
      continue;
    }
    if (data) playerIdMap[data.source_id] = data.id;
    console.log(`[seed] Upserted player: ${p.name}`);
  }

  // Insert injuries
  for (const inj of DEMO_INJURIES) {
    const playerId = playerIdMap[inj.source_id];
    if (!playerId) continue;

    const { error } = await supabase.from('player_injuries').upsert({
      player_id: playerId,
      status: inj.status,
      risk_score: inj.risk_score,
      risk_grade: inj.risk_grade,
      injury_history: inj.injury_history,
      total_missed_games: (inj.injury_history as { games_missed: number }[]).reduce((s, h) => s + h.games_missed, 0),
      current_injury_type: (inj as unknown as Record<string, string>).current_injury_type ?? null,
      current_injury_since: (inj as unknown as Record<string, string>).current_injury_since ?? null,
      return_estimate: (inj as unknown as Record<string, string>).return_estimate ?? null,
      last_updated_at: new Date().toISOString(),
    }, { onConflict: 'player_id' });

    if (error) {
      const msg = `Injury ${inj.source_id}: ${error.message}`;
      console.error('[seed]', msg);
      errors.push(msg);
    }
  }

  // Insert EQ — delete first to avoid upsert constraint issues
  for (const eq of DEMO_EQ) {
    const playerId = playerIdMap[eq.source_id];
    if (!playerId) continue;

    await supabase.from('eq_analyses').delete().eq('player_id', playerId);

    const ev = (eq as unknown as { evidence?: Record<string, string[]> }).evidence ?? {};
    const fl = (eq as unknown as { flags?: Record<string, string[]> }).flags ?? {};
    const { error } = await supabase.from('eq_analyses').insert({
      player_id: playerId,
      article_count: 8,
      total_score: eq.total_score,
      grade: eq.grade,
      dimensions: {
        self_awareness:  { score: Math.round(eq.total_score * 0.22), evidence: ev.self_awareness  ?? [], flags: fl.self_awareness  ?? [] },
        self_regulation: { score: Math.round(eq.total_score * 0.20), evidence: ev.self_regulation ?? [], flags: fl.self_regulation ?? [] },
        motivation:      { score: Math.round(eq.total_score * 0.20), evidence: ev.motivation      ?? [], flags: fl.motivation      ?? [] },
        empathy:         { score: Math.round(eq.total_score * 0.19), evidence: ev.empathy         ?? [], flags: fl.empathy         ?? [] },
        social_skills:   { score: Math.round(eq.total_score * 0.19), evidence: ev.social_skills   ?? [], flags: fl.social_skills   ?? [] },
      },
      verdict: eq.verdict,
      analysed_at: new Date().toISOString(),
    });

    if (error) {
      const msg = `EQ ${eq.source_id}: ${error.message}`;
      console.error('[seed]', msg);
      errors.push(msg);
    } else {
      console.log(`[seed] Inserted EQ for ${eq.source_id}`);
    }
  }

  // Insert league percentiles — delete first then insert
  for (const perc of DEMO_PERCENTILES) {
    const playerId = playerIdMap[perc.source_id];
    if (!playerId) continue;

    await supabase.from('league_percentiles').delete()
      .eq('player_id', playerId)
      .eq('league_id', perc.league_id)
      .eq('season', '2024/25');

    const rows = Object.entries(perc.stats).map(([stat_name, percentile]) => ({
      player_id: playerId,
      league_id: perc.league_id,
      season: '2024/25',
      stat_name,
      percentile,
    }));

    const { error } = await supabase.from('league_percentiles').insert(rows);

    if (error) {
      const msg = `Percentiles ${perc.source_id}: ${error.message}`;
      console.error('[seed]', msg);
      errors.push(msg);
    } else {
      console.log(`[seed] Inserted percentiles for ${perc.source_id}`);
    }
  }

  // Insert transfer signals (skip duplicates silently)
  for (const sig of DEMO_TRANSFER_SIGNALS) {
    await supabase.from('transfer_signals').insert({
      ...sig,
      detected_at: new Date().toISOString(),
    });
  }

  console.log('[seed] Done.', errors.length ? `Errors: ${errors.length}` : 'All OK');
  return { ok: errors.length === 0, errors };
}

// Run directly
if (require.main === module) {
  seedDemo().then(() => process.exit(0));
}
