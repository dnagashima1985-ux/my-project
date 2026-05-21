import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@/lib/supabase/server';
import { ingestEQForPlayer } from '@/lib/ingest/ingest-eq';

export async function POST(
  _req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

  const { data: player } = await supabase
    .from('players')
    .select('name')
    .eq('id', id)
    .single();

  if (!player) return NextResponse.json({ error: 'Player not found' }, { status: 404 });

  await ingestEQForPlayer(id, player.name);

  return NextResponse.json({ ok: true });
}
