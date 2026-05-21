'use client';

import Link from 'next/link';

interface TrialBannerProps {
  remaining: number;
}

export default function TrialBanner({ remaining }: TrialBannerProps) {
  const color =
    remaining >= 4 ? 'bg-gray-800 border-gray-700 text-gray-300' :
    remaining === 3 ? 'bg-yellow-500/10 border-yellow-500/20 text-yellow-400' :
    remaining === 2 ? 'bg-orange-500/10 border-orange-500/20 text-orange-400' :
    'bg-red-500/10 border-red-500/20 text-red-400';

  const pulse = remaining === 1 ? 'animate-pulse' : '';

  return (
    <div className={`border-b px-6 py-2 flex items-center justify-between text-sm ${color} ${pulse}`}>
      <span>
        {remaining === 0
          ? '🚫 Free trial used up'
          : `⚡ ${remaining} free longlist${remaining !== 1 ? 's' : ''} remaining`}
      </span>
      <Link
        href="/settings#plans"
        className="font-semibold underline underline-offset-2 hover:no-underline"
      >
        Upgrade →
      </Link>
    </div>
  );
}
