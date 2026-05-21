import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@/lib/supabase/server';
import { generatePDF } from '@/lib/export/pdf';
import { generatePPT } from '@/lib/export/ppt';

export async function GET(
  req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const format = req.nextUrl.searchParams.get('format') ?? 'pdf';

  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

  const { data: report } = await supabase
    .from('reports')
    .select('*, players(name, position, current_club, league, age, nationality, height_cm)')
    .eq('id', id)
    .eq('user_id', user.id)
    .single();

  if (!report) return NextResponse.json({ error: 'Not found' }, { status: 404 });

  const player = report.players as Record<string, unknown>;
  const content = (report.ai_content ?? {}) as Record<string, string>;
  const audienceLabel = report.audience === 'ceo' ? 'CEO / Owner'
    : report.audience === 'sd' ? 'Sports Director'
    : 'Coach';

  if (format === 'ppt') {
    const buf = await generatePPT({ player, content, audienceLabel, language: report.language });
    return new NextResponse(buf as unknown as BodyInit, {
      headers: {
        'Content-Type': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'Content-Disposition': `attachment; filename="ScoutIQ_${(player.name as string).replace(/\s/g, '_')}_${report.audience}.pptx"`,
      },
    });
  }

  const buf = await generatePDF({ player, content, audienceLabel, language: report.language });
  return new NextResponse(buf as unknown as BodyInit, {
    headers: {
      'Content-Type': 'application/pdf',
      'Content-Disposition': `attachment; filename="ScoutIQ_${(player.name as string).replace(/\s/g, '_')}_${report.audience}.pdf"`,
    },
  });
}
