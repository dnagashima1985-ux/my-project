import { NextRequest, NextResponse } from 'next/server';
import { runMarketIntelligence } from '@/lib/ingest/ingest-market-intelligence';

// Vercel Cron: runs at 6am UTC daily
export async function GET(req: NextRequest) {
  const auth = req.headers.get('authorization');
  if (auth !== `Bearer ${process.env.CRON_SECRET}`) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const signals = await runMarketIntelligence();
  return NextResponse.json({ ok: true, signals_stored: signals });
}
