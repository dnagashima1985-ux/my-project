import type { StyleProfileId, PlayerStats } from '@/types';

export type { StyleProfileId };

export interface ClassifyProfileInput {
  position: string;
  stats: PlayerStats;
  height_cm?: number;
}

export interface ClassifyProfileResult {
  primary: StyleProfileId;
  secondary?: StyleProfileId;
  scores: Record<StyleProfileId, number>;
  confidence: 'high' | 'medium' | 'low';
  caveats: string[];
}

const ALL_PROFILE_IDS: StyleProfileId[] = [
  'P01', 'P02', 'P03', 'P04', 'P05',
  'P06', 'P07', 'P08', 'P09', 'P10',
  'P11', 'P12', 'P13', 'P14', 'P15',
  'P16', 'P17', 'P18', 'P19', 'P20',
];

function clamp(v: number, min = 0, max = 100): number {
  return Math.max(min, Math.min(max, v));
}

function norm(value: number, lo: number, hi: number): number {
  if (hi === lo) return 0;
  return clamp(((value - lo) / (hi - lo)) * 100);
}

function per90(raw: number | undefined, minutes: number | undefined): number | undefined {
  if (raw == null || !minutes || minutes <= 0) return undefined;
  return (raw / minutes) * 90;
}

interface ScoringCtx {
  s: PlayerStats;
  min90: number | undefined;
  height: number | undefined;
  caveats: string[];
  missing: number;
  total: number;
}

function use(
  ctx: ScoringCtx,
  value: number | undefined,
  caveat?: string
): number {
  ctx.total++;
  if (value == null) {
    ctx.missing++;
    if (caveat) ctx.caveats.push(caveat);
    return 50;
  }
  return value;
}

function buildCtx(stats: PlayerStats, height_cm: number | undefined): ScoringCtx {
  const min90 = stats.minutes_played && stats.minutes_played > 0
    ? stats.minutes_played / 90
    : undefined;
  return { s: stats, min90, height: height_cm, caveats: [], missing: 0, total: 0 };
}

function pressIntensity90(ctx: ScoringCtx): number {
  const { s, min90 } = ctx;
  const t = s.tackles;
  const i = s.interceptions;
  if (t == null && i == null) {
    ctx.caveats.push('Press intensity estimated from tackles+interceptions; both missing');
    ctx.missing++;
    ctx.total++;
    return 50;
  }
  ctx.total++;
  const raw = (t ?? 0) + (i ?? 0);
  const per = min90 ? raw / min90 : raw / 30;
  if (t == null || i == null) {
    ctx.caveats.push('Press intensity estimated from tackles+interceptions; one component missing');
  }
  return norm(per, 2, 12);
}

function defActions90(ctx: ScoringCtx): number {
  const { s, min90 } = ctx;
  const t = s.tackles;
  const i = s.interceptions;
  ctx.total++;
  if (t == null && i == null) {
    ctx.missing++;
    return 50;
  }
  const raw = (t ?? 0) + (i ?? 0);
  const per = min90 ? raw / min90 : raw / 30;
  return norm(per, 1, 10);
}

function passAcc(ctx: ScoringCtx): number {
  return norm(use(ctx, ctx.s.pass_accuracy, 'Pass accuracy unavailable'), 60, 95);
}

function keyPasses90(ctx: ScoringCtx): number {
  const v = per90(ctx.s.key_passes, ctx.s.minutes_played);
  return norm(use(ctx, v, 'Key passes unavailable; per-90 estimate skipped'), 0, 3);
}

function xa90(ctx: ScoringCtx): number {
  const v = per90(ctx.s.xa, ctx.s.minutes_played);
  return norm(use(ctx, v, 'xA unavailable'), 0, 0.5);
}

function dribbleRate(ctx: ScoringCtx): number {
  return norm(use(ctx, ctx.s.dribble_success_rate, 'Dribble success rate unavailable'), 30, 80);
}

function dribble90(ctx: ScoringCtx): number {
  const v = per90(ctx.s.dribble_success, ctx.s.minutes_played);
  return norm(use(ctx, v, 'Dribble volume unavailable'), 0, 5);
}

function xg90(ctx: ScoringCtx): number {
  const v = per90(ctx.s.xg, ctx.s.minutes_played);
  return norm(use(ctx, v, 'xG unavailable'), 0, 0.6);
}

function shotAcc(ctx: ScoringCtx): number {
  const { shots, shots_on_target } = ctx.s;
  ctx.total++;
  if (shots == null || shots_on_target == null || shots === 0) {
    ctx.missing++;
    ctx.caveats.push('Shot accuracy unavailable');
    return 50;
  }
  return norm((shots_on_target / shots) * 100, 20, 80);
}

