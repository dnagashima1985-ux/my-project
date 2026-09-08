import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@/lib/supabase/server';
import { searchPlayerByName } from '@/lib/api-football/client';
import { addPlayerByName } from '@/lib/ingest/ingest-players';

// GET /api/players/search?q=ishiwatari  — search without saving
export async function GET(req: NextRequest) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

  const q = req.nextUrl.searchParams.get('q');
  if (!q || q.length < 2) return NextResponse.json({ results: [] });

  const season = new Date().getMonth() < 6 ? new Date().getFullYear() - 1 : new Date().getFullYear();
  const results = await searchPlayerByName(q, season);

  return NextResponse.json({
    results: results.map((p) => ({
      api_football_id: p.api_football_id,
      name: p.name,
      age: p.age,
      nationality: p.nationality,
      current_club: p.current_club,
      league: p.league,
      position: p.position,
      appearances: p.stats.appearances,
      goals: p.stats.goals,
      assists: p.stats.assists,
    })),
  });
}

// POST /api/players/search  — save the player to DB
export async function POST(req: NextRequest) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

  const { name } = await req.json();
  if (!name) return NextResponse.json({ error: 'name required' }, { status: 400 });

  const id = await addPlayerByName(name);
  if (!id) return NextResponse.json({ error: 'Player not found' }, { status: 404 });

  return NextResponse.json({ id });
}
