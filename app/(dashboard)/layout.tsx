import { redirect } from 'next/navigation';
import { createClient } from '@/lib/supabase/server';
import Sidebar from '@/components/layout/Sidebar';
import TrialBanner from '@/components/layout/TrialBanner';

export default async function DashboardLayout({ children }: { children: React.ReactNode }) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();

  if (!user) redirect('/login');

  const { data: profile } = await supabase
    .from('users')
    .select('*')
    .eq('id', user.id)
    .single();

  return (
    <div className="flex h-screen bg-gray-950 overflow-hidden">
      <Sidebar userEmail={user.email ?? ''} plan={profile?.plan ?? 'trial'} />
      <div className="flex-1 flex flex-col overflow-hidden">
        {profile?.plan === 'trial' && (
          <TrialBanner remaining={profile.trial_uses_remaining ?? 7} />
        )}
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
