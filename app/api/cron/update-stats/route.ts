import { NextRequest, NextResponse } from 'next/server';
import { ingestPlayers } from '@/lib/ingest/ingest-players';

// Vercel Cron: runs at 3am UTC daily
// vercel.json: { "crons": [{ "path": "/api/cron/update-stats", "schedule": "0 3 * * *" }] }
export async function GET(req: NextRequest) {
  const auth = req.headers.get('authorization');
  if (auth !== `Bearer ${process.env.CRON_SECRET}`) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const count = await ingestPlayers();
  return NextResponse.json({ ok: true, players_updated: count });
}
