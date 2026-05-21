import Link from 'next/link';
import type { PlayerWithDetails } from '@/types';

interface PlayerCardProps {
  player: PlayerWithDetails;
  fitScore?: number;
}

export default function PlayerCard({ player, fitScore }: PlayerCardProps) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 hover:border-gray-700 transition-colors">
      <div className="flex items-start justify-between">
        <div>
          <Link
            href={`/players/${player.id}`}
            className="text-lg font-bold text-white hover:text-emerald-400 transition-colors"
          >
            {player.name}
          </Link>
          {fitScore !== undefined && (
            <span className="ml-3 text-xs font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full">
              {fitScore}% fit
            </span>
          )}
          <div className="text-sm text-gray-500 mt-1">
            {[player.position, player.current_club, player.league].filter(Boolean).join(' · ')}
          </div>
        </div>

        {player.injury && (
          <div className={`text-xs font-semibold px-2 py-1 rounded-lg ${
            player.injury.risk_grade === 'LOW' ? 'bg-emerald-500/10 text-emerald-400' :
            player.injury.risk_grade === 'MEDIUM' ? 'bg-yellow-500/10 text-yellow-400' :
            player.injury.risk_grade === 'HIGH' ? 'bg-orange-500/10 text-orange-400' :
            'bg-red-500/10 text-red-400'
          }`}>
            {player.injury.risk_grade}
          </div>
        )}
      </div>

      {player.stats && (
        <div className="grid grid-cols-5 gap-2 mt-4">
          {[
            { label: 'G', value: player.stats.goals ?? 0 },
            { label: 'A', value: player.stats.assists ?? 0 },
            { label: 'xG', value: Number(player.stats.xg ?? 0).toFixed(1) },
            { label: 'xA', value: Number(player.stats.xa ?? 0).toFixed(1) },
            { label: 'PA%', value: `${player.stats.pass_accuracy ?? 0}` },
          ].map((s) => (
            <div key={s.label} className="text-center">
              <div className="text-base font-bold text-white">{s.value}</div>
              <div className="text-xs text-gray-600">{s.label}</div>
            </div>
          ))}
        </div>
      )}

      {player.style_profile && (
        <div className="mt-3 flex items-center gap-2">
          <span className="text-xs bg-gray-800 text-gray-400 px-2 py-0.5 rounded-full">
            {player.style_profile.primary_profile_id}
          </span>
          {player.style_profile.secondary_profile_id && (
            <span className="text-xs bg-gray-800 text-gray-400 px-2 py-0.5 rounded-full">
              {player.style_profile.secondary_profile_id}
            </span>
          )}
          <span className="text-xs text-gray-600 capitalize">
            {player.style_profile.confidence_level} confidence
          </span>
        </div>
      )}
    </div>
  );
}
