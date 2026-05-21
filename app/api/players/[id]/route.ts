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

  const { data: player } = await supabase
    .from('players')
    .select('id, name, position, current_club, league, age')
    .eq('id', id)
    .single();

  if (!player) return NextResponse.json({ error: 'Not found' }, { status: 404 });
  return NextResponse.json(player);
}
