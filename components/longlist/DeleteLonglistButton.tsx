'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Trash2 } from 'lucide-react';

export default function DeleteLonglistButton({ id }: { id: string }) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  async function handleDelete(e: React.MouseEvent) {
    e.preventDefault();
    if (!confirm('このロングリストを削除しますか？')) return;
    setLoading(true);
    await fetch(`/api/longlist/${id}`, { method: 'DELETE' });
    router.refresh();
  }

  return (
    <button
      onClick={handleDelete}
      disabled={loading}
      className="p-2 text-gray-600 hover:text-red-400 transition-colors disabled:opacity-50"
    >
      <Trash2 size={16} />
    </button>
  );
}
