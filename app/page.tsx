import Link from 'next/link';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Nav */}
      <nav className="border-b border-gray-800 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-2xl font-black text-emerald-400">Scout</span>
          <span className="text-2xl font-black text-white">IQ</span>
        </div>
        <div className="flex items-center gap-4">
          <Link href="/login" className="text-gray-400 hover:text-white text-sm transition-colors">
            Log in
          </Link>
          <Link
            href="/signup"
            className="bg-emerald-500 hover:bg-emerald-400 text-white text-sm font-semibold px-4 py-2 rounded-lg transition-colors"
          >
            Start free trial
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <main className="max-w-5xl mx-auto px-6 pt-24 pb-20 text-center">
        <div className="inline-flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/20 rounded-full px-4 py-1.5 text-emerald-400 text-sm font-medium mb-8">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          7 longlists free · All features · No credit card
        </div>

        <h1 className="text-5xl md:text-6xl font-black mb-6 leading-tight">
          AI-powered scouting intelligence
          <br />for{' '}
          <span className="text-emerald-400">football professionals</span>
        </h1>

        <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-10 leading-relaxed">
          From first look to final report —{' '}
          <span className="text-white font-semibold">ScoutIQ</span> combines AI analysis with real match data.
          Position × play style dual-axis evaluation. League-relative percentiles.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center mb-20">
          <Link
            href="/signup"
            className="bg-emerald-500 hover:bg-emerald-400 text-white font-bold text-lg px-8 py-4 rounded-xl transition-colors"
          >
            Start free — no credit card
          </Link>
          <Link
            href="/login"
            className="border border-gray-700 hover:border-gray-500 text-gray-300 hover:text-white font-semibold text-lg px-8 py-4 rounded-xl transition-colors"
          >
            Log in
          </Link>
        </div>

        {/* Feature grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
          {features.map((f) => (
            <div key={f.title} className="bg-gray-900 border border-gray-800 rounded-xl p-6">
              <div className="text-3xl mb-3">{f.icon}</div>
              <h3 className="font-bold text-white mb-2">{f.title}</h3>
              <p className="text-gray-400 text-sm leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </main>

      {/* Pricing */}
      <section className="border-t border-gray-800 py-20 px-6">
        <div className="max-w-4xl mx-auto text-center mb-12">
          <h2 className="text-3xl font-black mb-3">Simple pricing</h2>
          <p className="text-gray-400">Start free. Upgrade when you need more.</p>
        </div>
        <div className="max-w-4xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-4">
          {plans.map((p) => (
            <div
              key={p.name}
              className={`rounded-xl p-6 border ${
                p.highlight
                  ? 'border-emerald-500 bg-emerald-500/10'
                  : 'border-gray-800 bg-gray-900'
              }`}
            >
              {p.highlight && (
                <div className="text-xs font-bold text-emerald-400 uppercase tracking-wider mb-2">
                  Most popular
                </div>
              )}
              <div className="font-bold text-lg mb-1">{p.name}</div>
              <div className="text-3xl font-black text-emerald-400 mb-4">{p.price}</div>
              <ul className="space-y-2">
                {p.features.map((f) => (
                  <li key={f} className="text-sm text-gray-400 flex items-start gap-2">
                    <span className="text-emerald-400 mt-0.5">✓</span>
                    {f}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-800 py-8 px-6 text-center text-gray-600 text-sm">
        <p>© 2026 ScoutIQ. Professional football scouting intelligence.</p>
      </footer>
    </div>
  );
}

const features = [
  {
    icon: '🎯',
    title: 'AI Longlist Generation',
    desc: 'Enter a club profile and get a ranked longlist in minutes. 20 play style profiles × 18 positions dual-axis evaluation.',
  },
  {
    icon: '📊',
    title: 'League-Relative Percentiles',
    desc: 'Compare every stat against the player\'s own league. No more comparing Bundesliga xG to Serie A xG.',
  },
  {
    icon: '📋',
    title: 'Recipient-Specific Reports',
    desc: 'CEO, Sports Director, or Coach reports — each tailored to what that audience actually needs. PDF + PowerPoint.',
  },
  {
    icon: '🧠',
    title: 'EQ Analysis',
    desc: 'AI-powered emotional intelligence scoring across 5 dimensions. The industry\'s first automated EQ system for footballers.',
  },
  {
    icon: '🏥',
    title: 'Injury Intelligence',
    desc: 'Risk scoring 0–100 with LOW/MEDIUM/HIGH/CRITICAL grades. Know the negotiation implications before you make an offer.',
  },
  {
    icon: '📡',
    title: 'Market Intelligence (Elite)',
    desc: 'Daily transfer signals personalised to your club\'s profile. HOT/WARM/EARLY heat classification with alternative candidates.',
  },
];

const plans = [
  {
    name: 'Free Trial',
    price: '€0',
    highlight: false,
    features: ['7 longlists', 'All features unlocked', 'Email only', 'No credit card'],
  },
  {
    name: 'Starter',
    price: '€7/mo',
    highlight: false,
    features: ['10 longlists/mo', 'Percentiles', 'Profile classification', 'CSV export', 'Injury status'],
  },
  {
    name: 'Pro',
    price: '€14/mo',
    highlight: true,
    features: ['Unlimited longlists', 'Report builder', 'PDF + PPT export', 'EQ analysis', 'Injury details'],
  },
  {
    name: 'Elite',
    price: '€29/mo',
    highlight: false,
    features: ['Everything in Pro', 'Market Intelligence', '3 club registrations', 'Email alerts'],
  },
];
