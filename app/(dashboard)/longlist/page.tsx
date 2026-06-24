import { createClient } from '@/lib/supabase/server';
import Link from 'next/link';
import { Plus, ChevronRight } from 'lucide-react';
import DeleteLonglistButton from '@/components/longlist/DeleteLonglistButton';

export default async function LonglistPage() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();

  const { data: longlists } = await supabase
    .from('longlists')
    .select('id, generated_at, player_ids, club_profiles(club_name, positions, style)')
    .eq('user_id', user!.id)
    .order('generated_at', { ascending: false });

  return (
    <div className="max-w-3xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-white">Longlists</h1>
        <Link
          href="/longlist/new"
          className="flex items-center gap-2 bg-emerald-500 hover:bg-emerald-400 text-white font-semibold px-4 py-2 rounded-lg text-sm transition-colors"
        >
          <Plus size={16} />
          New longlist
        </Link>
      </div>

      {!longlists?.length ? (
        <div className="text-center py-20 text-gray-600">
          <div className="text-5xl mb-4">📋</div>
          <p className="text-lg font-medium text-gray-400 mb-2">No longlists yet</p>
          <p className="text-sm mb-6">Create your first longlist to find players matching your club&apos;s needs</p>
          <Link
            href="/longlist/new"
            className="bg-emerald-500 hover:bg-emerald-400 text-white font-semibold px-6 py-3 rounded-lg transition-colors"
          >
            Generate first longlist →
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {longlists.map((l: LonglistItem) => {
            const cp = l.club_profiles as ClubProfileRef | null;
            const count = Array.isArray(l.player_ids) ? l.player_ids.length : 0;
            return (
              <div key={l.id} className="flex items-center bg-gray-900 border border-gray-800 hover:border-gray-700 rounded-xl p-5 transition-colors">
                <Link href={`/longlist/${l.id}`} className="flex items-center justify-between flex-1">
                  <div>
                    <div className="font-semibold text-white">{cp?.club_name ?? 'Unnamed club'}</div>
                    <div className="text-sm text-gray-500 mt-0.5">
                      {cp?.style && <span className="mr-3">{cp.style}</span>}
                      <span>{count} player{count !== 1 ? 's' : ''}</span>
                      <span className="mx-2">·</span>
                      <span>{new Date(l.generated_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                  <ChevronRight size={18} className="text-gray-600" />
                </Link>
                <DeleteLonglistButton id={l.id} />
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

interface LonglistItem {
  id: string;
  generated_at: string;
  player_ids: unknown;
  club_profiles: unknown;
}

interface ClubProfileRef {
  club_name: string;
  positions: string[];
  style: string;
}
