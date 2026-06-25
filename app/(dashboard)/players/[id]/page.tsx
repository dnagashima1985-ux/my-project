import { createClient } from '@/lib/supabase/server';
import { notFound } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Bookmark, FileText } from 'lucide-react';
import PercentileGrid from '@/components/players/PercentileGrid';
import TriggerEQButton from '@/components/players/TriggerEQButton';
import type { LeaguePercentile } from '@/types';

interface PageProps {
  params: Promise<{ id: string }>;
}

export default async function PlayerDetailPage({ params }: PageProps) {
  const { id } = await params;
  const supabase = await createClient();

  const [{ data: player }, { data: eqRows }] = await Promise.all([
    supabase
      .from('players')
      .select(`
        *,
        player_style_profiles(*),
        player_injuries(*),
        league_percentiles(*)
      `)
      .eq('id', id)
      .single(),
    supabase
      .from('eq_analyses')
      .select('*')
      .eq('player_id', id)
      .limit(1),
  ]);

  if (!player) notFound();

  const profile = player.player_style_profiles?.[0];
  const injury = player.player_injuries?.[0];
  const eq = eqRows?.[0] ?? null;
  const percentiles = (player.league_percentiles ?? []) as LeaguePercentile[];
  const stats = player.stats ?? {};

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-start gap-4">
        <Link href="/players" className="text-gray-400 hover:text-white mt-1 transition-colors">
          <ArrowLeft size={20} />
        </Link>
        <div className="flex-1">
          <div className="flex items-center gap-3 flex-wrap">
            <h1 className="text-3xl font-black text-white">{player.name}</h1>
            {profile && (
              <span className="bg-emerald-500/10 text-emerald-400 font-semibold text-sm px-3 py-1 rounded-full">
                {profile.primary_profile_id}
              </span>
            )}
            {injury && <InjuryStatusBadge status={injury.status} />}
          </div>
          <div className="text-gray-400 mt-1">
            {[player.position, player.current_club, player.league].filter(Boolean).join(' · ')}
            {player.age && ` · Age ${player.age}`}
            {player.nationality && ` · ${player.nationality}`}
            {player.height_cm && ` · ${player.height_cm}cm`}
            {player.preferred_foot && ` · ${player.preferred_foot} foot`}
          </div>
        </div>
        <div className="flex gap-2 shrink-0">
          <form action="/api/shortlist/add" method="post">
            <input type="hidden" name="player_id" value={player.id} />
            <button type="submit" className="flex items-center gap-2 bg-gray-800 hover:bg-gray-700 text-gray-300 font-medium px-4 py-2 rounded-lg text-sm transition-colors">
              <Bookmark size={14} />
              Shortlist
            </button>
          </form>
          <Link
            href={`/reports/new?player=${player.id}`}
            className="flex items-center gap-2 bg-emerald-500 hover:bg-emerald-400 text-white font-medium px-4 py-2 rounded-lg text-sm transition-colors"
          >
            <FileText size={14} />
            Report
          </Link>
        </div>
      </div>

      {/* Percentiles */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-semibold text-white text-sm">League percentiles</h2>
          {stats.appearances && (
            <span className="text-xs text-gray-600">{stats.appearances} apps · {stats.minutes_played} min</span>
          )}
        </div>
        <PercentileGrid percentiles={percentiles} stats={stats} />
      </div>

      {/* Style profile */}
      {profile && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-semibold text-white text-sm">Style profile</h2>
            <span className={`text-xs px-2 py-0.5 rounded-full capitalize ${
              profile.confidence_level === 'high' ? 'bg-emerald-500/10 text-emerald-400' :
              profile.confidence_level === 'medium' ? 'bg-yellow-500/10 text-yellow-400' :
              'bg-red-500/10 text-red-400'
            }`}>
              {profile.confidence_level} confidence
            </span>
          </div>
          <div className="flex gap-2 flex-wrap">
            <ProfileBadge id={profile.primary_profile_id} label="Primary" />
            {profile.secondary_profile_id && (
              <ProfileBadge id={profile.secondary_profile_id} label="Secondary" />
            )}
          </div>
          {profile.key_evidence?.length && (
            <ul className="mt-2 text-xs text-gray-500 space-y-0.5">
              {profile.key_evidence.map((e: string, i: number) => (
                <li key={i}>· {e}</li>
              ))}
            </ul>
          )}
        </div>
      )}

      {/* Injury */}
      {injury && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-semibold text-white text-sm">Injury & availability</h2>
            <div className="flex items-center gap-3">
              <span className={`text-xs font-medium ${
                injury.status === 'available' ? 'text-emerald-400' :
                injury.status === 'doubtful' ? 'text-yellow-400' : 'text-red-400'
              }`}>
                {injury.status.charAt(0).toUpperCase() + injury.status.slice(1)}
              </span>
              <RiskGradeBadge grade={injury.risk_grade} score={injury.risk_score} />
            </div>
          </div>
          <div className="flex flex-wrap gap-4 text-xs mb-3">
            {injury.current_injury_type && (
              <span className="text-gray-400">Injury: <span className="text-white">{injury.current_injury_type}</span></span>
            )}
            {injury.return_estimate && (
              <span className="text-gray-400">Return: <span className="text-white">{new Date(injury.return_estimate).toLocaleDateString()}</span></span>
            )}
            <span className="text-gray-400">Games missed: <span className="text-white">{injury.total_missed_games ?? 0}</span></span>
          </div>
          {injury.injury_history?.length > 0 && (
            <div className="space-y-1">
              {injury.injury_history.map((h: InjuryHistoryItem, i: number) => (
                <div key={i} className="flex items-center gap-2 text-xs text-gray-500">
                  <span>{h.from}</span>
                  <span>→</span>
                  <span className="text-gray-400">{h.type}</span>
                  {h.games_missed > 0 && <span>({h.games_missed} games)</span>}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* EQ */}
      {eq ? (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-semibold text-white text-sm">EQ Analysis</h2>
            <div className="flex items-center gap-2">
              <span className={`text-xs font-semibold ${
                eq.grade === 'HIGH' ? 'text-emerald-400' :
                eq.grade === 'MEDIUM' ? 'text-yellow-400' :
                'text-gray-500'
              }`}>{eq.grade}</span>
              <span className="text-white font-bold">{eq.total_score}<span className="text-gray-600 font-normal text-xs">/100</span></span>
            </div>
          </div>
          {eq.verdict && <p className="text-xs text-gray-500 mb-3">{eq.verdict}</p>}
          {eq.dimensions && (
            <div className="space-y-3">
              {Object.entries(eq.dimensions as EQDimensions).map(([key, dim]) => (
                <div key={key}>
                  <div className="flex items-center justify-between text-xs mb-1">
                    <span className="text-gray-500 capitalize">{key.replace(/_/g, ' ')}</span>
                    <span className="text-gray-400">{dim.score}/20</span>
                  </div>
                  <div className="h-1 bg-gray-800 rounded-full overflow-hidden">
                    <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${(dim.score / 20) * 100}%` }} />
                  </div>
                  {dim.evidence?.length > 0 && (
                    <ul className="mt-1 space-y-0.5">
                      {dim.evidence.map((e: string, i: number) => (
                        <li key={i} className="text-xs text-gray-600">· {e}</li>
                      ))}
                    </ul>
                  )}
                  {dim.flags?.length > 0 && (
                    <ul className="mt-0.5 space-y-0.5">
                      {dim.flags.map((f: string, i: number) => (
                        <li key={i} className="text-xs text-yellow-700">⚠ {f}</li>
                      ))}
                    </ul>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      ) : (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
          <div className="flex items-center justify-between">
            <h2 className="font-semibold text-white text-sm">EQ Analysis</h2>
            <TriggerEQButton playerId={player.id} />
          </div>
          <p className="text-xs text-gray-600 mt-2">No EQ analysis yet. Click &ldquo;Run EQ analysis&rdquo; to generate one.</p>
        </div>
      )}
    </div>
  );
}

function StatBox({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="bg-gray-800 rounded-lg p-3">
      <div className="text-xl font-bold text-white">{value}</div>
      <div className="text-xs text-gray-500 mt-0.5">{label}</div>
    </div>
  );
}

function ProfileBadge({ id, label }: { id: string; label: string }) {
  return (
    <div className="bg-gray-800 rounded-lg px-4 py-2">
      <div className="text-xs text-gray-500 mb-0.5">{label}</div>
      <div className="text-sm font-bold text-emerald-400">{id}</div>
    </div>
  );
}

function InjuryStatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    available: 'bg-emerald-500/10 text-emerald-400',
    doubtful: 'bg-yellow-500/10 text-yellow-400',
    injured: 'bg-red-500/10 text-red-400',
  };
  return (
    <span className={`text-sm font-medium px-3 py-1 rounded-full capitalize ${colors[status] ?? 'text-gray-400'}`}>
      {status}
    </span>
  );
}

function RiskGradeBadge({ grade, score }: { grade: string; score: number }) {
  const colors: Record<string, string> = {
    LOW: 'text-emerald-400',
    MEDIUM: 'text-yellow-400',
    HIGH: 'text-orange-400',
    CRITICAL: 'text-red-400',
  };
  return (
    <span className={`text-xs font-semibold ${colors[grade] ?? 'text-gray-400'}`}>
      {grade} {score}
    </span>
  );
}

interface InjuryHistoryItem {
  type: string;
  from: string;
  to?: string;
  games_missed: number;
}

interface EQDimension {
  score: number;
  evidence: string[];
  flags: string[];
}

interface EQDimensions {
  self_awareness: EQDimension;
  self_regulation: EQDimension;
  motivation: EQDimension;
  empathy: EQDimension;
  social_skills: EQDimension;
}
