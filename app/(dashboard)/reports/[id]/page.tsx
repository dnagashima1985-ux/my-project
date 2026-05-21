import { createClient } from '@/lib/supabase/server';
import { notFound } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Download } from 'lucide-react';

interface PageProps {
  params: Promise<{ id: string }>;
}

export default async function ReportDetailPage({ params }: PageProps) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();

  const { data: report } = await supabase
    .from('reports')
    .select('*, players(name, position, current_club, league, age)')
    .eq('id', id)
    .eq('user_id', user!.id)
    .single();

  if (!report) notFound();

  const player = report.players as PlayerRef | null;
  const content = report.ai_content as Record<string, string> | null;
  const audienceLabel = report.audience === 'ceo' ? 'CEO / Owner' : report.audience === 'sd' ? 'Sports Director' : 'Coach';

  return (
    <div className="max-w-3xl mx-auto">
      <div className="flex items-center gap-3 mb-6">
        <Link href="/reports" className="text-gray-400 hover:text-white transition-colors">
          <ArrowLeft size={20} />
        </Link>
        <div className="flex-1">
          <h1 className="text-xl font-bold text-white">
            {player?.name} — {audienceLabel} Report
          </h1>
          <p className="text-sm text-gray-500">
            {player?.position} · {player?.current_club} ·{' '}
            {report.language === 'ja' ? 'Japanese' : report.language === 'nl' ? 'Dutch' : report.language === 'fr' ? 'French' : 'English'} ·{' '}
            {new Date(report.created_at).toLocaleDateString()}
          </p>
        </div>
        <a
          href={`/api/reports/${id}/download?format=pdf`}
          className="flex items-center gap-2 bg-gray-800 hover:bg-gray-700 text-gray-300 font-medium px-4 py-2 rounded-lg text-sm transition-colors"
        >
          <Download size={14} />
          PDF
        </a>
        <a
          href={`/api/reports/${id}/download?format=ppt`}
          className="flex items-center gap-2 bg-gray-800 hover:bg-gray-700 text-gray-300 font-medium px-4 py-2 rounded-lg text-sm transition-colors"
        >
          <Download size={14} />
          PPT
        </a>
      </div>

      {content ? (
        <div className="space-y-4">
          {Object.entries(content).map(([key, value]) => (
            <div key={key} className="bg-gray-900 border border-gray-800 rounded-xl p-5">
              <h2 className="font-semibold text-emerald-400 mb-3 capitalize">
                {key.replace(/_/g, ' ')}
              </h2>
              <div className="text-gray-300 text-sm leading-relaxed whitespace-pre-wrap">{value}</div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-20 text-gray-600">
          <p>Report content not available</p>
        </div>
      )}

      <div className="mt-6 bg-gray-900 border border-gray-800 rounded-xl p-4 text-xs text-gray-600">
        ⓘ AI-generated content uses only provided data. Financial figures are not invented by the AI.
      </div>
    </div>
  );
}

interface PlayerRef {
  name: string;
  position: string;
  current_club: string;
  league: string;
  age: number;
}
