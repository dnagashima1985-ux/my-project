import PercentileBar from './PercentileBar';
import type { LeaguePercentile } from '@/types';

interface PercentileGridProps {
  percentiles: LeaguePercentile[];
  stats?: Record<string, number>;
}

const STAT_LABELS: Record<string, string> = {
  goals:               'Goals',
  assists:             'Assists',
  xg:                  'xG',
  xa:                  'xA',
  shots:               'Shots',
  pass_accuracy:       'Pass accuracy',
  key_passes:          'Key passes',
  dribble_success_rate:'Dribble success',
  tackles:             'Tackles',
  interceptions:       'Interceptions',
  aerial_duel_win_pct: 'Aerial duels won',
};

// Stats that are most important to highlight
const HIGHLIGHT_STATS = new Set(['xg', 'xa', 'pass_accuracy', 'dribble_success_rate']);

export default function PercentileGrid({ percentiles, stats }: PercentileGridProps) {
  if (!percentiles.length) {
    return (
      <div className="text-center py-8 text-gray-600 text-sm">
        Percentile data not yet available for this player
      </div>
    );
  }

  const sorted = [...percentiles].sort((a, b) => b.percentile - a.percentile);

  return (
    <div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8">
        {sorted.map((p) => (
          <PercentileBar
            key={p.stat_name}
            label={STAT_LABELS[p.stat_name] ?? p.stat_name}
            value={p.percentile}
            raw={stats?.[p.stat_name]}
            highlight={HIGHLIGHT_STATS.has(p.stat_name)}
          />
        ))}
      </div>
      <p className="text-xs text-gray-600 mt-4">
        Percentiles relative to players in the same league and position this season.
      </p>
    </div>
  );
}