function aerialPct(ctx: ScoringCtx): number {
  return norm(use(ctx, ctx.s.aerial_duel_win_pct, 'Aerial duel win % unavailable'), 30, 75);
}

function tackles90(ctx: ScoringCtx): number {
  const v = per90(ctx.s.tackles, ctx.s.minutes_played);
  return norm(use(ctx, v, 'Tackles unavailable'), 0.5, 6);
}

function interceptions90(ctx: ScoringCtx): number {
  const v = per90(ctx.s.interceptions, ctx.s.minutes_played);
  return norm(use(ctx, v, 'Interceptions unavailable'), 0.3, 5);
}

function heightScore(ctx: ScoringCtx): number {
  ctx.total++;
  if (ctx.height == null) {
    ctx.missing++;
    ctx.caveats.push('Height unavailable; aerial profile estimated from aerial duel win %');
    return 50;
  }
  return norm(ctx.height, 170, 200);
}

function goals90(ctx: ScoringCtx): number {
  const v = per90(ctx.s.goals, ctx.s.minutes_played);
  return norm(use(ctx, v, 'Goals unavailable'), 0, 0.6);
}

function assists90(ctx: ScoringCtx): number {
  const v = per90(ctx.s.assists, ctx.s.minutes_played);
  return norm(use(ctx, v, 'Assists unavailable'), 0, 0.4);
}

function passVolume90(ctx: ScoringCtx): number {
  const v = per90(ctx.s.pass_count, ctx.s.minutes_played);
  return norm(use(ctx, v, 'Pass count unavailable'), 20, 100);
}

const PROFILE_POSITION_MAP: Record<StyleProfileId, string[]> = {
  P01: ['CM', 'CAM', 'FW', 'CF', 'LW', 'RW', 'ST'],
  P02: ['CDM', 'CM'],
  P03: ['CM'],
  P04: ['CM', 'CAM', 'LW', 'RW', 'WG'],
  P05: ['CAM', 'CM'],
  P06: ['ST', 'CF'],
  P07: ['ST'],
  P08: ['CF', 'ST'],
  P09: ['LW', 'RW'],
  P10: ['LW', 'RW', 'LB', 'RB'],
  P11: ['LW', 'RW'],
  P12: ['LB', 'RB'],
  P13: ['LB', 'RB'],
  P14: ['CB'],
  P15: ['CB'],
  P16: ['CB', 'CDM'],
  P17: ['CDM'],
  P18: ['CDM', 'CM'],
  P19: ['GK'],
  P20: ['GK'],
};

function positionMatches(profile: StyleProfileId, position: string): boolean {
  const upper = position.toUpperCase().trim();
  return PROFILE_POSITION_MAP[profile].some(
    (p) => upper === p || upper.includes(p)
  );
}

type Scorer = (ctx: ScoringCtx) => number;

function avg(...vals: number[]): number {
  return vals.reduce((a, b) => a + b, 0) / vals.length;
}

