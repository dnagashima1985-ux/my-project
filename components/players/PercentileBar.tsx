interface PercentileBarProps {
  label: string;
  value: number;       // 0–100
  raw?: string | number;
  highlight?: boolean;
}

export default function PercentileBar({ label, value, raw, highlight }: PercentileBarProps) {
  const color =
    value >= 80 ? 'bg-emerald-500' :
    value >= 60 ? 'bg-emerald-400' :
    value >= 40 ? 'bg-yellow-400' :
    value >= 20 ? 'bg-orange-400' :
    'bg-red-400';

  const textColor =
    value >= 80 ? 'text-emerald-400' :
    value >= 60 ? 'text-emerald-300' :
    value >= 40 ? 'text-yellow-400' :
    'text-orange-400';

  return (
    <div className={`py-2 ${highlight ? 'opacity-100' : 'opacity-80'}`}>
      <div className="flex items-center justify-between mb-1">
        <span className={`text-xs font-medium ${highlight ? 'text-white' : 'text-gray-400'}`}>
          {label}
        </span>
        <div className="flex items-center gap-2">
          {raw !== undefined && (
            <span className="text-xs text-gray-600">{raw}</span>
          )}
          <span className={`text-xs font-bold w-8 text-right ${textColor}`}>
            {value}
          </span>
        </div>
      </div>
      <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ${color}`}
          style={{ width: `${value}%` }}
        />
      </div>
    </div>
  );
}
