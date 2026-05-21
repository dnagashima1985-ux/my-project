'use client';

import { useRouter } from 'next/navigation';
import { Trash2 } from 'lucide-react';

export default function RemoveShortlistButton({ shortlistId }: { shortlistId: string }) {
  const router = useRouter();

  async function handleRemove() {
    await fetch(`/api/shortlist/${shortlistId}`, { method: 'DELETE' });
    router.refresh();
  }

  return (
    <button
      onClick={handleRemove}
      className="flex items-center gap-1.5 text-xs bg-gray-800 hover:bg-red-500/10 hover:text-red-400 text-gray-500 px-3 py-1.5 rounded-lg transition-colors"
    >
      <Trash2 size={12} />
      Remove
    </button>
  );
}