const SCORERS: Record<StyleProfileId, Scorer> = {
  P01: (ctx) => avg(
    pressIntensity90(ctx),
    use(ctx, ctx.s.aerial_duel_win_pct != null ? norm(ctx.s.aerial_duel_win_pct, 30, 65) : undefined, 'Duel win % unavailable for P01'),
    defActions90(ctx)
  ),
  P02: (ctx) => avg(
    passAcc(ctx),
    keyPasses90(ctx),
    passVolume90(ctx)
  ),
  P03: (ctx) => {
    const offScore = avg(goals90(ctx), assists90(ctx), keyPasses90(ctx));
    const defScore = avg(defActions90(ctx), tackles90(ctx));
    const diff = Math.abs(offScore - defScore);
    const balance = clamp(100 - diff);
    return avg(offScore, defScore, balance);
  },
  P04: (ctx) => avg(
    dribbleRate(ctx),
    dribble90(ctx),
    passVolume90(ctx)
  ),
  P05: (ctx) => avg(
    xa90(ctx),
    keyPasses90(ctx),
    passAcc(ctx)
  ),
  P06: (ctx) => avg(
    xg90(ctx),
    shotAcc(ctx),
    goals90(ctx)
  ),
  P07: (ctx) => avg(
    aerialPct(ctx),
    heightScore(ctx),
    defActions90(ctx)
  ),
  P08: (ctx) => avg(
    dribble90(ctx),
    keyPasses90(ctx),
    xa90(ctx)
  ),
  P09: (ctx) => avg(
    dribbleRate(ctx),
    dribble90(ctx),
    shotAcc(ctx)
  ),
  P10: (ctx) => avg(
    xa90(ctx),
    keyPasses90(ctx),
    passAcc(ctx)
  ),
  P11: (ctx) => avg(
    pressIntensity90(ctx),
    defActions90(ctx),
    dribble90(ctx)
  ),
  P12: (ctx) => avg(
    assists90(ctx),
    xa90(ctx),
    passVolume90(ctx)
  ),
  P13: (ctx) => avg(
    dribbleRate(ctx),
    passAcc(ctx),
    passVolume90(ctx)
  ),
  P14: (ctx) => avg(
    passAcc(ctx),
    keyPasses90(ctx),
    passVolume90(ctx)
  ),
  P15: (ctx) => avg(
    aerialPct(ctx),
    tackles90(ctx),
    interceptions90(ctx)
  ),
  P16: (ctx) => avg(
    interceptions90(ctx),
    defActions90(ctx),
    passAcc(ctx)
  ),
  P17: (ctx) => avg(
    interceptions90(ctx),
    tackles90(ctx),
    passAcc(ctx)
  ),
  P18: (ctx) => avg(
    use(ctx, ctx.s.aerial_duel_win_pct != null ? norm(ctx.s.aerial_duel_win_pct, 40, 75) : undefined, 'Duel win % unavailable for P18'),
    pressIntensity90(ctx),
    tackles90(ctx)
  ),
  P19: (ctx) => {
    ctx.caveats.push('GK sweeper actions not available; score estimated from pass accuracy and interceptions');
    return avg(passAcc(ctx), interceptions90(ctx));
  },
  P20: (ctx) => {
    const sotRate: number | undefined =
      ctx.s.shots_on_target != null && ctx.s.shots != null && ctx.s.shots > 0
        ? (ctx.s.shots_on_target / ctx.s.shots) * 100
        : undefined;
    const saveProxy = norm(
      use(ctx, sotRate != null ? 100 - sotRate : undefined, 'Save % unavailable; proxied from shots faced'),
      20, 80
    );
    const xgStopped = per90(ctx.s.xg, ctx.s.minutes_played);
    const stopScore = norm(
      use(ctx, xgStopped != null ? 100 - norm(xgStopped, 0, 0.3) : undefined, 'xGStopped unavailable; estimated from opponent xG proxy'),
      0, 100
    );
    return avg(saveProxy, stopScore);
  },
};

function computeScores(
  input: ClassifyProfileInput,
  candidates: StyleProfileId[]
): { scores: Record<StyleProfileId, number>; caveats: string[] } {
  const allCaveats: string[] = [];
  const scores = Object.fromEntries(
    ALL_PROFILE_IDS.map((id) => [id, 0])
  ) as Record<StyleProfileId, number>;

  for (const id of candidates) {
    const ctx = buildCtx(input.stats, input.height_cm);
    scores[id] = clamp(SCORERS[id](ctx));
    for (const c of ctx.caveats) {
      if (!allCaveats.includes(c)) allCaveats.push(c);
    }
  }

  return { scores, caveats: allCaveats };
}

function measureDataQuality(stats: PlayerStats, height_cm: number | undefined): { available: number; total: number } {
  const fields: (keyof PlayerStats)[] = [
    'goals', 'assists', 'xg', 'npxg', 'xa', 'shots', 'shots_on_target',
    'pass_count', 'pass_accuracy', 'key_passes',
    'dribble_success', 'dribble_success_rate',
    'tackles', 'interceptions', 'aerial_duel_win_pct',
    'appearances', 'minutes_played',
  ];
  const total = fields.length + 1;
  let available = fields.filter((f) => stats[f] != null).length;
  if (height_cm != null) available++;
  return { available, total };
}

function deriveConfidence(
  available: number,
  total: number
): 'high' | 'medium' | 'low' {
  const ratio = available / total;
  if (ratio >= 0.75) return 'high';
  if (ratio >= 0.5) return 'medium';
  return 'low';
}

export function classifyProfile(
  player: ClassifyProfileInput
): ClassifyProfileResult {
  const position = player.position ?? '';

  const candidates = ALL_PROFILE_IDS.filter((id) =>
    positionMatches(id, position)
  );

  const eligible = candidates.length > 0 ? candidates : ALL_PROFILE_IDS;

  const { scores, caveats } = computeScores(
    { ...player, position },
    eligible
  );

  const ranked = [...eligible].sort((a, b) => scores[b] - scores[a]);

  const primary = ranked[0];
  const secondary =
    ranked.length > 1 && scores[ranked[1]] >= scores[primary] - 15
      ? ranked[1]
      : undefined;

  const { available, total } = measureDataQuality(player.stats, player.height_cm);
  const confidence = deriveConfidence(available, total);

  const uniqueCaveats = [...new Set(caveats)];

  return { primary, secondary, scores, confidence, caveats: uniqueCaveats };
}
