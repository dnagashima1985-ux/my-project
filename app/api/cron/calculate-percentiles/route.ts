import { NextRequest, NextResponse } from 'next/server';
import { calculatePercentilesForAll } from '@/lib/percentiles/calculate';

export async function GET(req: NextRequest) {
  const auth = req.headers.get('authorization');
  if (auth !== `Bearer ${process.env.CRON_SECRET}`) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const count = await calculatePercentilesForAll(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!
  );

  return NextResponse.json({ ok: true, players_updated: count });
}
