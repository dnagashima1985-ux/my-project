-- ScoutIQ Initial Schema (PRD v12.0)

-- Users
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  plan TEXT DEFAULT 'trial', -- trial/starter/pro/elite
  trial_uses_remaining INT DEFAULT 7,
  trial_features_unlocked BOOLEAN DEFAULT true,
  preferred_language TEXT DEFAULT 'en', -- en/ja/nl/fr/es
  stripe_customer_id TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Club profiles (for longlist generation)
CREATE TABLE club_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  club_name TEXT,
  formation TEXT,
  style TEXT,
  positions JSONB,
  style_profiles JSONB, -- P01-P20
  age_min INT,
  age_max INT,
  height_min INT,
  budget_eur INT,
  target_leagues JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Players
CREATE TABLE players (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  age INT,
  height_cm INT,
  nationality TEXT,
  preferred_foot TEXT,
  current_club TEXT,
  league TEXT,
  position TEXT,
  stats JSONB,
  source_id TEXT UNIQUE, -- TheStatsAPI player ID
  last_updated_at TIMESTAMPTZ DEFAULT now()
);

-- Play style profiles
CREATE TABLE player_style_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  player_id UUID REFERENCES players(id) ON DELETE CASCADE,
  primary_profile_id TEXT,   -- P01-P20
  secondary_profile_id TEXT,
  profile_scores JSONB,
  confidence_level TEXT,     -- high/medium/low
  data_caveats JSONB,
  key_evidence JSONB,
  last_updated_at TIMESTAMPTZ DEFAULT now()
);

-- Injuries
CREATE TABLE player_injuries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  player_id UUID REFERENCES players(id) ON DELETE CASCADE,
  status TEXT,               -- available/doubtful/injured
  current_injury_type TEXT,
  current_injury_since DATE,
  return_estimate DATE,
  risk_score INT,            -- 0-100
  risk_grade TEXT,           -- LOW/MEDIUM/HIGH/CRITICAL
  injury_history JSONB,
  total_missed_games INT,
  last_updated_at TIMESTAMPTZ DEFAULT now()
);

-- League percentiles
CREATE TABLE league_percentiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  player_id UUID REFERENCES players(id) ON DELETE CASCADE,
  league_id TEXT,
  season TEXT,
  stat_name TEXT,
  percentile INT             -- 0-100
);

-- EQ analyses
CREATE TABLE eq_analyses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  player_id UUID REFERENCES players(id) ON DELETE CASCADE,
  article_count INT,
  total_score INT,
  grade TEXT,                -- HIGH/MEDIUM/LOW/UNKNOWN
  dimensions JSONB,
  verdict TEXT,
  analysed_at TIMESTAMPTZ DEFAULT now()
);

-- Longlists
CREATE TABLE longlists (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  club_profile_id UUID REFERENCES club_profiles(id),
  player_ids JSONB,          -- [{player_id, fit_score}]
  generated_at TIMESTAMPTZ DEFAULT now()
);

-- Reports
CREATE TABLE reports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  player_id UUID REFERENCES players(id),
  audience TEXT,             -- ceo/sd/coach
  language TEXT DEFAULT 'en',
  scout_inputs JSONB,
  ai_content JSONB,
  format TEXT,               -- pdf/ppt
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Transfer signals (Market Intelligence)
CREATE TABLE transfer_signals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  interested_club TEXT,
  target_player TEXT,
  target_club TEXT,
  position TEXT,
  heat TEXT,                 -- hot/warm/early
  confidence TEXT,           -- confirmed/rumour/speculation
  source TEXT,
  quote TEXT,
  detected_at TIMESTAMPTZ DEFAULT now()
);

-- User clubs (Market Intelligence)
CREATE TABLE user_clubs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  club_name TEXT,
  league TEXT,
  tier TEXT,
  budget_range TEXT,
  style TEXT,
  country TEXT,
  tm_id TEXT
);

-- MI recommendations
CREATE TABLE mi_recommendations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  signal_id UUID REFERENCES transfer_signals(id),
  alt_player_ids JSONB,
  fit_scores JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Shortlists
CREATE TABLE shortlists (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  player_id UUID REFERENCES players(id),
  note TEXT,
  added_at TIMESTAMPTZ DEFAULT now()
);

-- Subscriptions
CREATE TABLE subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  stripe_subscription_id TEXT,
  status TEXT,
  plan TEXT,
  current_period_end TIMESTAMPTZ
);

-- Indexes
CREATE INDEX idx_players_source_id ON players(source_id);
CREATE INDEX idx_players_position ON players(position);
CREATE INDEX idx_players_league ON players(league);
CREATE INDEX idx_league_percentiles_player ON league_percentiles(player_id, league_id, season);
CREATE INDEX idx_longlists_user ON longlists(user_id);
CREATE INDEX idx_shortlists_user ON shortlists(user_id);
CREATE INDEX idx_transfer_signals_heat ON transfer_signals(heat, detected_at DESC);
