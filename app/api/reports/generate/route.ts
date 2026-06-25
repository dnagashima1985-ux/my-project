import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@/lib/supabase/server';
import { generateReport } from '@/lib/claude/client';
import type { Language, ReportAudience } from '@/types';

export async function POST(req: NextRequest) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

  const { data: profile } = await supabase
    .from('users')
    .select('plan')
    .eq('id', user.id)
    .single();

  const plan = profile?.plan ?? 'trial';
  const isPaidPlan = plan !== 'trial' && plan !== 'starter';

  if (!isPaidPlan) {
    // Trial/starter users get 1 free report
    const { count } = await supabase
      .from('reports')
      .select('id', { count: 'exact', head: true })
      .eq('user_id', user.id);

    if ((count ?? 0) >= 1) {
      return NextResponse.json(
        { error: 'Trial users can generate 1 report. Upgrade to Pro or Elite for unlimited reports.', redirect: '/settings#plans' },
        { status: 403 }
      );
    }
  }

  const body = await req.json();
  const { player_id, audience, language, scout_inputs } = body;

  // Fetch full player details
  const { data: player } = await supabase
    .from('players')
    .select(`
      *,
      player_style_profiles(*),
      player_injuries(*),
      league_percentiles(*),
      eq_analyses(*)
    `)
    .eq('id', player_id)
    .single();

  if (!player) return NextResponse.json({ error: 'Player not found' }, { status: 404 });

  // Generate with Claude
  const aiContent = await generateReport(
    player,
    audience as ReportAudience,
    language as Language,
    scout_inputs
  );

  const { data: report } = await supabase
    .from('reports')
    .insert({
      user_id: user.id,
      player_id,
      audience,
      language,
      scout_inputs,
      ai_content: aiContent,
      format: 'pdf',
    })
    .select()
    .single();

  return NextResponse.json({ id: report!.id });
}
