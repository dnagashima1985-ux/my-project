'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard, ListChecks, Users, FileText,
  Bookmark, Radio, Settings, LogOut
} from 'lucide-react';

const navItems = [
  { href: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { href: '/longlist', icon: ListChecks, label: 'Longlist' },
  { href: '/players', icon: Users, label: 'Players' },
  { href: '/reports', icon: FileText, label: 'Reports' },
  { href: '/shortlist', icon: Bookmark, label: 'Shortlist' },
  { href: '/market-intelligence', icon: Radio, label: 'Market Intel', eliteOnly: true },
];

interface SidebarProps {
  userEmail: string;
  plan: string;
}

export default function Sidebar({ userEmail, plan }: SidebarProps) {
  const pathname = usePathname();

  return (
    <aside className="w-56 bg-gray-900 border-r border-gray-800 flex flex-col shrink-0">
      {/* Logo */}
      <div className="px-4 py-5 border-b border-gray-800">
        <Link href="/dashboard" className="flex items-center gap-1">
          <span className="text-xl font-black text-emerald-400">Scout</span>
          <span className="text-xl font-black text-white">IQ</span>
        </Link>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-2 py-4 space-y-0.5 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
          const isLocked = item.eliteOnly && plan !== 'elite';

          return (
            <Link
              key={item.href}
              href={isLocked ? '/settings#plans' : item.href}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                isActive
                  ? 'bg-emerald-500/10 text-emerald-400 font-medium'
                  : isLocked
                  ? 'text-gray-600 cursor-not-allowed'
                  : 'text-gray-400 hover:text-white hover:bg-gray-800'
              }`}
            >
              <item.icon size={16} />
              <span>{item.label}</span>
              {isLocked && (
                <span className="ml-auto text-xs bg-gray-800 text-gray-500 px-1.5 py-0.5 rounded">
                  Elite
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Bottom */}
      <div className="px-2 py-4 border-t border-gray-800 space-y-0.5">
        <Link
          href="/settings"
          className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-gray-400 hover:text-white hover:bg-gray-800 transition-colors"
        >
          <Settings size={16} />
          <span>Settings</span>
        </Link>

        {/* Plan badge */}
        <div className="px-3 py-2">
          <div className="text-xs text-gray-600 truncate">{userEmail}</div>
          <div className={`text-xs font-semibold mt-0.5 capitalize ${
            plan === 'elite' ? 'text-amber-400' :
            plan === 'pro' ? 'text-purple-400' :
            plan === 'starter' ? 'text-blue-400' :
            'text-gray-400'
          }`}>
            {plan === 'trial' ? 'Free trial' : plan}
          </div>
        </div>

        <form action="/api/auth/signout" method="post">
          <button
            type="submit"
            className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-gray-400 hover:text-white hover:bg-gray-800 transition-colors"
          >
            <LogOut size={16} />
            <span>Log out</span>
          </button>
        </form>
      </div>
    </aside>
  );
}
