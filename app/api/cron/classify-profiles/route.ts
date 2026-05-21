import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';
import { classifyProfile } from '@/lib/classify-profile';

export async function GET(req: NextRequest) {
  const auth = req.headers.get('authorization');
  if (auth !== `Bearer ${process.env.CRON_SECRET}`) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!
  );

  const { data: players } = await supabase
    .from('players')
    .select('id, position, stats')
    .limit(2000);

  if (!players) return NextResponse.json({ ok: true, count: 0 });

  let done = 0;
  for (const player of players) {
    if (!player.stats || !player.position) continue;

    try {
      const c = classifyProfile({ position: player.position, stats: player.stats });

      await supabase.from('player_style_profiles').upsert({
        player_id: player.id,
        primary_profile_id: c.primary,
        secondary_profile_id: c.secondary ?? null,
        profile_scores: c.scores,
        confidence_level: c.confidence,
        data_caveats: c.caveats,
        last_updated_at: new Date().toISOString(),
      }, { onConflict: 'player_id' });

      done++;
    } catch {
      // continue
    }
  }

  return NextResponse.json({ ok: true, count: done });
}
