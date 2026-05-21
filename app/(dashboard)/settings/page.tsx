import { createClient } from '@/lib/supabase/server';

const PLANS = [
  {
    id: 'trial',
    name: 'Free Trial',
    price: '€0',
    features: ['7 longlists total', 'All features unlocked', 'Email only', 'No credit card'],
    cta: null,
  },
  {
    id: 'starter',
    name: 'Starter',
    price: '€7/mo',
    features: ['10 longlists/month', 'Percentiles', 'Profile classification', 'CSV export', 'Injury status'],
    cta: 'Subscribe',
    priceId: process.env.STRIPE_STARTER_PRICE_ID,
  },
  {
    id: 'pro',
    name: 'Pro',
    price: '€14/mo',
    features: ['Unlimited longlists', 'Report builder', 'PDF + PPT export', 'EQ analysis', 'Full injury details'],
    cta: 'Subscribe',
    highlight: true,
    priceId: process.env.STRIPE_PRO_PRICE_ID,
  },
  {
    id: 'elite',
    name: 'Elite',
    price: '€29/mo',
    features: ['Everything in Pro', 'Market Intelligence', '3 club registrations', 'Email alerts'],
    cta: 'Subscribe',
    priceId: process.env.STRIPE_ELITE_PRICE_ID,
  },
];

export default async function SettingsPage() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();

  const { data: profile } = await supabase
    .from('users')
    .select('*')
    .eq('id', user!.id)
    .single();

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <h1 className="text-2xl font-bold text-white">Settings</h1>

      {/* Profile */}
      <section className="bg-gray-900 border border-gray-800 rounded-xl p-5">
        <h2 className="font-semibold text-white mb-4">Account</h2>
        <div className="space-y-3 text-sm">
          <div className="flex items-center justify-between">
            <span className="text-gray-400">Email</span>
            <span className="text-white">{user?.email}</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-gray-400">Plan</span>
            <span className={`font-semibold capitalize ${
              profile?.plan === 'elite' ? 'text-amber-400' :
              profile?.plan === 'pro' ? 'text-purple-400' :
              profile?.plan === 'starter' ? 'text-blue-400' :
              'text-gray-300'
            }`}>
              {profile?.plan === 'trial' ? 'Free trial' : profile?.plan}
            </span>
          </div>
          {profile?.plan === 'trial' && (
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Longlists remaining</span>
              <span className={`font-bold ${
                (profile.trial_uses_remaining ?? 0) <= 1 ? 'text-red-400' :
                (profile.trial_uses_remaining ?? 0) <= 3 ? 'text-yellow-400' :
                'text-white'
              }`}>
                {profile.trial_uses_remaining ?? 0} / 7
              </span>
            </div>
          )}
          <div className="flex items-center justify-between">
            <span className="text-gray-400">Language</span>
            <LangSelector currentLang={profile?.preferred_language ?? 'en'} userId={user!.id} />
          </div>
        </div>
      </section>

      {/* Plans */}
      <section id="plans">
        <h2 className="font-semibold text-white mb-4">Plans</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {PLANS.map((plan) => {
            const isCurrent = profile?.plan === plan.id;
            return (
              <div
                key={plan.id}
                className={`rounded-xl p-5 border ${
                  plan.highlight && !isCurrent
                    ? 'border-emerald-500/40 bg-emerald-500/5'
                    : isCurrent
                    ? 'border-emerald-500 bg-emerald-500/10'
                    : 'border-gray-800 bg-gray-900'
                }`}
              >
                {plan.highlight && !isCurrent && (
                  <div className="text-xs font-bold text-emerald-400 uppercase tracking-wider mb-2">
                    Most popular
                  </div>
                )}
                <div className="flex items-baseline justify-between mb-3">
                  <span className="font-bold text-white">{plan.name}</span>
                  <span className="text-xl font-black text-emerald-400">{plan.price}</span>
                </div>
                <ul className="space-y-1.5 mb-4">
                  {plan.features.map((f) => (
                    <li key={f} className="text-xs text-gray-400 flex items-start gap-2">
                      <span className="text-emerald-400 mt-0.5">✓</span>
                      {f}
                    </li>
                  ))}
                </ul>
                {isCurrent ? (
                  <div className="text-center text-sm font-medium text-emerald-400 bg-emerald-500/10 py-2 rounded-lg">
                    Current plan
                  </div>
                ) : plan.cta && plan.priceId ? (
                  <form action="/api/billing/checkout" method="post">
                    <input type="hidden" name="price_id" value={plan.priceId} />
                    <button
                      type="submit"
                      className="w-full bg-emerald-500 hover:bg-emerald-400 text-white font-semibold py-2 rounded-lg text-sm transition-colors"
                    >
                      {plan.cta}
                    </button>
                  </form>
                ) : null}
              </div>
            );
          })}
        </div>
        <p className="text-xs text-gray-600 text-center mt-3">
          Powered by Stripe. Cancel anytime. Break-even: Starter 43 · Pro 22 · Elite 11 users.
        </p>
      </section>

      {/* Danger zone */}
      <section className="bg-gray-900 border border-red-500/20 rounded-xl p-5">
        <h2 className="font-semibold text-red-400 mb-3">Danger zone</h2>
        <p className="text-sm text-gray-500 mb-3">
          Delete your account and all associated data. This action cannot be undone.
        </p>
        <form action="/api/account/delete" method="post">
          <button
            type="submit"
            className="text-sm text-red-400 hover:text-red-300 border border-red-500/30 hover:border-red-500/60 px-4 py-2 rounded-lg transition-colors"
          >
            Delete account
          </button>
        </form>
      </section>
    </div>
  );
}

function LangSelector({ currentLang, userId }: { currentLang: string; userId: string }) {
  const langs = [
    { id: 'en', label: 'English' },
    { id: 'ja', label: '日本語' },
    { id: 'nl', label: 'Nederlands' },
    { id: 'fr', label: 'Français' },
  ];
  const current = langs.find((l) => l.id === currentLang)?.label ?? 'English';

  return (
    <form action="/api/account/language" method="post" className="flex gap-2 items-center">
      <input type="hidden" name="user_id" value={userId} />
      <select
        name="language"
        defaultValue={currentLang}
        className="bg-gray-800 border border-gray-700 text-gray-300 text-sm rounded-lg px-3 py-1.5 focus:outline-none focus:border-emerald-500"
      >
        {langs.map((l) => (
          <option key={l.id} value={l.id}>{l.label}</option>
        ))}
      </select>
      <button
        type="submit"
        className="text-xs text-emerald-400 hover:text-emerald-300 underline"
      >
        Save
      </button>
    </form>
  );
}
