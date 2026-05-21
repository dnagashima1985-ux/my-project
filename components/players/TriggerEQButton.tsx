'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { RefreshCw } from 'lucide-react';

export default function TriggerEQButton({ playerId }: { playerId: string }) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);

  async function handleClick() {
    setLoading(true);
    await fetch(`/api/players/${playerId}/trigger-eq`, { method: 'POST' });
    setLoading(false);
    setDone(true);
    router.refresh();
  }

  return (
    <button
      onClick={handleClick}
      disabled={loading || done}
      className="flex items-center gap-1.5 text-xs bg-gray-800 hover:bg-gray-700 disabled:opacity-50 text-gray-400 px-3 py-1.5 rounded-lg transition-colors"
    >
      <RefreshCw size={12} className={loading ? 'animate-spin' : ''} />
      {done ? 'Analysed' : loading ? 'Analysing...' : 'Run EQ analysis'}
    </button>
  );
}
