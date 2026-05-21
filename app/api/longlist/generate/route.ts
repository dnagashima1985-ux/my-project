import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@/lib/supabase/server';
import { generateLonglist } from '@/lib/claude/client';
import { sendTrialLowEmail } from '@/lib/email/client';

export async function POST(req: NextRequest) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

  // Check trial / plan limits
  const { data: profile } = await supabase
    .from('users')
    .select('plan, trial_uses_remaining, preferred_language')
    .eq('id', user.id)
    .single();

  if (!profile) return NextResponse.json({ error: 'User not found' }, { status: 404 });

  if (profile.plan === 'trial' && profile.trial_uses_remaining <= 0) {
    return NextResponse.json({ error: 'Trial limit reached', redirect: '/settings#plans' }, { status: 403 });
  }

  if (profile.plan === 'starter') {
    // Count this month's longlists
    const startOfMonth = new Date();
    startOfMonth.setDate(1);
    startOfMonth.setHours(0, 0, 0, 0);
    const { count } = await supabase
      .from('longlists')
      .select('id', { count: 'exact', head: true })
      .eq('user_id', user.id)
      .gte('generated_at', startOfMonth.toISOString());

    if ((count ?? 0) >= 10) {
      return NextResponse.json({ error: 'Monthly limit reached (10/10)', redirect: '/settings#plans' }, { status: 403 });
    }
  }

  const body = await req.json();
  const {
    club_name, formation, style, positions, style_profiles,
    age_min, age_max, height_min, budget_eur, target_leagues,
  } = body;

  // Save club profile
  const { data: clubProfile, error: cpError } = await supabase
    .from('club_profiles')
    .insert({
      user_id: user.id,
      club_name,
      formation,
      style,
      positions,
      style_profiles,
      age_min,
      age_max,
      height_min,
      budget_eur,
      target_leagues,
    })
    .select()
    .single();

  if (cpError) return NextResponse.json({ error: cpError.message }, { status: 500 });

  // Fetch matching players from DB
  let query = supabase
    .from('players')
    .select(`
      *,
      player_style_profiles(*),
      player_injuries(*)
    `)
    .limit(200);

  if (positions?.length) query = query.in('position', positions);
  if (age_min) query = query.gte('age', age_min);
  if (age_max) query = query.lte('age', age_max);
  if (height_min) query = query.gte('height_cm', height_min);
  if (target_leagues?.length) query = query.in('league', target_leagues);

  const { data: players } = await query;

  if (!players?.length) {
    // Return empty longlist
    const { data: longlist } = await supabase
      .from('longlists')
      .insert({ user_id: user.id, club_profile_id: clubProfile.id, player_ids: [] })
      .select()
      .single();

    return NextResponse.json({ id: longlist!.id, players: [] });
  }

  // Generate with Claude
  const results = await generateLonglist(clubProfile, players, profile.preferred_language);

  // Save longlist
  const { data: longlist } = await supabase
    .from('longlists')
    .insert({
      user_id: user.id,
      club_profile_id: clubProfile.id,
      player_ids: results,
    })
    .select()
    .single();

  // Decrement trial uses + send low-use email
  if (profile.plan === 'trial') {
    const newRemaining = profile.trial_uses_remaining - 1;
    await supabase
      .from('users')
      .update({ trial_uses_remaining: newRemaining })
      .eq('id', user.id);

    if (newRemaining <= 2 && user.email) {
      sendTrialLowEmail(user.email, newRemaining).catch(() => {});
    }
  }

  return NextResponse.json({ id: longlist!.id });
}
