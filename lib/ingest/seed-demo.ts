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
  { source_id: 'demo-001', total_score: 78, grade: 'HIGH', verdict: 'Consistently takes responsibility in post-match interviews. Respected by teammates and noted for leadership qualities.' },
  { source_id: 'demo-002', total_score: 82, grade: 'HIGH', verdict: 'Strong motivation and self-awareness. No disciplinary issues. Positive media coverage across multiple sources.' },
  { source_id: 'demo-003', total_score: 55, grade: 'MEDIUM', verdict: 'Generally positive but occasional frustration on the pitch. No major incidents off the field.' },
  { source_id: 'demo-006', total_score: 44, grade: 'MEDIUM', verdict: 'Some disciplinary concerns. Red card incident with disputed circumstances. Generally cooperative with media.' },
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

export async function seedDemo() {
  const supabase = getSupabase();
  console.log('[seed] Starting demo data seed...');

  // Insert players
  const playerIdMap: Record<string, string> = {};

  for (const p of DEMO_PLAYERS) {
    const { data, error } = await supabase
      .from('players')
      .upsert(p, { onConflict: 'source_id' })
      .select('id, source_id')
      .single();

    if (error) { console.error('[seed] Player error:', error.message); continue; }
    if (data) playerIdMap[data.source_id] = data.id;
    console.log(`[seed] Upserted player: ${p.name}`);
  }

  // Insert injuries
  for (const inj of DEMO_INJURIES) {
    const playerId = playerIdMap[inj.source_id];
    if (!playerId) continue;

    await supabase.from('player_injuries').upsert({
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
  }

  // Insert EQ
  for (const eq of DEMO_EQ) {
    const playerId = playerIdMap[eq.source_id];
    if (!playerId) continue;

    await supabase.from('eq_analyses').upsert({
      player_id: playerId,
      article_count: 8,
      total_score: eq.total_score,
      grade: eq.grade,
      dimensions: {
        self_awareness:  { score: Math.round(eq.total_score * 0.22), evidence: [], flags: [] },
        self_regulation: { score: Math.round(eq.total_score * 0.20), evidence: [], flags: [] },
        motivation:      { score: Math.round(eq.total_score * 0.20), evidence: [], flags: [] },
        empathy:         { score: Math.round(eq.total_score * 0.19), evidence: [], flags: [] },
        social_skills:   { score: Math.round(eq.total_score * 0.19), evidence: [], flags: [] },
      },
      verdict: eq.verdict,
      analysed_at: new Date().toISOString(),
    }, { onConflict: 'player_id' });
  }

  // Insert transfer signals
  for (const sig of DEMO_TRANSFER_SIGNALS) {
    await supabase.from('transfer_signals').insert({
      ...sig,
      detected_at: new Date().toISOString(),
    });
  }

  console.log('[seed] Done.');
}

// Run directly
if (require.main === module) {
  seedDemo().then(() => process.exit(0));
}
