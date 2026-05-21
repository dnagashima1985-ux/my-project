import { createClient } from '@/lib/supabase/server';
import { notFound } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Bookmark, FileText } from 'lucide-react';

interface PageProps {
  params: Promise<{ id: string }>;
}

export default async function PlayerDetailPage({ params }: PageProps) {
  const { id } = await params;
  const supabase = await createClient();

  const { data: player } = await supabase
    .from('players')
    .select(`
      *,
      player_style_profiles(*),
      player_injuries(*),
      league_percentiles(*),
      eq_analyses(*)
    `)
    .eq('id', id)
    .single();

  if (!player) notFound();

  const profile = player.player_style_profiles?.[0];
  const injury = player.player_injuries?.[0];
  const eq = player.eq_analyses?.[0];
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

      {/* Stats grid */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
        <h2 className="font-semibold text-white mb-4">Season statistics</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatBox label="Goals" value={stats.goals ?? 0} />
          <StatBox label="Assists" value={stats.assists ?? 0} />
          <StatBox label="xG" value={Number(stats.xg ?? 0).toFixed(2)} />
          <StatBox label="npxG" value={Number(stats.npxg ?? 0).toFixed(2)} />
          <StatBox label="xA" value={Number(stats.xa ?? 0).toFixed(2)} />
          <StatBox label="Shots" value={stats.shots ?? 0} />
          <StatBox label="Pass accuracy" value={`${stats.pass_accuracy ?? 0}%`} />
          <StatBox label="Key passes" value={stats.key_passes ?? 0} />
          <StatBox label="Dribble success" value={`${stats.dribble_success_rate ?? 0}%`} />
          <StatBox label="Tackles" value={stats.tackles ?? 0} />
          <StatBox label="Interceptions" value={stats.interceptions ?? 0} />
          <StatBox label="Aerial duel %" value={`${stats.aerial_duel_win_pct ?? 0}%`} />
        </div>
        {stats.appearances && (
          <p className="text-xs text-gray-600 mt-3">
            {stats.appearances} appearances · {stats.minutes_played} minutes
          </p>
        )}
      </div>

      {/* Style profile */}
      {profile && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-semibold text-white">Style profile</h2>
            <span className={`text-xs px-2 py-0.5 rounded-full capitalize ${
              profile.confidence_level === 'high' ? 'bg-emerald-500/10 text-emerald-400' :
              profile.confidence_level === 'medium' ? 'bg-yellow-500/10 text-yellow-400' :
              'bg-red-500/10 text-red-400'
            }`}>
              {profile.confidence_level} confidence
            </span>
          </div>
          <div className="flex gap-3 flex-wrap">
            <ProfileBadge id={profile.primary_profile_id} label="Primary" />
            {profile.secondary_profile_id && (
              <ProfileBadge id={profile.secondary_profile_id} label="Secondary" />
            )}
          </div>
          {profile.key_evidence?.length && (
            <div className="mt-3">
              <p className="text-xs text-gray-500 mb-1">Key evidence:</p>
              <ul className="text-xs text-gray-400 space-y-0.5">
                {profile.key_evidence.map((e: string, i: number) => (
                  <li key={i}>· {e}</li>
                ))}
              </ul>
            </div>
          )}
          <p className="text-xs text-gray-600 italic mt-3">
            ⓘ Profiles are estimated using available statistics. Advanced metrics (pressures, progressive carries) are not available from current data sources.
          </p>
        </div>
      )}

      {/* Injury */}
      {injury && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-white">Injury information</h2>
            <RiskGradeBadge grade={injury.risk_grade} score={injury.risk_score} />
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm mb-4">
            <div>
              <div className="text-gray-500 text-xs mb-1">Current status</div>
              <div className={`font-medium ${
                injury.status === 'available' ? 'text-emerald-400' :
                injury.status === 'doubtful' ? 'text-yellow-400' : 'text-red-400'
              }`}>
                {injury.status.charAt(0).toUpperCase() + injury.status.slice(1)}
              </div>
            </div>
            {injury.current_injury_type && (
              <div>
                <div className="text-gray-500 text-xs mb-1">Current injury</div>
                <div className="text-white">{injury.current_injury_type}</div>
              </div>
            )}
            {injury.return_estimate && (
              <div>
                <div className="text-gray-500 text-xs mb-1">Expected return</div>
                <div className="text-white">{new Date(injury.return_estimate).toLocaleDateString()}</div>
              </div>
            )}
            <div>
              <div className="text-gray-500 text-xs mb-1">Games missed (total)</div>
              <div className="text-white">{injury.total_missed_games ?? 0}</div>
            </div>
          </div>
          {injury.injury_history?.length > 0 && (
            <div>
              <p className="text-xs text-gray-500 mb-2">Injury history</p>
              <div className="space-y-1">
                {injury.injury_history.map((h: InjuryHistoryItem, i: number) => (
                  <div key={i} className="flex items-center gap-3 text-xs text-gray-400">
                    <span className="text-gray-600">{h.from}</span>
                    <span className="text-gray-700">→</span>
                    <span>{h.type}</span>
                    {h.games_missed > 0 && <span className="text-gray-600">({h.games_missed} games)</span>}
                  </div>
                ))}
              </div>
            </div>
          )}
          <p className="text-xs text-gray-600 italic mt-4">
            ⓘ Injury data is sourced from publicly available sports databases. Return dates are estimates only.
          </p>
        </div>
      )}

      {/* EQ */}
      {eq ? (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-white">EQ Analysis</h2>
            <div className="text-right">
              <div className="text-2xl font-black text-white">{eq.total_score}<span className="text-gray-600 text-base font-normal">/100</span></div>
              <div className={`text-xs font-semibold ${
                eq.grade === 'HIGH' ? 'text-emerald-400' :
                eq.grade === 'MEDIUM' ? 'text-yellow-400' :
                'text-red-400'
              }`}>{eq.grade}</div>
            </div>
          </div>
          {eq.verdict && <p className="text-sm text-gray-400 mb-4">{eq.verdict}</p>}
          {eq.dimensions && (
            <div className="space-y-3">
              {Object.entries(eq.dimensions as EQDimensions).map(([key, dim]) => (
                <div key={key}>
                  <div className="flex items-center justify-between text-xs mb-1">
                    <span className="text-gray-400 capitalize">{key.replace(/_/g, ' ')}</span>
                    <span className="text-white font-medium">{dim.score}/20</span>
                  </div>
                  <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-emerald-500 rounded-full"
                      style={{ width: `${(dim.score / 20) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
          <p className="text-xs text-gray-600 italic mt-4">
            ⓘ EQ scores are AI-generated indicators based on publicly available media sources only.
          </p>
        </div>
      ) : (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 text-center text-gray-600">
          <p className="text-sm">EQ analysis not yet available for this player</p>
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
    LOW: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    MEDIUM: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
    HIGH: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
    CRITICAL: 'bg-red-500/10 text-red-400 border-red-500/20',
  };
  return (
    <div className={`border rounded-lg px-3 py-1 text-center ${colors[grade] ?? 'text-gray-400'}`}>
      <div className="text-xs font-semibold">{grade}</div>
      <div className="text-lg font-black">{score}</div>
    </div>
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
