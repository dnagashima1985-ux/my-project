import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@/lib/supabase/server';

export async function POST(req: NextRequest) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

  const contentType = req.headers.get('content-type') ?? '';
  let player_id: string | null = null;

  if (contentType.includes('application/json')) {
    const body = await req.json();
    player_id = body.player_id;
  } else {
    const form = await req.formData();
    player_id = form.get('player_id') as string;
  }

  if (!player_id) return NextResponse.json({ error: 'player_id required' }, { status: 400 });

  // Upsert to avoid duplicates
  await supabase
    .from('shortlists')
    .upsert({ user_id: user.id, player_id }, { onConflict: 'user_id,player_id' });

  const referer = req.headers.get('referer') ?? '/shortlist';
  return NextResponse.redirect(referer, { status: 303 });
}
