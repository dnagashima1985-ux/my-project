import { createClient } from '@/lib/supabase/server';
import Link from 'next/link';
import { Search } from 'lucide-react';

interface PageProps {
  searchParams: Promise<{ q?: string; position?: string; league?: string }>;
}

export default async function PlayersPage({ searchParams }: PageProps) {
  const { q, position, league } = await searchParams;
  const supabase = await createClient();

  let query = supabase
    .from('players')
    .select(`
      id, name, age, nationality, position, current_club, league,
      stats,
      player_style_profiles(primary_profile_id, confidence_level),
      player_injuries(risk_grade, status)
    `)
    .limit(50);

  if (q) query = query.ilike('name', `%${q}%`);
  if (position) query = query.eq('position', position);
  if (league) query = query.eq('league', league);

  const { data: players } = await query;

  return (
    <div className="max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold text-white mb-6">Players</h1>

      {/* Search & filters */}
      <form className="flex gap-3 mb-6">
        <div className="relative flex-1">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
          <input
            name="q"
            defaultValue={q}
            placeholder="Search by name..."
            className="w-full bg-gray-900 border border-gray-800 rounded-lg pl-9 pr-4 py-2.5 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-emerald-500"
          />
        </div>
        <select
          name="position"
          defaultValue={position}
          className="bg-gray-900 border border-gray-800 rounded-lg px-3 py-2.5 text-sm text-gray-300 focus:outline-none focus:border-emerald-500"
        >
          <option value="">All positions</option>
          {['GK','CB','LB','RB','CDM','CM','CAM','LW','RW','ST','CF'].map((p) => (
            <option key={p} value={p}>{p}</option>
          ))}
        </select>
        <button
          type="submit"
          className="bg-emerald-500 hover:bg-emerald-400 text-white font-medium px-4 py-2.5 rounded-lg text-sm transition-colors"
        >
          Search
        </button>
      </form>

      {!players?.length ? (
        <div className="text-center py-20 text-gray-600">
          <div className="text-4xl mb-3">👤</div>
          <p className="text-gray-400">No players found</p>
          {q && <p className="text-sm mt-1">Try a different search term</p>}
        </div>
      ) : (
        <>
          <p className="text-sm text-gray-600 mb-4">{players.length} players</p>
          <div className="space-y-2">
            {players.map((p: PlayerRow) => {
              const profile = p.player_style_profiles?.[0];
              const injury = p.player_injuries?.[0];
              return (
                <Link
                  key={p.id}
                  href={`/players/${p.id}`}
                  className="flex items-center justify-between bg-gray-900 border border-gray-800 hover:border-gray-700 rounded-xl px-5 py-4 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-8 h-8 bg-gray-800 rounded-full flex items-center justify-center text-xs font-bold text-gray-400">
                      {p.position?.slice(0, 2)}
                    </div>
                    <div>
                      <div className="font-semibold text-white">{p.name}</div>
                      <div className="text-xs text-gray-500 mt-0.5">
                        {p.current_club} · {p.league} {p.age && `· Age ${p.age}`} {p.nationality && `· ${p.nationality}`}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
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
                    {p.stats && (
                      <div className="text-xs text-gray-600 hidden md:flex gap-3">
                        <span>G: {p.stats.goals ?? 0}</span>
                        <span>A: {p.stats.assists ?? 0}</span>
                        <span>xG: {Number(p.stats.xg ?? 0).toFixed(1)}</span>
                      </div>
                    )}
                  </div>
                </Link>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}

interface PlayerRow {
  id: string;
  name: string;
  age: number;
  nationality: string;
  position: string;
  current_club: string;
  league: string;
  stats: { goals?: number; assists?: number; xg?: number };
  player_style_profiles: { primary_profile_id: string; confidence_level: string }[];
  player_injuries: { risk_grade: string; status: string }[];
}
