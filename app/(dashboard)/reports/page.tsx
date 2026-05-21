import { createClient } from '@/lib/supabase/server';
import Link from 'next/link';
import { ChevronRight, FileText, Lock } from 'lucide-react';

export default async function ReportsPage() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();

  const { data: profile } = await supabase
    .from('users')
    .select('plan')
    .eq('id', user!.id)
    .single();

  const isPro = profile?.plan === 'pro' || profile?.plan === 'elite';

  const { data: reports } = await supabase
    .from('reports')
    .select('id, created_at, audience, language, players(name, position)')
    .eq('user_id', user!.id)
    .order('created_at', { ascending: false });

  if (!isPro) {
    return (
      <div className="max-w-xl mx-auto text-center py-20">
        <Lock size={40} className="mx-auto text-gray-600 mb-4" />
        <h1 className="text-xl font-bold text-white mb-2">Report builder</h1>
        <p className="text-gray-400 mb-6">
          Generate professional CEO, Sports Director, and Coach reports.<br />
          Available on Pro and Elite plans.
        </p>
        <Link
          href="/settings#plans"
          className="bg-emerald-500 hover:bg-emerald-400 text-white font-semibold px-6 py-3 rounded-lg transition-colors"
        >
          Upgrade to Pro →
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-white">Reports</h1>
        <Link
          href="/reports/new"
          className="flex items-center gap-2 bg-emerald-500 hover:bg-emerald-400 text-white font-semibold px-4 py-2 rounded-lg text-sm transition-colors"
        >
          <FileText size={16} />
          New report
        </Link>
      </div>

      {!reports?.length ? (
        <div className="text-center py-20 text-gray-600">
          <div className="text-5xl mb-4">📄</div>
          <p className="text-gray-400 text-lg font-medium mb-2">No reports yet</p>
          <p className="text-sm mb-6">Generate CEO, Sports Director, or Coach reports for your target players</p>
          <Link href="/reports/new" className="text-emerald-400 hover:text-emerald-300">
            Generate first report →
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {reports.map((r: ReportRow) => {
            const p = r.players as PlayerRef | null;
            const audienceLabel = r.audience === 'ceo' ? 'CEO / Owner' : r.audience === 'sd' ? 'Sports Director' : 'Coach';
            const langLabel = r.language === 'ja' ? '🇯🇵 JA' : r.language === 'nl' ? '🇳🇱 NL' : r.language === 'fr' ? '🇫🇷 FR' : '🇬🇧 EN';

            return (
              <Link
                key={r.id}
                href={`/reports/${r.id}`}
                className="flex items-center justify-between bg-gray-900 border border-gray-800 hover:border-gray-700 rounded-xl px-5 py-4 transition-colors"
              >
                <div className="flex items-center gap-4">
                  <FileText size={20} className="text-gray-600 shrink-0" />
                  <div>
                    <div className="font-semibold text-white">
                      {p?.name ?? 'Unknown player'} — {audienceLabel}
                    </div>
                    <div className="text-xs text-gray-500 mt-0.5">
                      {p?.position} · {langLabel} · {new Date(r.created_at).toLocaleDateString()}
                    </div>
                  </div>
                </div>
                <ChevronRight size={18} className="text-gray-600" />
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}

interface ReportRow {
  id: string;
  created_at: string;
  audience: string;
  language: string;
  players: unknown;
}

interface PlayerRef {
  name: string;
  position: string;
}
