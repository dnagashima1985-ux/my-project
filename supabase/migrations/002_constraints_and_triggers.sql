-- Unique constraints for upserts

-- Percentiles: one row per player/league/season/stat
ALTER TABLE league_percentiles
  ADD CONSTRAINT uq_league_percentiles
  UNIQUE (player_id, league_id, season, stat_name);

-- Style profiles: one row per player
ALTER TABLE player_style_profiles
  ADD CONSTRAINT uq_player_style_profiles
  UNIQUE (player_id);

-- Injuries: one row per player
ALTER TABLE player_injuries
  ADD CONSTRAINT uq_player_injuries
  UNIQUE (player_id);

-- EQ: one row per player
ALTER TABLE eq_analyses
  ADD CONSTRAINT uq_eq_analyses
  UNIQUE (player_id);

-- Shortlists: one entry per user+player
ALTER TABLE shortlists
  ADD CONSTRAINT uq_shortlists
  UNIQUE (user_id, player_id);

-- Subscriptions: one per stripe subscription id
ALTER TABLE subscriptions
  ADD CONSTRAINT uq_subscriptions
  UNIQUE (stripe_subscription_id);

-- Auto-create user profile on Supabase Auth signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  INSERT INTO public.users (id, email, plan, trial_uses_remaining, trial_features_unlocked, preferred_language)
  VALUES (
    NEW.id,
    NEW.email,
    'trial',
    7,
    true,
    'en'
  )
  ON CONFLICT (id) DO NOTHING;
  RETURN NEW;
END;
$$;

-- Drop trigger if exists to allow re-runs
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- RLS (Row Level Security) policies
ALTER TABLE users               ENABLE ROW LEVEL SECURITY;
ALTER TABLE club_profiles       ENABLE ROW LEVEL SECURITY;
ALTER TABLE longlists           ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports             ENABLE ROW LEVEL SECURITY;
ALTER TABLE shortlists          ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_clubs          ENABLE ROW LEVEL SECURITY;
ALTER TABLE mi_recommendations  ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions       ENABLE ROW LEVEL SECURITY;

-- Users can only read/update their own row
CREATE POLICY "users: own row" ON users
  FOR ALL USING (auth.uid() = id);

-- Club profiles: own rows only
CREATE POLICY "club_profiles: own" ON club_profiles
  FOR ALL USING (auth.uid() = user_id);

-- Longlists: own rows only
CREATE POLICY "longlists: own" ON longlists
  FOR ALL USING (auth.uid() = user_id);

-- Reports: own rows only
CREATE POLICY "reports: own" ON reports
  FOR ALL USING (auth.uid() = user_id);

-- Shortlists: own rows only
CREATE POLICY "shortlists: own" ON shortlists
  FOR ALL USING (auth.uid() = user_id);

-- User clubs: own rows only
CREATE POLICY "user_clubs: own" ON user_clubs
  FOR ALL USING (auth.uid() = user_id);

-- MI recommendations: own rows only
CREATE POLICY "mi_recommendations: own" ON mi_recommendations
  FOR ALL USING (auth.uid() = user_id);

-- Subscriptions: own rows only
CREATE POLICY "subscriptions: own" ON subscriptions
  FOR ALL USING (auth.uid() = user_id);

-- Players, style profiles, injuries, percentiles, EQ: read-only for authenticated users
ALTER TABLE players              ENABLE ROW LEVEL SECURITY;
ALTER TABLE player_style_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE player_injuries      ENABLE ROW LEVEL SECURITY;
ALTER TABLE league_percentiles   ENABLE ROW LEVEL SECURITY;
ALTER TABLE eq_analyses          ENABLE ROW LEVEL SECURITY;
ALTER TABLE transfer_signals     ENABLE ROW LEVEL SECURITY;

CREATE POLICY "players: read authenticated"           ON players              FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "player_style_profiles: read auth"      ON player_style_profiles FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "player_injuries: read auth"            ON player_injuries       FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "league_percentiles: read auth"         ON league_percentiles    FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "eq_analyses: read auth"                ON eq_analyses           FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "transfer_signals: read auth"           ON transfer_signals      FOR SELECT USING (auth.role() = 'authenticated');
