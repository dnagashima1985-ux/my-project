import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@/lib/supabase/server';

export async function POST(req: NextRequest) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

  const form = await req.formData();
  const language = form.get('language') as string;

  const valid = ['en', 'ja', 'nl', 'fr', 'es'];
  if (!valid.includes(language)) {
    return NextResponse.json({ error: 'Invalid language' }, { status: 400 });
  }

  await supabase.from('users').update({ preferred_language: language }).eq('id', user.id);

  return NextResponse.redirect(
    new URL('/settings', process.env.NEXT_PUBLIC_APP_URL ?? 'http://localhost:3000'),
    { status: 303 }
  );
}
