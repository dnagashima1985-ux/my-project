import Anthropic from '@anthropic-ai/sdk';
import type { Language, ClubProfile, PlayerWithDetails, ReportAudience } from '@/types';

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY!,
});

const LANGUAGE_INSTRUCTION = (lang: Language) => `
LANGUAGE INSTRUCTION:
Generate ALL text output in ${lang === 'ja' ? 'Japanese' : lang === 'nl' ? 'Dutch' : lang === 'fr' ? 'French' : lang === 'es' ? 'Spanish' : 'English'}.
If Japanese: Use professional scouting terminology in Japanese.
Keep player names, club names, and profile IDs (P01-P20) in their original form.
Numbers and statistics remain unchanged.
`;

export async function generateLonglist(
  clubProfile: ClubProfile,
  players: PlayerWithDetails[],
  language: Language = 'en'
): Promise<{ player_id: string; fit_score: number; reasoning: string }[]> {
  const prompt = `${LANGUAGE_INSTRUCTION(language)}

You are a professional football scout AI. Generate a ranked longlist for the following club.

CLUB PROFILE:
${JSON.stringify(clubProfile, null, 2)}

AVAILABLE PLAYERS (top candidates):
${JSON.stringify(players.slice(0, 100), null, 2)}

For each suitable player, provide:
1. player_id (UUID)
2. fit_score (0-100, integer)
3. reasoning (2-3 sentences in the selected language)

Return a JSON array of the top 20 best fits. Only use player_ids from the provided list.
Format: [{"player_id": "...", "fit_score": 85, "reasoning": "..."}]

IMPORTANT: Only use provided data. Never invent statistics.`;

  const response = await anthropic.messages.create({
    model: 'claude-sonnet-4-6',
    max_tokens: 4096,
    messages: [{ role: 'user', content: prompt }],
  });

  const content = response.content[0];
  if (content.type !== 'text') throw new Error('Unexpected response type');

  const jsonMatch = content.text.match(/\[[\s\S]*\]/);
  if (!jsonMatch) throw new Error('No JSON array found in response');

  return JSON.parse(jsonMatch[0]);
}

export async function generateReport(
  player: PlayerWithDetails,
  audience: ReportAudience,
  language: Language,
  scoutInputs?: Record<string, unknown>
): Promise<Record<string, string>> {
  const prompt = `${LANGUAGE_INSTRUCTION(language)}

You are a professional football scout. Generate a ${audience === 'ceo' ? 'CEO/Owner' : audience === 'sd' ? 'Sports Director' : 'Manager/Coach'} report for:

PLAYER: ${JSON.stringify(player, null, 2)}
SCOUT INPUTS: ${JSON.stringify(scoutInputs ?? {}, null, 2)}

${audience === 'ceo' ? `CEO REPORT includes:
- Executive summary (investment perspective)
- Injury risk summary and negotiation implications
- EQ assessment summary
- Market positioning
RULE: Only use provided financial figures. Never invent transfer fees or salary numbers.` : ''}

${audience === 'sd' ? `SPORTS DIRECTOR REPORT includes:
- Tactical analysis and fit assessment
- Percentile rankings interpretation
- Similar players comparison
- Profile classification with confidence level
- Injury timeline implications` : ''}

${audience === 'coach' ? `COACH REPORT includes:
- Tactical role suitability (◎○△×)
- Strengths and weaknesses
- Tactical fit in formation
- Pressure stability and team adaptation (EQ)
- 3-4 paragraphs tactical scout note` : ''}

Return a JSON object with section keys and content values in the selected language.`;

  const response = await anthropic.messages.create({
    model: 'claude-sonnet-4-6',
    max_tokens: 4096,
    messages: [{ role: 'user', content: prompt }],
  });

  const content = response.content[0];
  if (content.type !== 'text') throw new Error('Unexpected response type');

  const jsonMatch = content.text.match(/\{[\s\S]*\}/);
  if (!jsonMatch) throw new Error('No JSON object found in response');

  return JSON.parse(jsonMatch[0]);
}

export async function analyzeEQ(
  playerName: string,
  articles: { title: string; date: string; source: string; url: string; content: string }[]
): Promise<{
  total_score: number;
  dimensions: Record<string, { score: number; evidence: string[]; flags: string[] }>;
  verdict: string;
}> {
  if (articles.length < 5) {
    throw new Error('Insufficient data — minimum 5 articles required');
  }

  const prompt = `You are analyzing the emotional intelligence (EQ) of a professional footballer.

PLAYER: ${playerName}

ARTICLES (${articles.length} total):
${JSON.stringify(articles, null, 2)}

Score each of the 5 EQ dimensions (0-20 each):
1. self_awareness: Takes responsibility vs deflects blame
2. self_regulation: No suspensions, calm vs red cards, controversies
3. motivation: Growth mindset vs passive/complaining
4. empathy: Positive teammate mentions vs criticises team
5. social_skills: Leadership, mediator vs dressing room issues

Rules:
- Unverified/single-source claims: include in flags array, DO NOT add to score
- Each evidence item MUST start with the article URL followed by " | ", then title, date, source, and explanation
- Format: "https://... | article title (date, source) — explanation"
- If the article has no URL, omit the URL prefix entirely
- If evidence is ambiguous, score conservatively

Return JSON:
{
  "total_score": <sum of 5 dimensions>,
  "dimensions": {
    "self_awareness": {"score": 0-20, "evidence": ["https://... | article title (date, source) — explanation"], "flags": []},
    "self_regulation": {"score": 0-20, "evidence": [], "flags": []},
    "motivation": {"score": 0-20, "evidence": [], "flags": []},
    "empathy": {"score": 0-20, "evidence": [], "flags": []},
    "social_skills": {"score": 0-20, "evidence": [], "flags": []}
  },
  "verdict": "2-3 sentence summary"
}`;

  const response = await anthropic.messages.create({
    model: 'claude-sonnet-4-6',
    max_tokens: 2048,
    messages: [{ role: 'user', content: prompt }],
  });

  const content = response.content[0];
  if (content.type !== 'text') throw new Error('Unexpected response type');

  const jsonMatch = content.text.match(/\{[\s\S]*\}/);
  if (!jsonMatch) throw new Error('No JSON object found in response');

  return JSON.parse(jsonMatch[0]);
}

export async function extractTransferSignals(
  articles: { title: string; date: string; source: string; content: string }[],
  userClub: string
): Promise<unknown[]> {
  const prompt = `Extract transfer signals from these articles for a scout at ${userClub}.

ARTICLES:
${JSON.stringify(articles, null, 2)}

For each transfer signal found, extract:
- interested_club: which club is tracking
- target_player: player name
- target_club: player's current club
- position: player's position
- heat: "hot" (3+ clubs) | "warm" (1-2 clubs) | "early" (initial mention)
- confidence: "confirmed" | "rumour" | "speculation"
- source: article source
- quote: most relevant quote

Return JSON array. If no signals found, return [].`;

  const response = await anthropic.messages.create({
    model: 'claude-sonnet-4-6',
    max_tokens: 2048,
    messages: [{ role: 'user', content: prompt }],
  });

  const content = response.content[0];
  if (content.type !== 'text') throw new Error('Unexpected response type');

  const jsonMatch = content.text.match(/\[[\s\S]*\]/);
  if (!jsonMatch) return [];

  return JSON.parse(jsonMatch[0]);
}
