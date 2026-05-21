import { createClient } from '@/lib/supabase/server';
import { notFound } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Bookmark, FileText } from 'lucide-react';
import PlayerCard from '@/components/players/PlayerCard';

interface PageProps {
  params: Promise<{ id: string }>;
}

export default async function LonglistDetailPage({ params }: PageProps) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();

  const { data: longlist } = await supabase
    .from('longlists')
    .select('*, club_profiles(*)')
    .eq('id', id)
    .eq('user_id', user!.id)
    .single();

  if (!longlist) notFound();

  const entries = (longlist.player_ids as LonglistEntry[] | null) ?? [];
  const playerIds = entries.map((e) => e.player_id);

  const { data: players } = await supabase
    .from('players')
    .select(`
      *,
      player_style_profiles(*),
      player_injuries(risk_score, risk_grade, status)
    `)
    .in('id', playerIds);

  // Sort by fit_score from the longlist
  const playerMap = new Map((players ?? []).map((p) => [p.id, p]));
  const sorted = entries
    .map((e) => ({ ...playerMap.get(e.player_id), fit_score: e.fit_score, reasoning: e.reasoning }))
    .filter((p) => p.id);

  const cp = longlist.club_profiles as ClubProfile;

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center gap-3 mb-6">
        <Link href="/longlist" className="text-gray-400 hover:text-white transition-colors">
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="text-xl font-bold text-white">{cp?.club_name ?? 'Longlist'}</h1>
          <p className="text-sm text-gray-500">
            {sorted.length} players · Generated {new Date(longlist.generated_at).toLocaleDateString()}
          </p>
        </div>
      </div>

      {cp && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 mb-6 flex flex-wrap gap-4 text-sm">
          {cp.formation && <span className="text-gray-400">Formation: <span className="text-white">{cp.formation}</span></span>}
          {cp.style && <span className="text-gray-400">Style: <span className="text-white">{cp.style}</span></span>}
          {cp.positions?.length && <span className="text-gray-400">Positions: <span className="text-white">{cp.positions.join(', ')}</span></span>}
          {cp.age_min && cp.age_max && (
            <span className="text-gray-400">Age: <span className="text-white">{cp.age_min}–{cp.age_max}</span></span>
          )}
        </div>
      )}

      {!sorted.length ? (
        <div className="text-center py-16 text-gray-600">
          <div className="text-4xl mb-3">🔍</div>
          <p className="text-gray-400">No players found matching these criteria.</p>
          <p className="text-sm mt-2">Try broadening your search filters.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {sorted.map((player, i) => (
            <div key={player.id} className="bg-gray-900 border border-gray-800 rounded-xl p-5">
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-start gap-4 flex-1">
                  <div className="text-2xl font-black text-gray-700 w-8 shrink-0">
                    {i + 1}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-3 flex-wrap">
                      <Link
                        href={`/players/${player.id}`}
                        className="text-lg font-bold text-white hover:text-emerald-400 transition-colors"
                      >
                        {player.name}
                      </Link>
                      <span className="bg-emerald-500/10 text-emerald-400 text-xs font-bold px-2 py-0.5 rounded-full">
                        {player.fit_score}% fit
                      </span>
                      {player.player_injuries?.[0] && (
                        <InjuryBadge grade={player.player_injuries[0].risk_grade} status={player.player_injuries[0].status} />
                      )}
                      {player.player_style_profiles?.[0] && (
                        <span className="bg-gray-800 text-gray-400 text-xs px-2 py-0.5 rounded-full">
                          {player.player_style_profiles[0].primary_profile_id}
                        </span>
                      )}
                    </div>
                    <div className="text-sm text-gray-500 mt-1">
                      {player.position} · {player.current_club} · {player.league}
                      {player.age && ` · Age ${player.age}`}
                      {player.nationality && ` · ${player.nationality}`}
                    </div>
                    {player.reasoning && (
                      <p className="text-sm text-gray-400 mt-2 leading-relaxed">{player.reasoning}</p>
                    )}
                    {player.stats && (
                      <div className="flex flex-wrap gap-4 mt-3">
                        <StatChip label="Goals" value={player.stats.goals ?? 0} />
                        <StatChip label="Assists" value={player.stats.assists ?? 0} />
                        <StatChip label="xG" value={Number(player.stats.xg ?? 0).toFixed(1)} />
                        <StatChip label="xA" value={Number(player.stats.xa ?? 0).toFixed(1)} />
                        <StatChip label="Pass %" value={`${player.stats.pass_accuracy ?? 0}%`} />
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex flex-col gap-2 shrink-0">
                  <ShortlistButton playerId={player.id} />
                  <Link
                    href={`/reports/new?player=${player.id}`}
                    className="flex items-center gap-1.5 text-xs bg-gray-800 hover:bg-gray-700 text-gray-300 px-3 py-1.5 rounded-lg transition-colors"
                  >
                    <FileText size={12} />
                    Report
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function StatChip({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="text-xs">
      <span className="text-gray-600">{label}: </span>
      <span className="text-gray-300 font-medium">{value}</span>
    </div>
  );
}

function InjuryBadge({ grade, status }: { grade: string; status: string }) {
  const colors: Record<string, string> = {
    LOW: 'bg-emerald-500/10 text-emerald-400',
    MEDIUM: 'bg-yellow-500/10 text-yellow-400',
    HIGH: 'bg-orange-500/10 text-orange-400',
    CRITICAL: 'bg-red-500/10 text-red-400',
  };
  const dot: Record<string, string> = {
    available: 'bg-emerald-400',
    doubtful: 'bg-yellow-400',
    injured: 'bg-red-400',
  };

  return (
    <span className={`flex items-center gap-1 text-xs px-2 py-0.5 rounded-full ${colors[grade] ?? 'text-gray-400'}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${dot[status] ?? 'bg-gray-400'}`} />
      {grade}
    </span>
  );
}

function ShortlistButton({ playerId }: { playerId: string }) {
  return (
    <form action={`/api/shortlist/add`} method="post">
      <input type="hidden" name="player_id" value={playerId} />
      <button
        type="submit"
        className="flex items-center gap-1.5 text-xs bg-gray-800 hover:bg-emerald-500/20 hover:text-emerald-400 text-gray-300 px-3 py-1.5 rounded-lg transition-colors"
      >
        <Bookmark size={12} />
        Shortlist
      </button>
    </form>
  );
}

interface LonglistEntry {
  player_id: string;
  fit_score: number;
  reasoning?: string;
}

interface ClubProfile {
  club_name: string;
  formation?: string;
  style?: string;
  positions?: string[];
  age_min?: number;
  age_max?: number;
}
