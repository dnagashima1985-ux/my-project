import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@/lib/supabase/server';

export async function GET(
  _req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

  // Starter+ required for CSV
  const { data: profile } = await supabase
    .from('users')
    .select('plan')
    .eq('id', user.id)
    .single();

  if (profile?.plan === 'trial') {
    return NextResponse.json({ error: 'Starter plan required for CSV export' }, { status: 403 });
  }

  const { data: longlist } = await supabase
    .from('longlists')
    .select('player_ids, club_profiles(club_name)')
    .eq('id', id)
    .eq('user_id', user.id)
    .single();

  if (!longlist) return NextResponse.json({ error: 'Not found' }, { status: 404 });

  const entries = (longlist.player_ids as { player_id: string; fit_score: number; reasoning?: string }[]) ?? [];
  const playerIds = entries.map((e) => e.player_id);

  const { data: players } = await supabase
    .from('players')
    .select(`
      id, name, age, height_cm, nationality, preferred_foot,
      position, current_club, league, stats,
      player_style_profiles(primary_profile_id, confidence_level),
      player_injuries(risk_grade, risk_score, status)
    `)
    .in('id', playerIds);

  const playerMap = new Map((players ?? []).map((p) => [p.id, p]));

  const headers = [
    'Rank', 'Name', 'Age', 'Height', 'Nationality', 'Foot',
    'Position', 'Club', 'League',
    'Goals', 'Assists', 'xG', 'xA', 'Pass%', 'KeyPasses',
    'Dribble%', 'Tackles', 'Interceptions', 'AerialWin%',
    'StyleProfile', 'Confidence',
    'InjuryRisk', 'RiskScore',
    'FitScore', 'Reasoning',
  ];

  const rows = entries.map((e, i) => {
    const p = playerMap.get(e.player_id);
    if (!p) return Array(headers.length).fill('');

    const stats = (p.stats ?? {}) as Record<string, number>;
    const styleProfile = (p.player_style_profiles as { primary_profile_id: string; confidence_level: string }[])?.[0];
    const injury = (p.player_injuries as { risk_grade: string; risk_score: number; status: string }[])?.[0];

    return [
      i + 1,
      p.name,
      p.age ?? '',
      p.height_cm ?? '',
      p.nationality ?? '',
      p.preferred_foot ?? '',
      p.position ?? '',
      p.current_club ?? '',
      p.league ?? '',
      stats.goals ?? '',
      stats.assists ?? '',
      Number(stats.xg ?? 0).toFixed(2),
      Number(stats.xa ?? 0).toFixed(2),
      stats.pass_accuracy ?? '',
      stats.key_passes ?? '',
      stats.dribble_success_rate ?? '',
      stats.tackles ?? '',
      stats.interceptions ?? '',
      stats.aerial_duel_win_pct ?? '',
      styleProfile?.primary_profile_id ?? '',
      styleProfile?.confidence_level ?? '',
      injury?.risk_grade ?? '',
      injury?.risk_score ?? '',
      e.fit_score,
      (e.reasoning ?? '').replace(/,/g, ';'),
    ];
  });

  const csvLines = [
    headers.join(','),
    ...rows.map((r) => r.join(',')),
  ];

  const cp = longlist.club_profiles as { club_name?: string } | null;
  const filename = `ScoutIQ_${(cp?.club_name ?? 'Longlist').replace(/\s/g, '_')}.csv`;

  return new NextResponse(csvLines.join('\n'), {
    headers: {
      'Content-Type': 'text/csv; charset=utf-8',
      'Content-Disposition': `attachment; filename="${filename}"`,
    },
  });
}
