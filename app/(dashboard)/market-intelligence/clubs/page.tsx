'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Plus, Trash2 } from 'lucide-react';

interface UserClub {
  id: string;
  club_name: string;
  league: string;
  tier: string;
  budget_range: string;
  style: string;
  country: string;
}

const LEAGUES = [
  'Premier League', 'La Liga', 'Bundesliga', 'Serie A', 'Ligue 1',
  'Eredivisie', 'Primeira Liga', 'Championship', 'J1 League', 'MLS', 'Other',
];

const TIERS = [
  'Top 6', 'Mid-table', 'Lower half', 'Promotion contender', 'Relegation battler',
];

const BUDGET_RANGES = [
  '< €5M', '€5–15M', '€15–30M', '€30–60M', '€60M+',
];

const STYLES = [
  'High press', 'Possession', 'Counter-attack', 'Direct play', 'Low block', 'Gegenpressing', 'Mixed',
];

export default function ClubsPage() {
  const router = useRouter();
  const [clubs, setClubs] = useState<UserClub[]>([]);
  const [loading, setLoading] = useState(true);
  const [adding, setAdding] = useState(false);
  const [form, setForm] = useState({
    club_name: '', league: '', tier: '', budget_range: '', style: '', country: '',
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetch('/api/user-clubs').then((r) => r.json()).then((d) => {
      setClubs(d.clubs ?? []);
      setLoading(false);
    });
  }, []);

  async function handleAdd(e: React.FormEvent) {
    e.preventDefault();
    if (!form.club_name || !form.league) { setError('Club name and league are required'); return; }
    if (clubs.length >= 3) { setError('Maximum 3 clubs on Elite plan'); return; }
    setError('');
    setSaving(true);

    const res = await fetch('/api/user-clubs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form),
    });

    if (!res.ok) {
      setError('Failed to add club');
      setSaving(false);
      return;
    }

    const data = await res.json();
    setClubs((prev) => [...prev, data.club]);
    setForm({ club_name: '', league: '', tier: '', budget_range: '', style: '', country: '' });
    setAdding(false);
    setSaving(false);
  }

  async function handleDelete(id: string) {
    await fetch(`/api/user-clubs/${id}`, { method: 'DELETE' });
    setClubs((prev) => prev.filter((c) => c.id !== id));
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="flex items-center gap-3 mb-6">
        <Link href="/market-intelligence" className="text-gray-400 hover:text-white transition-colors">
          <ArrowLeft size={20} />
        </Link>
        <div>
          <h1 className="text-xl font-bold text-white">Registered clubs</h1>
          <p className="text-sm text-gray-500">ScoutIQ filters signals to similar clubs only</p>
        </div>
      </div>

      {/* Club list */}
      {loading ? (
        <div className="text-gray-500 py-8 text-center">Loading...</div>
      ) : (
        <div className="space-y-3 mb-6">
          {clubs.map((club) => (
            <div key={club.id} className="bg-gray-900 border border-gray-800 rounded-xl p-5 flex items-start justify-between">
              <div>
                <div className="font-semibold text-white">{club.club_name}</div>
                <div className="text-sm text-gray-500 mt-0.5">
                  {[club.league, club.tier, club.budget_range, club.style].filter(Boolean).join(' · ')}
                </div>
              </div>
              <button
                onClick={() => handleDelete(club.id)}
                className="text-gray-600 hover:text-red-400 transition-colors"
              >
                <Trash2 size={16} />
              </button>
            </div>
          ))}

          {clubs.length === 0 && !adding && (
            <div className="text-center py-12 text-gray-600">
              <p className="mb-2">No clubs registered yet</p>
              <p className="text-sm">Register your club to receive personalised daily signals</p>
            </div>
          )}
        </div>
      )}

      {/* Add form */}
      {adding ? (
        <form onSubmit={handleAdd} className="bg-gray-900 border border-gray-800 rounded-xl p-5 space-y-4">
          <h2 className="font-semibold text-white">Register a club</h2>
          {error && (
            <div className="bg-red-500/10 border border-red-500/20 text-red-400 rounded-lg px-4 py-3 text-sm">{error}</div>
          )}
          <div>
            <label className="label">Club name *</label>
            <input type="text" value={form.club_name} onChange={(e) => setForm((f) => ({ ...f, club_name: e.target.value }))} required className="input" placeholder="e.g. FC Utrecht" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">League *</label>
              <select value={form.league} onChange={(e) => setForm((f) => ({ ...f, league: e.target.value }))} required className="input">
                <option value="">Select...</option>
                {LEAGUES.map((l) => <option key={l} value={l}>{l}</option>)}
              </select>
            </div>
            <div>
              <label className="label">Country</label>
              <input type="text" value={form.country} onChange={(e) => setForm((f) => ({ ...f, country: e.target.value }))} className="input" placeholder="e.g. Netherlands" />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">League tier</label>
              <select value={form.tier} onChange={(e) => setForm((f) => ({ ...f, tier: e.target.value }))} className="input">
                <option value="">Select...</option>
                {TIERS.map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div>
              <label className="label">Transfer budget</label>
              <select value={form.budget_range} onChange={(e) => setForm((f) => ({ ...f, budget_range: e.target.value }))} className="input">
                <option value="">Select...</option>
                {BUDGET_RANGES.map((b) => <option key={b} value={b}>{b}</option>)}
              </select>
            </div>
          </div>
          <div>
            <label className="label">Play style</label>
            <select value={form.style} onChange={(e) => setForm((f) => ({ ...f, style: e.target.value }))} className="input">
              <option value="">Select...</option>
              {STYLES.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
          <div className="flex gap-3">
            <button type="submit" disabled={saving} className="bg-emerald-500 hover:bg-emerald-400 disabled:bg-emerald-500/50 text-white font-semibold px-6 py-2 rounded-lg text-sm transition-colors">
              {saving ? 'Saving...' : 'Register club'}
            </button>
            <button type="button" onClick={() => { setAdding(false); setError(''); }} className="text-gray-400 hover:text-white px-4 py-2 rounded-lg text-sm transition-colors">
              Cancel
            </button>
          </div>
        </form>
      ) : clubs.length < 3 ? (
        <button
          onClick={() => setAdding(true)}
          className="flex items-center gap-2 border border-dashed border-gray-700 hover:border-emerald-500/50 text-gray-400 hover:text-emerald-400 w-full py-4 rounded-xl justify-center text-sm transition-colors"
        >
          <Plus size={16} />
          Register club ({clubs.length}/3)
        </button>
      ) : (
        <p className="text-center text-sm text-gray-600">Maximum 3 clubs reached (Elite plan)</p>
      )}

      <style jsx>{`
        .label { display: block; font-size: 0.875rem; font-weight: 500; color: #d1d5db; margin-bottom: 0.375rem; }
        .input { width: 100%; background: #1f2937; border: 1px solid #374151; border-radius: 0.5rem; padding: 0.625rem 1rem; color: white; font-size: 0.875rem; outline: none; }
        .input:focus { border-color: #10b981; }
        .input::placeholder { color: #6b7280; }
      `}</style>
    </div>
  );
}
