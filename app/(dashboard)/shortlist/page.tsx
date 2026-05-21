import { createClient } from '@/lib/supabase/server';
import Link from 'next/link';
import { FileText } from 'lucide-react';
import RemoveShortlistButton from '@/components/players/RemoveShortlistButton';

export default async function ShortlistPage() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();

  const { data: shortlist } = await supabase
    .from('shortlists')
    .select(`
      id, note, added_at,
      players(id, name, age, position, current_club, league, stats,
        player_style_profiles(primary_profile_id),
        player_injuries(risk_grade, status)
      )
    `)
    .eq('user_id', user!.id)
    .order('added_at', { ascending: false });

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-white">Shortlist</h1>
        <span className="text-sm text-gray-500">{shortlist?.length ?? 0} players</span>
      </div>

      {!shortlist?.length ? (
        <div className="text-center py-20 text-gray-600">
          <div className="text-5xl mb-4">🔖</div>
          <p className="text-gray-400 text-lg font-medium mb-2">No players shortlisted</p>
          <p className="text-sm mb-6">Add players to your shortlist from longlists or player profiles</p>
          <Link href="/longlist/new" className="text-emerald-400 hover:text-emerald-300">
            Generate a longlist →
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {shortlist.map((s: ShortlistRow) => {
            const p = s.players as PlayerRow | null;
            if (!p) return null;
            const profile = p.player_style_profiles?.[0];
            const injury = p.player_injuries?.[0];
            const stats = p.stats ?? {};

            return (
              <div key={s.id} className="bg-gray-900 border border-gray-800 rounded-xl p-5">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 flex-wrap">
                      <Link
                        href={`/players/${p.id}`}
                        className="font-bold text-white hover:text-emerald-400 transition-colors"
                      >
                        {p.name}
                      </Link>
                      {profile && (
                        <span className="text-xs bg-gray-800 text-gray-400 px-2 py-0.5 rounded-full">
                          {profile.primary_profile_id}
                        </span>
                      )}
                      {injury && (
                        <span className={`text-xs px-2 py-0.5 rounded-full ${
                          injury.risk_grade === 'LOW' ? 'bg-emerald-500/10 text-emerald-400' :
                          injury.risk_grade === 'MEDIUM' ? 'bg-yellow-500/10 text-yellow-400' :
                          injury.risk_grade === 'HIGH' ? 'bg-orange-500/10 text-orange-400' :
                          'bg-red-500/10 text-red-400'
                        }`}>
                          {injury.risk_grade}
                        </span>
                      )}
                    </div>
                    <div className="text-sm text-gray-500 mt-0.5">
                      {p.position} · {p.current_club} · {p.league}{p.age ? ` · Age ${p.age}` : ''}
                    </div>
                    {stats.goals !== undefined && (
                      <div className="flex gap-4 mt-2 text-xs text-gray-600">
                        <span>G: {stats.goals}</span>
                        <span>A: {stats.assists ?? 0}</span>
                        <span>xG: {Number(stats.xg ?? 0).toFixed(1)}</span>
                        <span>xA: {Number(stats.xa ?? 0).toFixed(1)}</span>
                      </div>
                    )}
                    {s.note && <p className="text-sm text-gray-500 mt-2 italic">{s.note}</p>}
                    <p className="text-xs text-gray-700 mt-1">
                      Added {new Date(s.added_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="flex flex-col gap-2 shrink-0">
                    <Link
                      href={`/reports/new?player=${p.id}`}
                      className="flex items-center gap-1.5 text-xs bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 px-3 py-1.5 rounded-lg transition-colors"
                    >
                      <FileText size={12} />
                      Report
                    </Link>
                    <RemoveShortlistButton shortlistId={s.id} />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

interface ShortlistRow {
  id: string;
  note: string;
  added_at: string;
  players: unknown;
}

interface PlayerRow {
  id: string;
  name: string;
  age: number;
  position: string;
  current_club: string;
  league: string;
  stats: Record<string, number>;
  player_style_profiles: { primary_profile_id: string }[];
  player_injuries: { risk_grade: string; status: string }[];
}
