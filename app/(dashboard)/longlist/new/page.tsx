'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

const POSITIONS = [
  'GK', 'CB', 'LB', 'RB', 'CDM', 'CM', 'CAM', 'LW', 'RW', 'ST', 'CF'
];

const STYLE_PROFILES = [
  { id: 'P01', name: 'Press Trigger' },
  { id: 'P02', name: 'Deep Playmaker' },
  { id: 'P03', name: 'Box-to-Box' },
  { id: 'P04', name: 'Ball Carrier' },
  { id: 'P05', name: 'Creative Midfielder' },
  { id: 'P06', name: 'Goal Scorer' },
  { id: 'P07', name: 'Target Man' },
  { id: 'P08', name: 'False Nine' },
  { id: 'P09', name: 'Inside Forward' },
  { id: 'P10', name: 'Wide Playmaker' },
  { id: 'P11', name: 'Pressing Winger' },
  { id: 'P12', name: 'Overlapping Fullback' },
  { id: 'P13', name: 'Inverted Fullback' },
  { id: 'P14', name: 'Ball-Playing CB' },
  { id: 'P15', name: 'Defensive CB' },
  { id: 'P16', name: 'Sweeper' },
  { id: 'P17', name: 'Anchor' },
  { id: 'P18', name: 'Ball-Winner' },
  { id: 'P19', name: 'Goalkeeper Sweeper' },
  { id: 'P20', name: 'Shot-Stopper' },
];

const TOP_LEAGUES = [
  'Premier League', 'La Liga', 'Bundesliga', 'Serie A', 'Ligue 1',
  'Eredivisie', 'Primeira Liga', 'Championship', 'Pro League (Belgium)',
  'J1 League', 'MLS', 'Bundesliga 2', 'Serie B',
];

