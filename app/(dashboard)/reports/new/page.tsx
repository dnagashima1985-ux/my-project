'use client';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

function NewReportForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const playerId = searchParams.get('player');

  const [player, setPlayer] = useState<{ id: string; name: string; position: string; current_club: string } | null>(null);
  const [audience, setAudience] = useState<'ceo' | 'sd' | 'coach'>('sd');
  const [language, setLanguage] = useState('en');
  const [salary, setSalary] = useState('');
  const [transferFee, setTransferFee] = useState('');
  const [negotiationStatus, setNegotiationStatus] = useState('');
  const [competingClubs, setCompetingClubs] = useState('');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (playerId) {
      fetch(`/api/players/${playerId}`)
        .then((r) => r.json())
        .then((d) => setPlayer(d))
        .catch(() => {});
    }
  }, [playerId]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!playerId) { setError('No player selected'); return; }
    setError('');
    setLoading(true);

    const res = await fetch('/api/reports/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        player_id: playerId,
        audience,
        language,
        scout_inputs: {
          salary_eur: salary ? Number(salary) : undefined,
          transfer_fee_eur: transferFee ? Number(transferFee) : undefined,
          negotiation_status: negotiationStatus || undefined,
          competing_clubs: competingClubs ? competingClubs.split(',').map((c) => c.trim()) : undefined,
          notes: notes || undefined,
        },
      }),
    });

    if (!res.ok) {
      const data = await res.json();
      setError(data.error ?? 'Failed to generate report');
      setLoading(false);
      return;
    }

    const data = await res.json();
    router.push(`/reports/${data.id}`);
  }

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold text-white mb-6">Generate report</h1>

      {player && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 mb-6 flex items-center gap-3">
          <div className="w-10 h-10 bg-gray-800 rounded-full flex items-center justify-center text-sm font-bold text-gray-400">
            {player.position?.slice(0, 2)}
          </div>
          <div>
            <div className="font-semibold text-white">{player.name}</div>
            <div className="text-sm text-gray-500">{player.position} · {player.current_club}</div>
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-5">
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 text-red-400 rounded-lg px-4 py-3 text-sm">
            {error}
          </div>
        )}

        {/* Report type */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 space-y-3">
          <h2 className="font-semibold text-white">Report type</h2>
          <div className="grid grid-cols-3 gap-3">
            {([
              { id: 'ceo', label: 'CEO / Owner', desc: 'Investment & risk focus' },
              { id: 'sd', label: 'Sports Director', desc: 'Tactical & data analysis' },
              { id: 'coach', label: 'Coach', desc: 'Tactical role & fit' },
            ] as const).map((opt) => (
              <button
                key={opt.id}
                type="button"
                onClick={() => setAudience(opt.id)}
                className={`p-3 rounded-lg border text-left transition-colors ${
                  audience === opt.id
                    ? 'border-emerald-500 bg-emerald-500/10'
                    : 'border-gray-700 bg-gray-800 hover:border-gray-600'
                }`}
              >
                <div className="font-medium text-sm text-white">{opt.label}</div>
                <div className="text-xs text-gray-500 mt-0.5">{opt.desc}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Language */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 space-y-3">
          <h2 className="font-semibold text-white">Language</h2>
          <div className="flex flex-wrap gap-2">
            {[
              { id: 'en', label: 'English' },
              { id: 'ja', label: '日本語' },
              { id: 'nl', label: 'Nederlands' },
              { id: 'fr', label: 'Français' },
            ].map((l) => (
              <button
                key={l.id}
                type="button"
                onClick={() => setLanguage(l.id)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  language === l.id
                    ? 'bg-emerald-500 text-white'
                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                }`}
              >
                {l.label}
              </button>
            ))}
          </div>
        </div>

        {/* Scout inputs (optional) */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 space-y-4">
          <h2 className="font-semibold text-white">Scout inputs <span className="text-gray-600 text-xs font-normal">(optional)</span></h2>
          <p className="text-xs text-gray-600">Only CEO reports use financial data. AI will never invent figures you don&apos;t provide.</p>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Salary (EUR/year)</label>
              <input type="number" value={salary} onChange={(e) => setSalary(e.target.value)} className="input" placeholder="e.g. 800000" />
            </div>
            <div>
              <label className="label">Transfer fee (EUR)</label>
              <input type="number" value={transferFee} onChange={(e) => setTransferFee(e.target.value)} className="input" placeholder="e.g. 5000000" />
            </div>
          </div>

          <div>
            <label className="label">Negotiation status</label>
            <input type="text" value={negotiationStatus} onChange={(e) => setNegotiationStatus(e.target.value)} className="input" placeholder="e.g. Initial contact made" />
          </div>

          <div>
            <label className="label">Competing clubs</label>
            <input type="text" value={competingClubs} onChange={(e) => setCompetingClubs(e.target.value)} className="input" placeholder="Comma-separated: Ajax, PSV" />
          </div>

          <div>
            <label className="label">Scout notes</label>
            <textarea value={notes} onChange={(e) => setNotes(e.target.value)} className="input min-h-[80px] resize-none" placeholder="Add any observations, context, or notes..." />
          </div>
        </div>

        <button
          type="submit"
          disabled={loading || !playerId}
          className="w-full bg-emerald-500 hover:bg-emerald-400 disabled:bg-emerald-500/50 text-white font-bold py-4 rounded-xl text-lg transition-colors"
        >
          {loading ? '⚡ Generating report...' : 'Generate report →'}
        </button>
      </form>

      <style jsx>{`
        .label { display: block; font-size: 0.875rem; font-weight: 500; color: #d1d5db; margin-bottom: 0.375rem; }
        .input { width: 100%; background: #1f2937; border: 1px solid #374151; border-radius: 0.5rem; padding: 0.625rem 1rem; color: white; font-size: 0.875rem; outline: none; }
        .input:focus { border-color: #10b981; }
        .input::placeholder { color: #6b7280; }
      `}</style>
    </div>
  );
}

export default function NewReportPage() {
  return (
    <Suspense fallback={<div className="text-gray-400">Loading...</div>}>
      <NewReportForm />
    </Suspense>
  );
}
