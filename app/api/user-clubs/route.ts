import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@/lib/supabase/server';

export async function GET() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

  const { data: clubs } = await supabase
    .from('user_clubs')
    .select('*')
    .eq('user_id', user.id)
    .order('club_name');

  return NextResponse.json({ clubs: clubs ?? [] });
}

export async function POST(req: NextRequest) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

  // Check plan
  const { data: profile } = await supabase
    .from('users')
    .select('plan')
    .eq('id', user.id)
    .single();

  if (profile?.plan !== 'elite') {
    return NextResponse.json({ error: 'Elite plan required' }, { status: 403 });
  }

  // Check limit (max 3)
  const { count } = await supabase
    .from('user_clubs')
    .select('id', { count: 'exact', head: true })
    .eq('user_id', user.id);

  if ((count ?? 0) >= 3) {
    return NextResponse.json({ error: 'Maximum 3 clubs on Elite plan' }, { status: 400 });
  }

  const body = await req.json();
  const { club_name, league, tier, budget_range, style, country } = body;

  const { data: club, error } = await supabase
    .from('user_clubs')
    .insert({ user_id: user.id, club_name, league, tier, budget_range, style, country })
    .select()
    .single();

  if (error) return NextResponse.json({ error: error.message }, { status: 500 });
  return NextResponse.json({ club });
}
