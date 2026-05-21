import { createClient } from '@/lib/supabase/server';
import Link from 'next/link';
import { Plus, ChevronRight } from 'lucide-react';

export default async function DashboardPage() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();

  const [{ data: longlists }, { data: shortlists }, { data: reports }] = await Promise.all([
    supabase
      .from('longlists')
      .select('id, generated_at, club_profiles(club_name)')
      .eq('user_id', user!.id)
      .order('generated_at', { ascending: false })
      .limit(5),
    supabase
      .from('shortlists')
      .select('id, added_at, players(name, position, current_club)')
      .eq('user_id', user!.id)
      .order('added_at', { ascending: false })
      .limit(5),
    supabase
      .from('reports')
      .select('id, created_at, audience, language, players(name)')
      .eq('user_id', user!.id)
      .order('created_at', { ascending: false })
      .limit(5),
  ]);

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">Dashboard</h1>
        <Link
          href="/longlist/new"
          className="flex items-center gap-2 bg-emerald-500 hover:bg-emerald-400 text-white font-semibold px-4 py-2 rounded-lg text-sm transition-colors"
        >
          <Plus size={16} />
          New longlist
        </Link>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-3 gap-4">
        <StatCard label="Longlists generated" value={longlists?.length ?? 0} />
        <StatCard label="Shortlisted players" value={shortlists?.length ?? 0} />
        <StatCard label="Reports created" value={reports?.length ?? 0} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent longlists */}
        <section className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-white">Recent longlists</h2>
            <Link href="/longlist" className="text-xs text-emerald-400 hover:text-emerald-300 flex items-center gap-1">
              View all <ChevronRight size={12} />
            </Link>
          </div>
          {!longlists?.length ? (
            <EmptyState
              message="No longlists yet"
              cta="Generate your first longlist"
              href="/longlist/new"
            />
          ) : (
            <ul className="space-y-2">
              {(longlists as unknown as LonglistRow[]).map((l) => (
                <li key={l.id}>
                  <Link
                    href={`/longlist/${l.id}`}
                    className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-800 transition-colors"
                  >
                    <div>
                      <div className="text-sm font-medium text-white">
                        {(Array.isArray(l.club_profiles) ? l.club_profiles[0] : l.club_profiles)?.club_name ?? 'Unnamed club'}
                      </div>
                      <div className="text-xs text-gray-500">
                        {new Date(l.generated_at).toLocaleDateString()}
                      </div>
                    </div>
                    <ChevronRight size={14} className="text-gray-600" />
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </section>

        {/* Shortlisted players */}
        <section className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-white">Shortlisted players</h2>
            <Link href="/shortlist" className="text-xs text-emerald-400 hover:text-emerald-300 flex items-center gap-1">
              View all <ChevronRight size={12} />
            </Link>
          </div>
          {!shortlists?.length ? (
            <EmptyState message="No players shortlisted yet" />
          ) : (
            <ul className="space-y-2">
              {(shortlists as unknown as ShortlistRow[]).map((s) => (
                <li key={s.id}>
                  <Link
                    href={`/players/${(Array.isArray(s.players) ? s.players[0] : s.players as PlayerRef | null)?.id ?? ''}`}
                    className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-800 transition-colors"
                  >
                    <div>
                      <div className="text-sm font-medium text-white">
                        {(Array.isArray(s.players) ? s.players[0] : s.players as PlayerRef | null)?.name ?? '—'}
                      </div>
                      <div className="text-xs text-gray-500">
                        {(Array.isArray(s.players) ? s.players[0] : s.players as PlayerRef | null)?.position} · {(Array.isArray(s.players) ? s.players[0] : s.players as PlayerRef | null)?.current_club}
                      </div>
                    </div>
                    <ChevronRight size={14} className="text-gray-600" />
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <div className="text-3xl font-black text-emerald-400">{value}</div>
      <div className="text-sm text-gray-400 mt-1">{label}</div>
    </div>
  );
}

function EmptyState({ message, cta, href }: { message: string; cta?: string; href?: string }) {
  return (
    <div className="text-center py-8 text-gray-600">
      <p className="text-sm mb-2">{message}</p>
      {cta && href && (
        <Link href={href} className="text-sm text-emerald-400 hover:text-emerald-300">
          {cta} →
        </Link>
      )}
    </div>
  );
}

interface LonglistRow {
  id: string;
  generated_at: string;
  club_profiles: { club_name: string } | { club_name: string }[] | null;
}

interface PlayerRef {
  id: string;
  name: string;
  position: string;
  current_club: string;
}

interface ShortlistRow {
  id: string;
  added_at: string;
  players: PlayerRef | PlayerRef[] | null;
}
