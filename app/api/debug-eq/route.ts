import { createClient } from '@supabase/supabase-js';
import { NextResponse } from 'next/server';

export async function GET() {
  const supabase = createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!
  );

  const { data: eq, error: eqErr } = await supabase.from('eq_analyses').select('*');
  const { data: players, error: pErr } = await supabase.from('players').select('id, name, source_id');

  return NextResponse.json({
    eq_count: eq?.length ?? 0,
    eq_rows: eq ?? [],
    eq_error: eqErr?.message ?? null,
    players: players ?? [],
    players_error: pErr?.message ?? null,
    service_key_set: !!process.env.SUPABASE_SERVICE_ROLE_KEY,
  });
}
