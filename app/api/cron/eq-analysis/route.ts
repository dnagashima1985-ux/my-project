import { NextRequest, NextResponse } from 'next/server';
import { ingestEQBatch } from '@/lib/ingest/ingest-eq';

// Vercel Cron: runs at 4am UTC daily
export async function GET(req: NextRequest) {
  const auth = req.headers.get('authorization');
  if (auth !== `Bearer ${process.env.CRON_SECRET}`) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const count = await ingestEQBatch(50);
  return NextResponse.json({ ok: true, players_analyzed: count });
}