export default function NewLonglistPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [clubName, setClubName] = useState('');
  const [formation, setFormation] = useState('');
  const [style, setStyle] = useState('');
  const [positions, setPositions] = useState<string[]>([]);
  const [styleProfiles, setStyleProfiles] = useState<string[]>([]);
  const [ageMin, setAgeMin] = useState('18');
  const [ageMax, setAgeMax] = useState('30');
  const [heightMin, setHeightMin] = useState('');
  const [budget, setBudget] = useState('');
  const [leagues, setLeagues] = useState<string[]>([]);

  function toggle<T>(arr: T[], setArr: (v: T[]) => void, val: T) {
    setArr(arr.includes(val) ? arr.filter((x) => x !== val) : [...arr, val]);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!clubName || positions.length === 0) {
      setError('Club name and at least one position are required.');
      return;
    }
    setError('');
    setLoading(true);

    const res = await fetch('/api/longlist/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        club_name: clubName,
        formation,
        style,
        positions,
        style_profiles: styleProfiles,
        age_min: Number(ageMin),
        age_max: Number(ageMax),
        height_min: heightMin ? Number(heightMin) : undefined,
        budget_eur: budget ? Number(budget) : undefined,
        target_leagues: leagues,
      }),
    });

    if (!res.ok) {
      const data = await res.json();
      setError(data.error ?? 'Failed to generate longlist');
      setLoading(false);
      return;
    }

    const data = await res.json();
    router.push(`/longlist/${data.id}`);
  }

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold text-white mb-6">New longlist</h1>

      <form onSubmit={handleSubmit} className="space-y-6">
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 text-red-400 rounded-lg px-4 py-3 text-sm">
            {error}
          </div>
        )}

        {/* Club info */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 space-y-4">
          <h2 className="font-semibold text-white">Club profile</h2>

          <div>
            <label className="label">Club name *</label>
            <input
              type="text"
              value={clubName}
              onChange={(e) => setClubName(e.target.value)}
              required
              className="input"
              placeholder="e.g. FC Utrecht"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Formation</label>
              <input
                type="text"
                value={formation}
                onChange={(e) => setFormation(e.target.value)}
                className="input"
                placeholder="e.g. 4-3-3"
              />
            </div>
            <div>
              <label className="label">Play style</label>
              <input
                type="text"
                value={style}
                onChange={(e) => setStyle(e.target.value)}
                className="input"
                placeholder="e.g. High press, possession"
              />
            </div>
          </div>
        </div>

        {/* Player criteria */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 space-y-4">
          <h2 className="font-semibold text-white">Player criteria</h2>

          <div>
            <label className="label">Target positions *</label>
            <div className="flex flex-wrap gap-2 mt-2">
              {POSITIONS.map((p) => (
                <button
                  key={p}
                  type="button"
                  onClick={() => toggle(positions, setPositions, p)}
                  className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                    positions.includes(p)
                      ? 'bg-emerald-500 text-white'
                      : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                  }`}
                >
                  {p}
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Min age</label>
              <input type="number" value={ageMin} onChange={(e) => setAgeMin(e.target.value)} className="input" min="15" max="45" />
            </div>
            <div>
              <label className="label">Max age</label>
              <input type="number" value={ageMax} onChange={(e) => setAgeMax(e.target.value)} className="input" min="15" max="45" />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Min height (cm)</label>
              <input type="number" value={heightMin} onChange={(e) => setHeightMin(e.target.value)} className="input" placeholder="Optional" />
            </div>
            <div>
              <label className="label">Budget (EUR)</label>
              <input type="number" value={budget} onChange={(e) => setBudget(e.target.value)} className="input" placeholder="Optional" />
            </div>
          </div>
        </div>

        {/* Style profiles */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 space-y-3">
          <div>
            <h2 className="font-semibold text-white">Style profiles</h2>
            <p className="text-xs text-gray-500 mt-0.5">Select desired play styles for your targets</p>
          </div>
          <div className="flex flex-wrap gap-2">
            {STYLE_PROFILES.map((sp) => (
              <button
                key={sp.id}
                type="button"
                onClick={() => toggle(styleProfiles, setStyleProfiles, sp.id)}
                className={`px-3 py-1 rounded-lg text-xs font-medium transition-colors ${
                  styleProfiles.includes(sp.id)
                    ? 'bg-emerald-500 text-white'
                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                }`}
              >
                {sp.id} {sp.name}
              </button>
            ))}
          </div>
          <p className="text-xs text-gray-600 italic">
            ⓘ Profiles are estimated using available statistics. Advanced metrics (pressures, progressive carries) are not available from current data sources.
          </p>
        </div>

        {/* Target leagues */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 space-y-3">
          <h2 className="font-semibold text-white">Target leagues</h2>
          <div className="flex flex-wrap gap-2">
            {TOP_LEAGUES.map((l) => (
              <button
                key={l}
                type="button"
                onClick={() => toggle(leagues, setLeagues, l)}
                className={`px-3 py-1 rounded-lg text-xs font-medium transition-colors ${
                  leagues.includes(l)
                    ? 'bg-emerald-500 text-white'
                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                }`}
              >
                {l}
              </button>
            ))}
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-emerald-500 hover:bg-emerald-400 disabled:bg-emerald-500/50 text-white font-bold py-4 rounded-xl text-lg transition-colors"
        >
          {loading ? '⚡ Generating with AI...' : 'Generate longlist →'}
        </button>
      </form>

      <style jsx>{`
        .label { display: block; font-size: 0.875rem; font-weight: 500; color: #d1d5db; margin-bottom: 0.375rem; }
        .input { width: 100%; background: #1f2937; border: 1px solid #374151; border-radius: 0.5rem; padding: 0.625rem 1rem; color: white; font-size: 0.875rem; outline: none; }
        .input:focus { border-color: #10b981; ring: 2px solid #10b981; }
        .input::placeholder { color: #6b7280; }
      `}</style>
    </div>
  );
}
