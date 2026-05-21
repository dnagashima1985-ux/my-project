import { Resend } from 'resend';

function getResend() {
  return new Resend(process.env.RESEND_API_KEY!);
}

const FROM = 'ScoutIQ <hello@scoutiq.app>';

export async function sendWelcomeEmail(to: string): Promise<void> {
  const resend = getResend();
  await resend.emails.send({
    from: FROM,
    to,
    subject: 'Welcome to ScoutIQ — your 7 free longlists are ready',
    html: `
      <div style="font-family:system-ui,sans-serif;max-width:520px;margin:0 auto;background:#030712;color:#f9fafb;padding:40px 32px;border-radius:16px">
        <h1 style="color:#10b981;font-size:24px;margin:0 0 8px">Welcome to ScoutIQ</h1>
        <p style="color:#9ca3af;font-size:14px;margin:0 0 24px">The only scouting tool built for professional scouts</p>
        <p style="color:#f9fafb;margin:0 0 16px">You have <strong style="color:#10b981">7 free longlists</strong> — all features unlocked, no credit card required.</p>
        <p style="color:#f9fafb;margin:0 0 24px">Here&apos;s what you can do right now:</p>
        <ul style="color:#d1d5db;padding-left:20px;line-height:1.8">
          <li>Generate an AI longlist from a club profile</li>
          <li>View league-relative percentiles for every player</li>
          <li>Explore 20 play style profiles (P01–P20)</li>
          <li>Check injury risk scores before making your recommendation</li>
        </ul>
        <a href="https://scoutiq.app/longlist/new" style="display:inline-block;margin-top:28px;background:#10b981;color:#fff;font-weight:700;padding:14px 28px;border-radius:10px;text-decoration:none">
          Start scouting →
        </a>
        <p style="color:#4b5563;font-size:12px;margin-top:32px">ScoutIQ · Professional Football Scouting Intelligence</p>
      </div>
    `,
  });
}

export async function sendTrialLowEmail(to: string, remaining: number): Promise<void> {
  const resend = getResend();
  const urgency = remaining === 1 ? 'Last free longlist' : `${remaining} free longlists remaining`;
  await resend.emails.send({
    from: FROM,
    to,
    subject: `ScoutIQ: ${urgency}`,
    html: `
      <div style="font-family:system-ui,sans-serif;max-width:520px;margin:0 auto;background:#030712;color:#f9fafb;padding:40px 32px;border-radius:16px">
        <h1 style="color:#f97316;font-size:22px;margin:0 0 16px">${urgency}</h1>
        <p style="color:#f9fafb;margin:0 0 16px">
          You&apos;ve used ${7 - remaining} of your 7 free longlists.
          Upgrade to keep going — from just <strong style="color:#10b981">€7/month</strong>.
        </p>
        <a href="https://scoutiq.app/settings#plans" style="display:inline-block;margin-top:12px;background:#10b981;color:#fff;font-weight:700;padding:14px 28px;border-radius:10px;text-decoration:none">
          View plans →
        </a>
        <p style="color:#4b5563;font-size:12px;margin-top:32px">ScoutIQ · scoutiq.app</p>
      </div>
    `,
  });
}

export async function sendNewSignalEmail(
  to: string,
  signals: { target_player: string; interested_club: string; heat: string; position: string }[]
): Promise<void> {
  const resend = getResend();
  const signalRows = signals.map((s) => {
    const heatColor = s.heat === 'hot' ? '#ef4444' : s.heat === 'warm' ? '#f97316' : '#3b82f6';
    const heatLabel = s.heat === 'hot' ? '🔥 HOT' : s.heat === 'warm' ? '⚡ WARM' : '● EARLY';
    return `
      <tr>
        <td style="padding:10px 0;border-bottom:1px solid #1f2937;color:${heatColor};font-weight:700">${heatLabel}</td>
        <td style="padding:10px 0;border-bottom:1px solid #1f2937;color:#f9fafb">${s.target_player}</td>
        <td style="padding:10px 0;border-bottom:1px solid #1f2937;color:#9ca3af">${s.interested_club}</td>
        <td style="padding:10px 0;border-bottom:1px solid #1f2937;color:#6b7280">${s.position}</td>
      </tr>
    `;
  }).join('');

  await resend.emails.send({
    from: FROM,
    to,
    subject: `ScoutIQ: ${signals.length} new transfer signal${signals.length !== 1 ? 's' : ''} today`,
    html: `
      <div style="font-family:system-ui,sans-serif;max-width:600px;margin:0 auto;background:#030712;color:#f9fafb;padding:40px 32px;border-radius:16px">
        <h1 style="color:#10b981;font-size:22px;margin:0 0 8px">Market Intelligence</h1>
        <p style="color:#9ca3af;font-size:14px;margin:0 0 24px">${signals.length} new signal${signals.length !== 1 ? 's' : ''} detected today</p>
        <table style="width:100%;border-collapse:collapse">
          <thead>
            <tr style="color:#6b7280;font-size:12px;text-align:left">
              <th style="padding-bottom:8px">Heat</th>
              <th style="padding-bottom:8px">Player</th>
              <th style="padding-bottom:8px">Club tracking</th>
              <th style="padding-bottom:8px">Position</th>
            </tr>
          </thead>
          <tbody>${signalRows}</tbody>
        </table>
        <a href="https://scoutiq.app/market-intelligence" style="display:inline-block;margin-top:24px;background:#10b981;color:#fff;font-weight:700;padding:14px 28px;border-radius:10px;text-decoration:none">
          View all signals →
        </a>
        <p style="color:#4b5563;font-size:12px;margin-top:32px">
          Transfer signals are based on media reports and rumours. ScoutIQ does not verify accuracy.<br>
          ScoutIQ · scoutiq.app
        </p>
      </div>
    `,
  });
}
