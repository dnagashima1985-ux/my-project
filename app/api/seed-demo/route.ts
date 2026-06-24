import { NextResponse } from 'next/server';
import { seedDemo } from '@/lib/ingest/seed-demo';

export async function POST() {
  await seedDemo();
  return NextResponse.json({ ok: true });
}
