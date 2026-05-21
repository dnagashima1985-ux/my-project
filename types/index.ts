// ScoutIQ Type Definitions

export type Plan = 'trial' | 'starter' | 'pro' | 'elite';
export type Language = 'en' | 'ja' | 'nl' | 'fr' | 'es';
export type ReportAudience = 'ceo' | 'sd' | 'coach';
export type InjuryStatus = 'available' | 'doubtful' | 'injured';
export type RiskGrade = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type SignalHeat = 'hot' | 'warm' | 'early';
export type ConfidenceLevel = 'high' | 'medium' | 'low';
export type EQGrade = 'HIGH' | 'MEDIUM' | 'LOW' | 'UNKNOWN';

export type StyleProfileId =
  | 'P01' | 'P02' | 'P03' | 'P04' | 'P05'
  | 'P06' | 'P07' | 'P08' | 'P09' | 'P10'
  | 'P11' | 'P12' | 'P13' | 'P14' | 'P15'
  | 'P16' | 'P17' | 'P18' | 'P19' | 'P20';

export interface User {
  id: string;
  email: string;
  plan: Plan;
  trial_uses_remaining: number;
  trial_features_unlocked: boolean;
  preferred_language: Language;
  stripe_customer_id?: string;
  created_at: string;
}

export interface PlayerStats {
  goals?: number;
  assists?: number;
  xg?: number;
  npxg?: number;
  xa?: number;
  shots?: number;
  shots_on_target?: number;
  pass_count?: number;
  pass_accuracy?: number;
  key_passes?: number;
  dribble_success?: number;
  dribble_success_rate?: number;
  tackles?: number;
  interceptions?: number;
  aerial_duel_win_pct?: number;
  yellow_cards?: number;
  red_cards?: number;
  appearances?: number;
  minutes_played?: number;
}

export interface Player {
  id: string;
  name: string;
  age?: number;
  height_cm?: number;
  nationality?: string;
  preferred_foot?: string;
  current_club?: string;
  league?: string;
  position?: string;
  stats?: PlayerStats;
  source_id?: string;
  last_updated_at: string;
}

export interface PlayerStyleProfile {
  id: string;
  player_id: string;
  primary_profile_id: StyleProfileId;
  secondary_profile_id?: StyleProfileId;
  profile_scores: Record<StyleProfileId, number>;
  confidence_level: ConfidenceLevel;
  data_caveats?: string[];
  key_evidence?: string[];
  last_updated_at: string;
}

export interface InjuryHistory {
  type: string;
  from: string;
  to?: string;
  games_missed: number;
}

export interface PlayerInjury {
  id: string;
  player_id: string;
  status: InjuryStatus;
  current_injury_type?: string;
  current_injury_since?: string;
  return_estimate?: string;
  risk_score: number;
  risk_grade: RiskGrade;
  injury_history: InjuryHistory[];
  total_missed_games: number;
  last_updated_at: string;
}

export interface LeaguePercentile {
  id: string;
  player_id: string;
  league_id: string;
  season: string;
  stat_name: string;
  percentile: number;
}

export interface EQDimension {
  score: number;      // 0-20
  evidence: string[];
  flags: string[];    // unverified claims
}

export interface EQAnalysis {
  id: string;
  player_id: string;
  article_count: number;
  total_score: number;
  grade: EQGrade;
  dimensions: {
    self_awareness: EQDimension;
    self_regulation: EQDimension;
    motivation: EQDimension;
    empathy: EQDimension;
    social_skills: EQDimension;
  };
  verdict: string;
  analysed_at: string;
}

export interface LonglistEntry {
  player_id: string;
  fit_score: number;
}

export interface Longlist {
  id: string;
  user_id: string;
  club_profile_id: string;
  player_ids: LonglistEntry[];
  generated_at: string;
}

export interface ClubProfile {
  id: string;
  user_id: string;
  club_name: string;
  formation?: string;
  style?: string;
  positions: string[];
  style_profiles: StyleProfileId[];
  age_min?: number;
  age_max?: number;
  height_min?: number;
  budget_eur?: number;
  target_leagues: string[];
  created_at: string;
}

export interface ScoutInputs {
  salary_eur?: number;
  transfer_fee_eur?: number;
  negotiation_status?: string;
  competing_clubs?: string[];
  notes?: string;
}

export interface Report {
  id: string;
  user_id: string;
  player_id: string;
  audience: ReportAudience;
  language: Language;
  scout_inputs?: ScoutInputs;
  ai_content?: Record<string, unknown>;
  format: 'pdf' | 'ppt';
  created_at: string;
}

export interface TransferSignal {
  id: string;
  interested_club: string;
  target_player: string;
  target_club: string;
  position: string;
  heat: SignalHeat;
  confidence: string;
  source: string;
  quote: string;
  detected_at: string;
}

export interface PlayerWithDetails extends Player {
  style_profile?: PlayerStyleProfile;
  injury?: PlayerInjury;
  percentiles?: LeaguePercentile[];
  eq?: EQAnalysis;
}
