import os
import pandas as pd
import logging
import glob
import numpy as np
from utils import project_paths
from utils.generic_util import default_filters, calculate_level_from_xp, combat_level_from_xp
import time

gold_parquet_folder_path = project_paths.gold_parquet_folder_path
gold_parquet_analytics_path = project_paths.gold_parquet_analytics_path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

normalize_cols = ['metric', 'skill', 'boss', 'skill_a', 'skill_b', 'top_skill', 'weakest_skill',
                'top_activity', 'weakest_activity', 'data_category_type', 'data_category_name']
############### HELPER FUNCTIONS ###############

def fix_snapshot_timestamp(df):
    '''
    Fix snapshot_ts column so it is stored as a proper datetime64 type.
    Power BI struggles with ISO 8601 strings (especially trailing "Z" and
    inconsistent millisecond precision).  Converting to datetime64 in the
    parquet source lets Power BI read it as a native DateTime column.
    '''
    if 'snapshot_ts' in df.columns:
        df['snapshot_ts'] = pd.to_datetime(df['snapshot_ts'], utc=True).dt.tz_localize(None)
        logging.info("Fixed snapshot_ts -> datetime64[ns] (timezone-naive UTC)")
    return df


def add_calculated_levels(df):
    '''
    Add level calculations for each row in the dataframe (vectorized).
    For skills (where check_metric_has_level is True), calculate level from XP value.
    '''
    logging.info("Calculating levels from XP values...")

    df = df.copy()

    # Create mask for skills only
    if 'metric' in df.columns:
        skill_mask = df['metric'].isin(default_filters['skill_names'])

        # Vectorize the level calculation using np.vectorize
        calculate_level_vec = np.vectorize(calculate_level_from_xp)

        # Initialize level column
        df['level'] = None

        # Apply vectorized calculation only to skills
        df.loc[skill_mask, 'level'] = calculate_level_vec(
            df.loc[skill_mask, 'value'].astype(int).values
        )

    return df


def find_parquet_files(base_directory):
    '''
    Recursively search for all parquet files in the directory and its month subdirectories.
    Expects structure: base_dir/month_folders/combined_*.parquet
    '''
    parquet_files = []

    # Find all combined_*.parquet files recursively
    pattern = os.path.join(base_directory, "**", "combined_*.parquet")
    parquet_files = sorted(glob.glob(pattern, recursive=True))

    if not parquet_files:
        logging.warning(f"No parquet files found in {base_directory}")
        return []

    logging.info(f"Found {len(parquet_files)} parquet files")
    return parquet_files


def normalize_osrs_names_for_output(df):
    '''
    Normalize OSRS metric and category names in gold layer output (vectorized).
    
    Transforms:
    - metric / skill / boss: attack -> Attack, abyssal_sire -> Abyssal Sire, etc.
    - data_category_name: applies same normalization as metric names
    - data_category_type: group -> Group, leaderboard -> Leaderboard
    
    Does NOT modify: column names, group names (in data), usernames, or any logic.
    Uses snake_case to Title Case conversion via underscore -> space replacement.
    Optimized with vectorized pandas string operations (10-100x faster than apply).
    '''
    if df is None or df.empty:
        return df
    
    df = df.copy()
    
    # Vectorized normalization using pandas string methods (implemented in C/Cython)
    # Much faster than apply() since it operates on entire series at once
    def vectorized_normalize(series):
        '''Apply vectorized string transformations to entire series.'''
        return series.astype(str).str.replace('_', ' ', regex=False).str.title()
    
    # Normalize skill/boss/metric columns (these appear in different tables after renaming)
    for col in normalize_cols:
        if col in df.columns:
            df[col] = vectorized_normalize(df[col])
            logging.debug(f"Normalized column '{col}' in {len(df)} rows")
    return df

def load_and_concatenate_parquets(parquet_files):
    '''
    Load all parquet files and concatenate into a single dataframe.
    '''
    dfs = []

    for file_path in parquet_files:
        try:
            df = pd.read_parquet(file_path)
            dfs.append(df)
            logging.info(f"Loaded {os.path.basename(file_path)} ({len(df)} rows)")
        except Exception as e:
            logging.error(f"Failed to load {file_path}: {e}")
            continue

    if not dfs:
        logging.error("No parquet files were successfully loaded")
        return None

    combined_df = pd.concat(dfs, ignore_index=True)
    logging.info(f"Combined into {len(combined_df)} total rows")
    return combined_df


############### EXTRACTION METHODS — SKILLS & PLAYERS ###############

def extract_player_level_aggregates(df):
    '''
    Extract: Player-Level Aggregates (Core Gold Table) - Vectorized
    Grain: 1 row per player
    '''
    logging.info("Extracting Player-Level Aggregates...")

    required_cols = ['player_id', 'value', 'metric']
    if not all(col in df.columns for col in required_cols):
        logging.warning(f"Missing required columns. Available: {df.columns.tolist()}")
        return pd.DataFrame()

    df = df[df['player_id'].notna()].copy()
    df = df[df["metric"] != "overall"]

    # Vectorized aggregations using groupby
    agg_dict = {
        'value': 'sum',
        'username': 'first',
        'display_name': 'first',
        'rank': 'mean'
    }

    result_df = df.groupby('player_id').agg(agg_dict).reset_index()
    result_df.rename(columns={'value': 'total_xp', 'rank': 'overall_rank'}, inplace=True)

    if 'level' in df.columns:
        level_df = df[df['level'].notna()].copy()

        # Average level per player
        avg_level_df = (
            level_df.groupby('player_id')['level']
            .mean()
            .reset_index(name='avg_level')
        )

        # Count unique skills maxed (level >= 99) per player
        maxed_skills_df = (
            level_df[level_df['level'] >= 99]
            .groupby('player_id')['metric']
            .nunique()
            .reset_index(name='maxed_skills_count')
        )
        # Merge stats
        level_stats = avg_level_df.merge(maxed_skills_df, on='player_id', how='left')
        level_stats['maxed_skills_count'] = level_stats['maxed_skills_count'].fillna(0)

        result_df = result_df.merge(level_stats, on='player_id', how='left')
        result_df[['avg_level', 'maxed_skills_count']] = result_df[['avg_level', 'maxed_skills_count']].fillna(0)
    else:
        result_df['avg_level'] = 0
        result_df['maxed_skills_count'] = 0

    # Find top/weakest skills and activities per player
    skill_mask = df['metric'].isin(default_filters['skill_names'])

    # Top and weakest skills
    skill_df = df[skill_mask].copy()
    if not skill_df.empty:
        top_skills_idx = skill_df.groupby('player_id')['value'].idxmax()
        weakest_skills_idx = skill_df.groupby('player_id')['value'].idxmin()

        top_skills = skill_df.loc[top_skills_idx, ['player_id', 'metric']].rename(columns={'metric': 'top_skill'}).reset_index(drop=True)
        weakest_skills = skill_df.loc[weakest_skills_idx, ['player_id', 'metric']].rename(columns={'metric': 'weakest_skill'}).reset_index(drop=True)

        result_df = result_df.merge(top_skills, on='player_id', how='left')
        result_df = result_df.merge(weakest_skills, on='player_id', how='left')
    else:
        result_df['top_skill'] = 'unknown'
        result_df['weakest_skill'] = 'unknown'

    # Top and weakest activities (non-skills)
    activity_df = df[~skill_mask].copy()
    if not activity_df.empty:
        top_activities_idx = activity_df.groupby('player_id')['value'].idxmax()
        weakest_activities_idx = activity_df.groupby('player_id')['value'].idxmin()

        top_activities = activity_df.loc[top_activities_idx, ['player_id', 'metric']].rename(columns={'metric': 'top_activity'}).reset_index(drop=True)
        weakest_activities = activity_df.loc[weakest_activities_idx, ['player_id', 'metric']].rename(columns={'metric': 'weakest_activity'}).reset_index(drop=True)

        result_df = result_df.merge(top_activities, on='player_id', how='left')
        result_df = result_df.merge(weakest_activities, on='player_id', how='left')
    else:
        result_df['top_activity'] = 'unknown'
        result_df['weakest_activity'] = 'unknown'

    # Fill any missing values
    result_df[['top_skill', 'weakest_skill', 'top_activity', 'weakest_activity']] = \
        result_df[['top_skill', 'weakest_skill', 'top_activity', 'weakest_activity']].fillna('unknown')

    # FIX: Safely assign data_category columns per player (groupby first, then merge)
    if 'data_category_type' in df.columns and 'data_category_name' in df.columns:
        category_df = df.groupby('player_id').agg(
            data_category_type=('data_category_type', 'first'),
            data_category_name=('data_category_name', 'first')
        ).reset_index()
        result_df = result_df.merge(category_df, on='player_id', how='left')
    else:
        result_df['data_category_type'] = 'unknown'
        result_df['data_category_name'] = 'unknown'

    logging.info(f"Created {len(result_df)} player aggregates")
    return result_df


def extract_player_progression(df):
    '''
    Extract: Player Progression (Time-Series Gold) - Vectorized
    Grain: (player_id, snapshot_ts, metric)
    '''
    logging.info("Extracting Player Progression...")

    required_cols = ['player_id', 'value', 'snapshot_ts', 'metric']
    if not all(col in df.columns for col in required_cols):
        logging.warning("Missing required columns for progression")
        return pd.DataFrame()

    skill_df = df[df['metric'].isin(default_filters['skill_names'])].copy()

    if skill_df.empty:
        logging.warning("No skill data available for progression")
        return pd.DataFrame()

    # Vectorized approach: sort and use groupby + shift
    skill_df = skill_df.sort_values(['player_id', 'metric', 'snapshot_ts']).reset_index(drop=True)

    # Calculate deltas using groupby and shift
    skill_df['xp_gained'] = skill_df.groupby(['player_id', 'metric'])['value'].diff().fillna(0)
    skill_df['level_gained'] = skill_df.groupby(['player_id', 'metric'])['level'].diff().fillna(0)

    # Calculate growth rate vectorized
    prev_xp = skill_df.groupby(['player_id', 'metric'])['value'].shift(1)
    skill_df['xp_growth_rate'] = np.where(
        prev_xp > 0,
        (skill_df['xp_gained'] / prev_xp) * 100,
        0
    )

    # Select and rename columns
    cols = [
        'player_id', 'username', 'snapshot_ts', 'metric', 'value', 'level',
        'xp_gained', 'level_gained', 'xp_growth_rate'
    ]
    # Add snapshot_month if it exists
    if 'snapshot_month' in skill_df.columns:
        cols.append('snapshot_month')
    
    result_df = skill_df[cols].copy()
    result_df.rename(columns={'metric': 'skill', 'value': 'total_xp'}, inplace=True)

    logging.info(f"Created {len(result_df)} progression records")
    return result_df


def extract_skill_level_aggregates(df):
    '''
    Extract: Skill-Level Aggregates
    Grain: 1 row per skill
    '''
    logging.info("Extracting Skill-Level Aggregates...")

    required_cols = ['metric', 'value']
    if not all(col in df.columns for col in required_cols):
        logging.warning("Missing required columns for skill aggregates")
        return pd.DataFrame()

    skill_df = df[df['metric'].isin(default_filters['skill_names'])].copy()

    if skill_df.empty:
        logging.warning("No skill data for skill aggregates")
        return pd.DataFrame()

    skill_agg = skill_df.groupby('metric')['value'].agg([
        ('avg_xp_per_skill', 'mean'),
        ('median_xp', 'median'),
        ('xp_std_dev', 'std')
    ]).reset_index()
    skill_agg.rename(columns={'metric': 'skill'}, inplace=True)

    player_counts = skill_df.groupby('metric')['player_id'].nunique().reset_index()
    player_counts.rename(columns={'metric': 'skill', 'player_id': 'player_count'}, inplace=True)
    skill_agg = skill_agg.merge(player_counts, on='skill', how='left')

    p99_xp = skill_df.groupby('metric')['value'].quantile(0.99).reset_index()
    p99_xp.rename(columns={'metric': 'skill', 'value': 'top_1_percent_xp'}, inplace=True)
    skill_agg = skill_agg.merge(p99_xp, on='skill', how='left')

    if 'level' in skill_df.columns:
        level_agg = skill_df[skill_df['level'].notna()].groupby('metric')['level'].mean().reset_index()
        level_agg.rename(columns={'metric': 'skill', 'level': 'avg_level'}, inplace=True)
        skill_agg = skill_agg.merge(level_agg, on='skill', how='left')
        skill_agg['avg_level'] = skill_agg['avg_level'].fillna(0)
    else:
        skill_agg['avg_level'] = 0

    result_df = skill_agg
    logging.info(f"Created {len(result_df)} skill aggregates")
    return result_df


def extract_leaderboard_snapshots(df, top_n=100):
    '''
    Extract: Leaderboard Snapshots (Denormalized Gold)
    Grain: (skill, rank)

    Creates top-N leaderboards per skill.
    '''
    logging.info(f"Extracting Leaderboard Snapshots (top {top_n})...")

    required_cols = ['metric', 'player_id', 'value', 'rank']
    if not all(col in df.columns for col in required_cols):
        logging.warning("Missing required columns for leaderboard")
        return pd.DataFrame()

    skill_df = df[df['metric'].isin(default_filters['skill_names'])].copy()

    if skill_df.empty:
        logging.warning("No skill data for leaderboards")
        return pd.DataFrame()

    cols_to_get = ['player_id', 'username', 'value', 'rank', 'metric']
    if 'level' in skill_df.columns:
        cols_to_get.append('level')

    skill_df = skill_df.sort_values(
        by=['metric', 'value'],
        ascending=[True, False]
    )
    result_df = (
        skill_df.groupby('metric', group_keys=False)
        .head(top_n)
        .copy()
    )
    result_df = result_df[cols_to_get]
    result_df['leaderboard_rank'] = result_df.groupby('metric').cumcount() + 1
    result_df.rename(columns={'metric': 'skill'}, inplace=True)

    logging.info(f"Created leaderboard data for {len(result_df)} entries")
    return result_df


def extract_player_segmentation(df):
    '''
    Extract: Player Segmentation Table - Vectorized
    Grain: player
    '''
    logging.info("Extracting Player Segmentation...")

    required_cols = ['player_id', 'value', 'metric']
    if not all(col in df.columns for col in required_cols):
        logging.warning("Missing required columns for segmentation")
        return pd.DataFrame()

    skill_df = df[df['metric'].isin(default_filters['skill_names'])].copy()

    if skill_df.empty:
        logging.warning("No skill data for segmentation")
        return pd.DataFrame()

    casual_threshold = 1_000_000
    active_threshold = 10_000_000
    early_level = 30
    mid_level = 60
    late_level = 85
    combat_skills = ['attack', 'strength', 'defence', 'hitpoints', 'ranged', 'magic']

    player_agg = skill_df.groupby('player_id').agg({
        'value': 'sum',
        'username': 'first'
    }).reset_index()
    player_agg.rename(columns={'value': 'total_xp'}, inplace=True)

    if 'level' in skill_df.columns:
        level_agg = skill_df[skill_df['level'].notna()].groupby('player_id')['level'].mean().reset_index()
        level_agg.rename(columns={'level': 'avg_level'}, inplace=True)
        player_agg = player_agg.merge(level_agg, on='player_id', how='left')
        player_agg['avg_level'] = player_agg['avg_level'].fillna(0)
    else:
        player_agg['avg_level'] = 0

    combat_df = skill_df[skill_df['metric'].isin(combat_skills)].groupby('player_id')['value'].sum().reset_index()
    combat_df.rename(columns={'value': 'combat_xp'}, inplace=True)
    player_agg = player_agg.merge(combat_df, on='player_id', how='left')
    player_agg['combat_xp'] = player_agg['combat_xp'].fillna(0)

    combat_ratio = player_agg['combat_xp'] / player_agg['total_xp'].clip(lower=1)
    player_agg['player_type'] = np.select(
        [combat_ratio > 0.6, combat_ratio < 0.4],
        ['combat-focused', 'skiller'],
        default='balanced'
    )
    player_agg['player_type'] = np.where(player_agg['total_xp'] == 0, 'new', player_agg['player_type'])

    player_agg['activity_tier'] = np.select(
        [player_agg['total_xp'] < casual_threshold, player_agg['total_xp'] < active_threshold],
        ['casual', 'active'],
        default='hardcore'
    )

    player_agg['progress_stage'] = np.select(
        [player_agg['avg_level'] < early_level,
         player_agg['avg_level'] < mid_level,
         player_agg['avg_level'] < late_level],
        ['early', 'mid', 'late'],
        default='endgame'
    )

    result_df = player_agg[[
        'player_id', 'username', 'player_type', 'activity_tier', 'progress_stage', 'total_xp', 'avg_level'
    ]]

    logging.info(f"Segmented {len(result_df)} players")
    return result_df


def extract_skill_efficiency_metrics(df):
    '''
    Extract: Skill Efficiency Metrics (Advanced Gold)
    Grain: (player, skill)
    '''
    logging.info("Extracting Skill Efficiency Metrics...")

    required_cols = ['player_id', 'metric', 'value']
    if not all(col in df.columns for col in required_cols):
        logging.warning("Missing required columns for efficiency metrics")
        return pd.DataFrame()

    skill_df = df[df['metric'].isin(default_filters['skill_names'])].copy()

    if skill_df.empty:
        logging.warning("No skill data for efficiency metrics")
        return pd.DataFrame()

    result_df = skill_df.groupby(['player_id', 'metric']).agg({
        'value': 'first',
        'level': 'first'
    }).reset_index()

    result_df['level'] = result_df['level'].fillna(1).astype(int)
    result_df['level'] = result_df['level'].clip(lower=1)

    result_df['xp_per_level'] = result_df['value'] / result_df['level']
    result_df['xp_to_next_level'] = ((result_df['level'] + 1) * result_df['xp_per_level'] - result_df['value']).clip(lower=0)

    result_df['efficiency_percentile'] = result_df.groupby('metric')['xp_per_level'].rank(pct=True) * 100

    result_df = result_df.rename(columns={'metric': 'skill', 'value': 'xp'})[
        ['player_id', 'skill', 'xp', 'level', 'xp_per_level', 'xp_to_next_level', 'efficiency_percentile']
    ]

    logging.info(f"Created efficiency metrics for {len(result_df)} skill-player combinations")
    return result_df


def extract_wide_format_table(df):
    '''
    Extract: Wide Table (Pivoted Format)
    Grain: player

    Converts long format to wide format for ML/BI.
    Includes combat level calculation for each player.
    '''
    logging.info("Extracting Wide Format Table...")

    required_cols = ['player_id', 'metric', 'value']
    if not all(col in df.columns for col in required_cols):
        logging.warning("Missing required columns for wide format")
        return pd.DataFrame()

    skill_df = df[df['metric'].isin(default_filters['skill_names'])].copy()

    if skill_df.empty:
        logging.warning("No skill data for wide format")
        return pd.DataFrame()

    wide_xp = skill_df.pivot_table(
        index='player_id',
        columns='metric',
        values='value',
        aggfunc='first'
    ).reset_index()

    wide_xp.columns = [
        col if col == 'player_id' else f"{col}_xp"
        for col in wide_xp.columns
    ]

    if 'level' in skill_df.columns:
        wide_level = skill_df.pivot_table(
            index='player_id',
            columns='metric',
            values='level',
            aggfunc='first'
        ).reset_index()

        wide_level.columns = [
            col if col == 'player_id' else f"{col}_level"
            for col in wide_level.columns
        ]

        wide_xp = wide_xp.merge(wide_level, on='player_id', how='left')

    combat_skills = ['attack', 'strength', 'defence', 'hitpoints', 'prayer', 'ranged', 'magic']
    combat_cols = [f"{skill}_xp" for skill in combat_skills if f"{skill}_xp" in wide_xp.columns]

    if len(combat_cols) == len(combat_skills):
        combat_level_vec = np.vectorize(combat_level_from_xp)
        combat_xp_arrays = [wide_xp[col].fillna(0).astype(int).values for col in combat_cols]
        wide_xp['combat_level'] = combat_level_vec(*combat_xp_arrays)
        logging.info("Added combat level calculations to wide format")
    else:
        logging.warning(f"Missing some combat skills for combat level calculation. Found: {combat_cols}")

    logging.info(f"Created wide format table with {len(wide_xp)} players")
    return wide_xp


def extract_ranking_change_table(df):
    '''
    Extract: Ranking Change Table (Delta-Based)
    Grain: (player, skill, snapshot_ts)
    '''
    logging.info("Extracting Ranking Change Table...")

    required_cols = ['player_id', 'metric', 'rank', 'snapshot_ts']
    if not all(col in df.columns for col in required_cols):
        logging.warning("Missing required columns for ranking changes")
        return pd.DataFrame()

    skill_df = df[df['metric'].isin(default_filters['skill_names'])].copy()

    if skill_df.empty:
        logging.warning("No skill data for ranking changes")
        return pd.DataFrame()

    skill_df = skill_df.sort_values(['player_id', 'metric', 'snapshot_ts']).reset_index(drop=True)
    skill_df['rank_change'] = skill_df.groupby(['player_id', 'metric'])['rank'].shift(1) - skill_df['rank']

    result_df = skill_df[skill_df['rank_change'].notna()].copy()
    
    cols = ['player_id', 'metric', 'snapshot_ts', 'rank', 'rank_change', 'value', 'level']
    # Add snapshot_month if it exists
    if 'snapshot_month' in skill_df.columns:
        cols.append('snapshot_month')
    
    result_df = result_df[cols].copy()
    result_df.rename(columns={'metric': 'skill', 'value': 'xp'}, inplace=True)
    result_df['rank_change'] = result_df['rank_change'].astype(int)
    logging.info(f"Created {len(result_df)} ranking change records")
    return result_df


############### EXTRACTION METHODS — BOSSES & ACTIVITIES ###############

def extract_boss_aggregates(df):
    '''
    Extract: Boss / Activity Aggregates
    Grain: 1 row per boss/activity metric
    '''
    logging.info("Extracting Boss Aggregates...")

    required_cols = ['player_id', 'metric', 'value']
    if not all(col in df.columns for col in required_cols):
        logging.warning("Missing required columns for boss aggregates")
        return pd.DataFrame()

    boss_df = df[~df['metric'].isin(default_filters['skill_names'])].copy()
    boss_df = boss_df[boss_df['metric'] != 'overall']

    if boss_df.empty:
        logging.warning("No boss/activity data for boss aggregates")
        return pd.DataFrame()

    boss_agg = boss_df.groupby('metric')['value'].agg([
        ('avg_kills', 'mean'),
        ('median_kills', 'median'),
        ('kill_std_dev', 'std'),
        ('max_kills', 'max')
    ]).reset_index()
    boss_agg.rename(columns={'metric': 'boss'}, inplace=True)

    player_counts = boss_df.groupby('metric')['player_id'].nunique().reset_index()
    player_counts.columns = ['boss', 'player_count']
    boss_agg = boss_agg.merge(player_counts, on='boss', how='left')

    p99 = boss_df.groupby('metric')['value'].quantile(0.99).reset_index()
    p99.columns = ['boss', 'p99_kills']
    boss_agg = boss_agg.merge(p99, on='boss', how='left')

    logging.info(f"Created {len(boss_agg)} boss aggregates")
    return boss_agg


def extract_player_boss_profile(df):
    '''
    Extract: Player Boss Profile
    Grain: (player_id, boss)
    '''
    logging.info("Extracting Player Boss Profile...")

    required_cols = ['player_id', 'metric', 'value', 'rank']
    if not all(col in df.columns for col in required_cols):
        logging.warning("Missing required columns for player boss profile")
        return pd.DataFrame()

    boss_df = df[~df['metric'].isin(default_filters['skill_names'])].copy()
    boss_df = boss_df[boss_df['metric'] != 'overall']

    if boss_df.empty:
        logging.warning("No boss/activity data for player boss profile")
        return pd.DataFrame()

    result_df = boss_df.sort_values('snapshot_ts', ascending=False).groupby(
        ['player_id', 'metric']
    ).agg(
        kills=('value', 'first'),
        rank=('rank', 'first'),
        username=('username', 'first')
    ).reset_index()
    result_df.rename(columns={'metric': 'boss'}, inplace=True)

    result_df['kill_percentile'] = result_df.groupby('boss')['kills'].rank(pct=True) * 100

    logging.info(f"Created {len(result_df)} player-boss profile records")
    return result_df


def extract_boss_progression(df):
    '''
    Extract: Boss / Activity Progression (Time-Series)
    Grain: (player_id, boss, snapshot_ts)
    '''
    logging.info("Extracting Boss Progression...")

    required_cols = ['player_id', 'value', 'snapshot_ts', 'metric']
    if not all(col in df.columns for col in required_cols):
        logging.warning("Missing required columns for boss progression")
        return pd.DataFrame()

    boss_df = df[~df['metric'].isin(default_filters['skill_names'])].copy()
    boss_df = boss_df[boss_df['metric'] != 'overall']

    if boss_df.empty:
        logging.warning("No boss/activity data for boss progression")
        return pd.DataFrame()

    boss_df = boss_df.sort_values(['player_id', 'metric', 'snapshot_ts']).reset_index(drop=True)

    boss_df['kills_gained'] = boss_df.groupby(['player_id', 'metric'])['value'].diff().fillna(0)

    prev_kills = boss_df.groupby(['player_id', 'metric'])['value'].shift(1)
    boss_df['kill_growth_rate'] = np.where(
        prev_kills > 0,
        (boss_df['kills_gained'] / prev_kills) * 100,
        0
    )

    cols = [
        'player_id', 'username', 'snapshot_ts', 'metric', 'value',
        'kills_gained', 'kill_growth_rate'
    ]
    # Add snapshot_month if it exists
    if 'snapshot_month' in boss_df.columns:
        cols.append('snapshot_month')
    
    result_df = boss_df[cols].copy()
    result_df.rename(columns={'metric': 'boss', 'value': 'total_kills'}, inplace=True)

    logging.info(f"Created {len(result_df)} boss progression records")
    return result_df


############### EXTRACTION METHODS — COHORT & CROSS-CUTTING ###############

def extract_cohort_comparison(df):
    '''
    Extract: Cohort / Group Comparison Analytics
    Grain: (data_category_type, data_category_name, metric)
    '''
    logging.info("Extracting Cohort Comparison...")

    required_cols = ['data_category_type', 'data_category_name', 'metric', 'value', 'player_id']
    if not all(col in df.columns for col in required_cols):
        logging.warning("Missing required columns for cohort comparison")
        return pd.DataFrame()

    work_df = df[df['metric'] != 'overall'].copy()

    if work_df.empty:
        logging.warning("No data for cohort comparison")
        return pd.DataFrame()

    agg_dict = {
        'value': ['mean', 'median', 'std', 'max'],
        'player_id': 'nunique'
    }

    cohort_agg = work_df.groupby(
        ['data_category_type', 'data_category_name', 'metric']
    ).agg(agg_dict).reset_index()

    cohort_agg.columns = [
        'data_category_type', 'data_category_name', 'metric',
        'avg_value', 'median_value', 'value_std_dev', 'max_value', 'player_count'
    ]

    if 'level' in work_df.columns:
        level_agg = (
            work_df[work_df['level'].notna()]
            .groupby(['data_category_type', 'data_category_name', 'metric'])['level']
            .mean()
            .reset_index(name='avg_level')
        )
        cohort_agg = cohort_agg.merge(
            level_agg,
            on=['data_category_type', 'data_category_name', 'metric'],
            how='left'
        )
        cohort_agg['avg_level'] = cohort_agg['avg_level'].fillna(0)
    else:
        cohort_agg['avg_level'] = 0

    logging.info(f"Created {len(cohort_agg)} cohort comparison records")
    return cohort_agg


def extract_cohort_segmentation_distribution(df, segmentation_df):
    '''
    Extract: Cohort Segmentation Distribution
    Grain: (data_category_type, data_category_name, segment_type, segment_value)
    '''
    logging.info("Extracting Cohort Segmentation Distribution...")

    if segmentation_df is None or segmentation_df.empty:
        logging.warning("Segmentation data is empty; skipping cohort segmentation distribution")
        return pd.DataFrame()

    required_cols_df = ['player_id', 'data_category_type', 'data_category_name']
    if not all(col in df.columns for col in required_cols_df):
        logging.warning("Missing cohort columns in source data")
        return pd.DataFrame()

    cohort_info = df.groupby('player_id').agg(
        data_category_type=('data_category_type', 'first'),
        data_category_name=('data_category_name', 'first')
    ).reset_index()

    merged = segmentation_df.merge(cohort_info, on='player_id', how='left')

    segment_cols = ['player_type', 'activity_tier', 'progress_stage']
    available_segment_cols = [c for c in segment_cols if c in merged.columns]

    if not available_segment_cols:
        logging.warning("No segment columns found in segmentation data")
        return pd.DataFrame()

    melted = merged.melt(
        id_vars=['player_id', 'data_category_type', 'data_category_name'],
        value_vars=available_segment_cols,
        var_name='segment_type',
        value_name='segment_value'
    )

    result_df = (
        melted.groupby(['data_category_type', 'data_category_name', 'segment_type', 'segment_value'])
        .agg(player_count=('player_id', 'nunique'))
        .reset_index()
    )

    totals = result_df.groupby(
        ['data_category_type', 'data_category_name', 'segment_type']
    )['player_count'].transform('sum')
    result_df['pct_of_cohort'] = np.where(totals > 0, (result_df['player_count'] / totals) * 100, 0)

    logging.info(f"Created {len(result_df)} cohort segmentation distribution records")
    return result_df


def extract_player_activity(df):
    '''
    Extract: Player Activity / Retention Signals
    Grain: 1 row per player
    '''
    logging.info("Extracting Player Activity...")

    required_cols = ['player_id', 'snapshot_ts']
    if not all(col in df.columns for col in required_cols):
        logging.warning("Missing required columns for player activity")
        return pd.DataFrame()

    ts_df = df.copy()
    ts_df['snapshot_ts'] = pd.to_datetime(ts_df['snapshot_ts'])

    activity = ts_df.groupby('player_id').agg(
        first_seen=('snapshot_ts', 'min'),
        last_seen=('snapshot_ts', 'max'),
        total_snapshots=('snapshot_ts', 'nunique'),
        username=('username', 'first')
    ).reset_index()

    activity['days_active'] = (activity['last_seen'] - activity['first_seen']).dt.days

    activity['avg_days_between_snapshots'] = np.where(
        activity['total_snapshots'] > 1,
        activity['days_active'] / (activity['total_snapshots'] - 1),
        0
    )

    max_snapshot = ts_df['snapshot_ts'].max()
    cutoff = max_snapshot - pd.Timedelta(days=30)
    activity['is_active_30d'] = activity['last_seen'] >= cutoff

    if 'data_category_type' in df.columns and 'data_category_name' in df.columns:
        cohort_info = df.groupby('player_id').agg(
            data_category_type=('data_category_type', 'first'),
            data_category_name=('data_category_name', 'first')
        ).reset_index()
        activity = activity.merge(cohort_info, on='player_id', how='left')

    logging.info(f"Created {len(activity)} player activity records")
    return activity


def extract_milestones(df):
    '''
    Extract: Milestone / Achievement Tracking
    Grain: (player_id, skill, milestone_type)
    '''
    logging.info("Extracting Milestones...")

    required_cols = ['player_id', 'metric', 'snapshot_ts']
    if not all(col in df.columns for col in required_cols):
        logging.warning("Missing required columns for milestones")
        return pd.DataFrame()

    if 'level' not in df.columns:
        logging.warning("Level column not available; skipping milestones")
        return pd.DataFrame()

    skill_df = df[df['metric'].isin(default_filters['skill_names'])].copy()
    skill_df = skill_df[skill_df['level'].notna()].copy()

    if skill_df.empty:
        logging.warning("No skill-level data for milestones")
        return pd.DataFrame()

    maxed = skill_df[skill_df['level'] >= 99].copy()
    if not maxed.empty:
        maxed = maxed.sort_values('snapshot_ts')
        first_99 = maxed.groupby(['player_id', 'metric']).agg(
            milestone_snapshot_ts=('snapshot_ts', 'first'),
            username=('username', 'first')
        ).reset_index()
        first_99['milestone_type'] = 'level_99'
        first_99.rename(columns={'metric': 'skill'}, inplace=True)
    else:
        first_99 = pd.DataFrame()

    if not maxed.empty:
        num_skills = len(default_filters['skill_names'])
        maxed_per_player = (
            maxed.groupby('player_id')['metric'].nunique().reset_index(name='skills_maxed')
        )
        fully_maxed_players = maxed_per_player[maxed_per_player['skills_maxed'] == num_skills]['player_id']
        if not fully_maxed_players.empty:
            last_99 = (
                maxed[maxed['player_id'].isin(fully_maxed_players)]
                .sort_values('snapshot_ts')
                .groupby(['player_id', 'metric'])
                .agg(milestone_snapshot_ts=('snapshot_ts', 'first'))
                .reset_index()
            )
            maxed_account = (
                last_99.groupby('player_id')
                .agg(milestone_snapshot_ts=('milestone_snapshot_ts', 'max'))
                .reset_index()
            )
            maxed_account['skill'] = 'all_skills'
            maxed_account['milestone_type'] = 'maxed_account'
            maxed_account = maxed_account.merge(
                df.groupby('player_id')['username'].first().reset_index(),
                on='player_id', how='left'
            )
        else:
            maxed_account = pd.DataFrame()
    else:
        maxed_account = pd.DataFrame()

    frames = [f for f in [first_99, maxed_account] if not f.empty]
    if frames:
        result_df = pd.concat(frames, ignore_index=True)
        result_df = result_df[['player_id', 'username', 'skill', 'milestone_type', 'milestone_snapshot_ts']]
    else:
        result_df = pd.DataFrame()

    logging.info(f"Created {len(result_df)} milestone records")
    return result_df


def extract_skill_correlations(wide_df):
    '''
    Extract: Skill Correlation Matrix
    Grain: (skill_a, skill_b)
    '''
    logging.info("Extracting Skill Correlations...")

    if wide_df is None or wide_df.empty:
        logging.warning("Wide format data is empty; skipping skill correlations")
        return pd.DataFrame()

    xp_cols = [c for c in wide_df.columns if c.endswith('_xp')]

    if len(xp_cols) < 2:
        logging.warning("Not enough skill XP columns for correlation analysis")
        return pd.DataFrame()

    corr_matrix = wide_df[xp_cols].corr()

    clean_names = {c: c.replace('_xp', '') for c in xp_cols}
    corr_matrix = corr_matrix.rename(index=clean_names, columns=clean_names)

    corr_matrix = corr_matrix.reset_index().rename(columns={'index': 'skill_a'})
    result_df = corr_matrix.melt(id_vars='skill_a', var_name='skill_b', value_name='correlation')

    logging.info(f"Created {len(result_df)} skill correlation pairs")
    return result_df

def extract_anomaly_detection(progression_df, boss_progression_df=None):
    '''
    Extract: Anomaly / Botting Detection (Skills + Bosses)
    Grain: rows from progression that are flagged
    '''
    logging.info("Extracting Anomaly Detection...")

    results = []

    # ================================================================
    # SKILL ANOMALY DETECTION
    # ================================================================
    if progression_df is not None and not progression_df.empty:
        skill_required = ['player_id', 'skill', 'xp_gained']
        if all(col in progression_df.columns for col in skill_required):
            logging.info("Running skill anomaly detection...")
            sdf = progression_df.copy()

            # --- Flag 1: Statistical outliers per skill ---
            skill_stats = sdf.groupby('skill')['xp_gained'].agg(['mean', 'std']).reset_index()
            skill_stats.columns = ['skill', 'skill_mean', 'skill_std']
            skill_stats['skill_std'] = skill_stats['skill_std'].fillna(0)

            sdf = sdf.merge(skill_stats, on='skill', how='left')
            sdf['anomaly_threshold'] = sdf['skill_mean'] + 3 * sdf['skill_std']
            sdf['is_anomaly'] = sdf['xp_gained'] > sdf['anomaly_threshold']

            # --- Flag 2: Suspiciously uniform gains (bot-like) ---
            nonzero_sdf = sdf[sdf['xp_gained'] > 0].copy()
            player_skill_stats = nonzero_sdf.groupby(['player_id', 'skill']).agg(
                gain_std=('xp_gained', 'std'),
                gain_count=('xp_gained', 'count'),
                total_gain=('xp_gained', 'sum')
            ).reset_index()
            player_skill_stats['gain_std'] = player_skill_stats['gain_std'].fillna(0)

            suspicious = player_skill_stats[
                (player_skill_stats['gain_std'] < 1) &
                (player_skill_stats['gain_count'] > 5) &
                (player_skill_stats['total_gain'] > 100)
            ][['player_id', 'skill']].copy()
            suspicious['is_suspicious_uniform'] = True

            sdf = sdf.merge(suspicious, on=['player_id', 'skill'], how='left')
            sdf['is_suspicious_uniform'] = sdf['is_suspicious_uniform'].fillna(False)

            flagged_skills = sdf[sdf['is_anomaly'] | sdf['is_suspicious_uniform']].copy()

            # Normalize columns for combined output
            skill_result = flagged_skills.rename(columns={
                'skill': 'metric',
                'total_xp': 'metric_total',
                'xp_gained': 'gained',
                'skill_mean': 'metric_mean',
                'skill_std': 'metric_std'
            })
            skill_result['detection_type'] = 'skill'

            cols = [
                'player_id', 'username', 'snapshot_ts',
                'detection_type', 'metric', 'metric_total',
                'gained', 'metric_mean', 'metric_std', 'anomaly_threshold',
                'is_anomaly', 'is_suspicious_uniform'
            ]
            # Add snapshot_month if it exists
            if 'snapshot_month' in skill_result.columns:
                cols.append('snapshot_month')
            
            skill_result = skill_result[cols].copy()

            results.append(skill_result)
            logging.info(f"Skill anomalies: {len(skill_result)} flagged "
                         f"({skill_result['is_anomaly'].sum()} anomalies, "
                         f"{skill_result['is_suspicious_uniform'].sum()} suspicious uniform)")
        else:
            logging.warning("Missing required columns for skill anomaly detection")
    else:
        logging.warning("Skill progression data is empty; skipping skill anomaly detection")

    # ================================================================
    # BOSS / ACTIVITY ANOMALY DETECTION
    # ================================================================
    if boss_progression_df is not None and not boss_progression_df.empty:
        boss_required = ['player_id', 'boss', 'kills_gained']
        if all(col in boss_progression_df.columns for col in boss_required):
            logging.info("Running boss anomaly detection...")
            bdf = boss_progression_df.copy()

            # --- Flag 1: Statistical outliers per boss ---
            boss_stats = bdf.groupby('boss')['kills_gained'].agg(['mean', 'std']).reset_index()
            boss_stats.columns = ['boss', 'boss_mean', 'boss_std']
            boss_stats['boss_std'] = boss_stats['boss_std'].fillna(0)

            bdf = bdf.merge(boss_stats, on='boss', how='left')
            bdf['anomaly_threshold'] = bdf['boss_mean'] + 3 * bdf['boss_std']
            bdf['is_anomaly'] = bdf['kills_gained'] > bdf['anomaly_threshold']

            # --- Flag 2: Suspiciously uniform kills (bot-like) ---
            nonzero_bdf = bdf[bdf['kills_gained'] > 0].copy()
            player_boss_stats = nonzero_bdf.groupby(['player_id', 'boss']).agg(
                gain_std=('kills_gained', 'std'),
                gain_count=('kills_gained', 'count'),
                total_gain=('kills_gained', 'sum')
            ).reset_index()
            player_boss_stats['gain_std'] = player_boss_stats['gain_std'].fillna(0)

            suspicious_boss = player_boss_stats[
                (player_boss_stats['gain_std'] < 1) &
                (player_boss_stats['gain_count'] > 5) &
                (player_boss_stats['total_gain'] > 5)
            ][['player_id', 'boss']].copy()
            suspicious_boss['is_suspicious_uniform'] = True

            bdf = bdf.merge(suspicious_boss, on=['player_id', 'boss'], how='left')
            bdf['is_suspicious_uniform'] = bdf['is_suspicious_uniform'].fillna(False)

            flagged_bosses = bdf[bdf['is_anomaly'] | bdf['is_suspicious_uniform']].copy()

            # Normalize columns for combined output
            boss_result = flagged_bosses.rename(columns={
                'boss': 'metric',
                'total_kills': 'metric_total',
                'kills_gained': 'gained',
                'boss_mean': 'metric_mean',
                'boss_std': 'metric_std'
            })
            boss_result['detection_type'] = 'boss'

            cols = [
                'player_id', 'username', 'snapshot_ts',
                'detection_type', 'metric', 'metric_total',
                'gained', 'metric_mean', 'metric_std', 'anomaly_threshold',
                'is_anomaly', 'is_suspicious_uniform'
            ]
            # Add snapshot_month if it exists
            if 'snapshot_month' in boss_result.columns:
                cols.append('snapshot_month')
            
            boss_result = boss_result[cols].copy()

            results.append(boss_result)
            logging.info(f"Boss anomalies: {len(boss_result)} flagged "
                         f"({boss_result['is_anomaly'].sum()} anomalies, "
                         f"{boss_result['is_suspicious_uniform'].sum()} suspicious uniform)")
        else:
            logging.warning("Missing required columns for boss anomaly detection")
    else:
        logging.info("No boss progression data provided; skipping boss anomaly detection")

    # ================================================================
    # COMBINE RESULTS
    # ================================================================
    if not results:
        logging.warning("No anomalies detected from either source")
        return pd.DataFrame()

    combined = pd.concat(results, ignore_index=True)
    logging.info(f"Total combined anomalies: {len(combined)} "
                 f"(skills: {(combined['detection_type'] == 'skill').sum()}, "
                 f"bosses: {(combined['detection_type'] == 'boss').sum()})")
    return combined

############### GOLD CONSOLIDATION HELPERS ###############
# These functions merge intermediate extraction results into the final
# consumer-facing gold tables.  The philosophy: one table per business
# grain, NOT one table per metric.

def _build_gold_players(intermediates):
    '''
    Consolidate all per-player data into a single wide gold table.

    Merges:
    - wide_format          (skill xp + levels + combat_level)
    - player_aggregates    (total_xp, ranks, top/weakest, cohort info)
    - player_segmentation  (player_type, activity_tier, progress_stage)
    - player_activity      (first_seen, last_seen, retention signals)
    - milestones           (pivoted: has_any_99, first_99_date, etc.)

    Grain: 1 row per player_id
    '''
    logging.info("Building gold_players_core...")

    wide = intermediates.get('wide_format')
    if wide is None or wide.empty:
        logging.warning("wide_format is empty; cannot build gold_players_core")
        return pd.DataFrame()

    gold = wide.copy()

    # --- Player aggregates ---
    agg = intermediates.get('player_aggregates')
    if agg is not None and not agg.empty:
        desired = [
            'player_id', 'username', 'display_name', 'total_xp', 'avg_level',
            'maxed_skills_count', 'overall_rank', 'top_skill', 'weakest_skill',
            'top_activity', 'weakest_activity', 'data_category_type', 'data_category_name'
        ]
        cols = [c for c in desired if c in agg.columns]
        gold = gold.merge(agg[cols], on='player_id', how='left')

    # --- Player segmentation ---
    seg = intermediates.get('player_segmentation')
    if seg is not None and not seg.empty:
        seg_cols = ['player_id', 'player_type', 'activity_tier', 'progress_stage']
        seg_cols = [c for c in seg_cols if c in seg.columns]
        gold = gold.merge(seg[seg_cols], on='player_id', how='left')

    # --- Player activity / retention ---
    act = intermediates.get('player_activity')
    if act is not None and not act.empty:
        act_cols = [
            'player_id', 'first_seen', 'last_seen', 'total_snapshots',
            'days_active', 'avg_days_between_snapshots', 'is_active_30d'
        ]
        act_cols = [c for c in act_cols if c in act.columns]
        gold = gold.merge(act[act_cols], on='player_id', how='left')

    # --- Milestones (pivot into player-level flags) ---
    ms = intermediates.get('milestones')
    if ms is not None and not ms.empty:
        # First level-99 date per player
        lvl99 = ms[ms['milestone_type'] == 'level_99']
        if not lvl99.empty:
            first_99 = lvl99.groupby('player_id')['milestone_snapshot_ts'].min().reset_index()
            first_99.columns = ['player_id', 'first_99_date']
            first_99['has_any_99'] = True
            gold = gold.merge(first_99, on='player_id', how='left')
        else:
            gold['first_99_date'] = pd.NaT
            gold['has_any_99'] = False

        # Maxed-account date
        maxed = ms[ms['milestone_type'] == 'maxed_account']
        if not maxed.empty:
            ma = maxed.groupby('player_id')['milestone_snapshot_ts'].first().reset_index()
            ma.columns = ['player_id', 'maxed_account_date']
            ma['has_maxed_account'] = True
            gold = gold.merge(ma, on='player_id', how='left')
        else:
            gold['maxed_account_date'] = pd.NaT
            gold['has_maxed_account'] = False
    else:
        gold['first_99_date'] = pd.NaT
        gold['has_any_99'] = False
        gold['maxed_account_date'] = pd.NaT
        gold['has_maxed_account'] = False

    # Fill boolean defaults
    gold['has_any_99'] = gold['has_any_99'].fillna(False)
    gold['has_maxed_account'] = gold['has_maxed_account'].fillna(False)

    logging.info(f"gold_players_core: {len(gold)} players, {len(gold.columns)} columns")
    return gold


def _build_gold_skill_progression(intermediates):
    '''
    Consolidate all skill time-series into one fact table.

    Merges:
    - player_progression   (xp_gained, level_gained, xp_growth_rate)
    - ranking_changes      (rank, rank_change)

    Adds temporal rollup helper columns (date, week_start, month)
    so Power BI can aggregate without needing separate daily/weekly/monthly tables.

    Grain: player_id x skill x snapshot_ts
    '''
    logging.info("Building gold_skill_progression...")

    prog = intermediates.get('player_progression')
    if prog is None or prog.empty:
        logging.warning("player_progression is empty; cannot build gold_skill_progression")
        return pd.DataFrame()

    gold = prog.copy()

    # --- Merge rank changes ---
    rc = intermediates.get('ranking_changes')
    if rc is not None and not rc.empty:
        rc_cols = ['player_id', 'skill', 'snapshot_ts', 'rank', 'rank_change']
        rc_cols = [c for c in rc_cols if c in rc.columns]
        gold = gold.merge(rc[rc_cols], on=['player_id', 'skill', 'snapshot_ts'], how='left')

    # --- Add temporal rollup columns (fully vectorized, no .apply) ---
    ts = pd.to_datetime(gold['snapshot_ts'])
    gold['date'] = ts.dt.normalize()
    gold['week_start'] = (ts - pd.to_timedelta(ts.dt.weekday, unit='D')).dt.normalize()
    gold['month'] = ts.dt.to_period('M').dt.start_time

    logging.info(f"gold_skill_progression: {len(gold)} rows, {len(gold.columns)} columns")
    return gold


def _build_gold_boss_progression(intermediates):
    '''
    Consolidate all boss/activity time-series into one fact table.

    Merges:
    - boss_progression      (kills_gained, kill_growth_rate)
    - player_boss_profile   (kill_percentile)

    Adds temporal rollup helper columns.

    Grain: player_id x boss x snapshot_ts
    '''
    logging.info("Building gold_boss_progression...")

    bp = intermediates.get('boss_progression')
    if bp is None or bp.empty:
        logging.warning("boss_progression is empty; cannot build gold_boss_progression")
        return pd.DataFrame()

    gold = bp.copy()

    # --- Merge boss profile percentile ---
    profile = intermediates.get('player_boss_profile')
    if profile is not None and not profile.empty:
        profile_cols = ['player_id', 'boss', 'kill_percentile']
        profile_cols = [c for c in profile_cols if c in profile.columns]
        gold = gold.merge(profile[profile_cols], on=['player_id', 'boss'], how='left')

    # --- Temporal rollup columns ---
    ts = pd.to_datetime(gold['snapshot_ts'])
    gold['date'] = ts.dt.normalize()
    gold['week_start'] = (ts - pd.to_timedelta(ts.dt.weekday, unit='D')).dt.normalize()
    gold['month'] = ts.dt.to_period('M').dt.start_time

    logging.info(f"gold_boss_progression: {len(gold)} rows, {len(gold.columns)} columns")
    return gold


def _build_gold_skills_reference(intermediates):
    '''
    Consolidate skill-level reference / distribution data.

    Merges:
    - skill_aggregates     (avg_xp, median, p99, std, player_count, avg_level)
    - skill_efficiency     (aggregated to skill level: avg xp_per_level, median)

    Grain: 1 row per skill
    '''
    logging.info("Building gold_skills_reference...")

    sa = intermediates.get('skill_aggregates')
    if sa is None or sa.empty:
        logging.warning("skill_aggregates is empty; cannot build gold_skills_reference")
        return pd.DataFrame()

    gold = sa.copy()

    # --- Aggregate efficiency metrics from player x skill to skill level ---
    eff = intermediates.get('skill_efficiency')
    if eff is not None and not eff.empty:
        eff_agg = eff.groupby('skill').agg(
            avg_xp_per_level=('xp_per_level', 'mean'),
            median_xp_per_level=('xp_per_level', 'median'),
            avg_efficiency_percentile=('efficiency_percentile', 'mean')
        ).reset_index()
        gold = gold.merge(eff_agg, on='skill', how='left')

    logging.info(f"gold_skills_reference: {len(gold)} skills, {len(gold.columns)} columns")
    return gold


def _build_gold_bosses_reference(intermediates):
    '''
    Boss-level reference / distribution data.

    Grain: 1 row per boss
    '''
    logging.info("Building gold_bosses_reference...")

    ba = intermediates.get('boss_aggregates')
    if ba is None or ba.empty:
        logging.warning("boss_aggregates is empty; cannot build gold_bosses_reference")
        return pd.DataFrame()

    logging.info(f"gold_bosses_reference: {len(ba)} bosses, {len(ba.columns)} columns")
    return ba.copy()


def _build_gold_cohort_analytics(intermediates):
    '''
    Consolidate cohort comparison + segmentation distribution.

    Merges:
    - cohort_comparison               (avg/median/std/max per cohort x metric)
    - cohort_segmentation_dist        (pivoted into pct columns per cohort)

    Grain: data_category_type x data_category_name x metric
    '''
    logging.info("Building gold_cohort_analytics...")

    cc = intermediates.get('cohort_comparison')
    if cc is None or cc.empty:
        logging.warning("cohort_comparison is empty; cannot build gold_cohort_analytics")
        return pd.DataFrame()

    gold = cc.copy()

    # --- Pivot segmentation distribution into wide columns per cohort ---
    csd = intermediates.get('cohort_segmentation_dist')
    if csd is not None and not csd.empty:
        try:
            pivot = csd.pivot_table(
                index=['data_category_type', 'data_category_name'],
                columns=['segment_type', 'segment_value'],
                values='pct_of_cohort',
                aggfunc='first'
            ).reset_index()

            # Flatten multi-level columns
            new_cols = []
            for col in pivot.columns:
                if isinstance(col, tuple) and col[1] != '':
                    new_cols.append(f"pct_{col[0]}_{col[1]}")
                else:
                    new_cols.append(col if isinstance(col, str) else col[0])
            pivot.columns = new_cols

            gold = gold.merge(
                pivot,
                on=['data_category_type', 'data_category_name'],
                how='left'
            )
        except Exception as e:
            logging.warning(f"Could not pivot cohort segmentation distribution: {e}")

    logging.info(f"gold_cohort_analytics: {len(gold)} rows, {len(gold.columns)} columns")
    return gold


############### MAIN ORCHESTRATION ###############

def generate_gold_parquets(input_directory, output_directory):
    '''
    Main orchestration function — Consolidated Gold Layer.

    Produces 8 combined gold parquets (1 file per aggregation type, all date partitions combined):

    1. gold_players_core_combined            1 row / player (wide + agg + seg + activity + milestones)
    2. gold_skill_progression_combined       player x skill x snapshot (deltas + rank + temporal cols)
    3. gold_boss_progression_combined        player x boss x snapshot (deltas + percentile + temporal cols)
    4. gold_skills_reference_combined        1 row / skill (distributions + efficiency)
    5. gold_bosses_reference_combined        1 row / boss (distributions)
    6. gold_cohort_analytics_combined        cohort x metric (comparison + segmentation %)
    7. gold_skill_correlations_combined      skill_a x skill_b (Pearson correlation matrix)
    8. gold_anomalies_combined               flagged rows only (sparse)
    '''
    logging.info(f"Starting gold layer generation from {input_directory}")

    # Ensure output directory exists
    os.makedirs(output_directory, exist_ok=True)

    # Step 1: Find parquet files
    parquet_files = find_parquet_files(input_directory)
    if not parquet_files:
        logging.error("No parquet files found, exiting")
        return False

    # Step 1.5: Load and combine all parquet files first
    logging.info(f"Loading and combining {len(parquet_files)} parquet files...")
    all_dfs = []
    for each_df_name in parquet_files:
        df = pd.read_parquet(each_df_name)
        df = fix_snapshot_timestamp(df)
        if 'level' not in df.columns:
            logging.info(f'Calculating levels for {os.path.basename(each_df_name)}')
            df = add_calculated_levels(df)
        
        # Extract month from directory path (e.g., "2026-03" -> March 1, 2026)
        try:
            # Get parent directory name (e.g., "2026-03")
            parent_dir = os.path.basename(os.path.dirname(each_df_name))
            # Try to parse YYYY-MM format
            if len(parent_dir) >= 7 and parent_dir[4] == '-':
                month_str = parent_dir[:7]  # "2026-03"
                snapshot_month = pd.to_datetime(month_str, format='%Y-%m').normalize()
                df['snapshot_month'] = snapshot_month
                logging.info(f"Added snapshot_month: {snapshot_month.date()} for {os.path.basename(each_df_name)}")
            else:
                logging.warning(f"Could not extract month from directory: {parent_dir}, using earliest snapshot_ts")
                if 'snapshot_ts' in df.columns:
                    df['snapshot_month'] = pd.to_datetime(df['snapshot_ts']).dt.to_period('M').dt.start_time
                else:
                    df['snapshot_month'] = pd.NaT
        except Exception as e:
            logging.warning(f"Error extracting month from {each_df_name}: {e}")
            if 'snapshot_ts' in df.columns:
                df['snapshot_month'] = pd.to_datetime(df['snapshot_ts']).dt.to_period('M').dt.start_time
            else:
                df['snapshot_month'] = pd.NaT
        
        all_dfs.append(df)
        logging.info(f"Loaded {os.path.basename(each_df_name)} ({len(df)} rows)")
    
    # Concatenate all dataframes
    combined_df = pd.concat(all_dfs, ignore_index=True)
    logging.info(f"Combined all files into single dataframe ({len(combined_df)} total rows)")
    
    # Ensure snapshot_month is in datetime64 format for Power BI
    if 'snapshot_month' in combined_df.columns:
        combined_df['snapshot_month'] = pd.to_datetime(combined_df['snapshot_month']).dt.tz_localize(None)
        logging.info(f"snapshot_month column added in datetime64 format")

    # =================================================================
    # Step 2: Compute intermediate extraction results on combined data
    # =================================================================
    intermediates = {}

    try:
        # -- Per-player slices --
        intermediates['player_aggregates'] = extract_player_level_aggregates(combined_df)
        intermediates['player_segmentation'] = extract_player_segmentation(combined_df)
        intermediates['player_activity'] = extract_player_activity(combined_df)
        intermediates['wide_format'] = extract_wide_format_table(combined_df)
        intermediates['milestones'] = extract_milestones(combined_df)

        # -- Skill time-series --
        intermediates['player_progression'] = extract_player_progression(combined_df)
        intermediates['ranking_changes'] = extract_ranking_change_table(combined_df)

        # -- Boss time-series --
        intermediates['boss_progression'] = extract_boss_progression(combined_df)
        intermediates['player_boss_profile'] = extract_player_boss_profile(combined_df)

        # -- Reference / Distribution --
        intermediates['skill_aggregates'] = extract_skill_level_aggregates(combined_df)
        intermediates['skill_efficiency'] = extract_skill_efficiency_metrics(combined_df)
        intermediates['boss_aggregates'] = extract_boss_aggregates(combined_df)

        # -- Cohort --
        intermediates['cohort_comparison'] = extract_cohort_comparison(combined_df)
        intermediates['cohort_segmentation_dist'] = extract_cohort_segmentation_distribution(
            combined_df, intermediates['player_segmentation']
        )

        # -- Cross-cutting (depend on intermediates above) --
        intermediates['skill_correlations'] = extract_skill_correlations(
            intermediates['wide_format']
        )
        intermediates['anomaly_detection'] = extract_anomaly_detection(
            intermediates['player_progression'], intermediates['boss_progression']
        )

    except Exception as e:
        logging.error(f"Error during extraction: {e}", exc_info=True)
        return False

    # =================================================================
    # Step 3: Build consolidated gold tables
    # =================================================================
    gold_outputs = {}

    gold_outputs['gold_players_core_combined'] = _build_gold_players(intermediates)
    gold_outputs['gold_skill_progression_combined'] = _build_gold_skill_progression(intermediates)
    gold_outputs['gold_boss_progression_combined'] = _build_gold_boss_progression(intermediates)
    gold_outputs['gold_skills_reference_combined'] = _build_gold_skills_reference(intermediates)
    gold_outputs['gold_bosses_reference_combined'] = _build_gold_bosses_reference(intermediates)
    gold_outputs['gold_cohort_analytics_combined'] = _build_gold_cohort_analytics(intermediates)

    # Pass-through tables (already at final grain, no merge needed)
    gold_outputs['gold_skill_correlations_combined'] = intermediates.get('skill_correlations', pd.DataFrame())
    gold_outputs['gold_anomalies_combined'] = intermediates.get('anomaly_detection', pd.DataFrame())

    # =================================================================
    # Step 3.5: Normalize OSRS names for output
    # =================================================================
    for name, result_df in gold_outputs.items():
        if result_df is not None and not result_df.empty:
            gold_outputs[name] = normalize_osrs_names_for_output(result_df)

    # =================================================================
    # Step 4: Write combined gold parquets
    # =================================================================
    written_count = 0

    for name, result_df in gold_outputs.items():
        if result_df is None or result_df.empty:
            logging.warning(f"Skipping {name}: empty dataframe")
            continue
        output_file = os.path.join(output_directory, f"{name}_private.parquet")

        try:
            result_df.to_parquet(output_file, index=False, engine="pyarrow", compression="snappy")
            logging.info(f"Saved {name}: {output_file} ({len(result_df)} rows, {len(result_df.columns)} cols)")
            written_count += 1
        except Exception as e:
            logging.error(f"Failed to save {name}: {e}")
            continue

    logging.info(f"Wrote {written_count} combined gold parquets")
    logging.info("Gold layer generation complete!")
    return True


############### MAIN ENTRY POINT ###############

def main():
    # Input directory - the combined backup folder
    input_dir = r"C:\Users\Gabriel\Desktop\LetsDoThisOneMoreTime\Data Pipelines\OSRS Player Behavior\combined 14-57-09-530"

    # Output directory for gold parquets
    start_time = time.time()
    print(f"start time:{time.strftime('%Y-%m-%d | %H:%M:%S')}")
    output_dir = gold_parquet_analytics_path
    success = generate_gold_parquets(input_dir, output_dir)
    end_time = time.time()
    elapsed_time = end_time - start_time
    file_write_string = f"{time.strftime('%Y-%m-%d')}: Total time taken: {elapsed_time:.2f} seconds ; {elapsed_time/60:.2f} minutes."
    print(file_write_string)
    if success:
        logging.info("Process completed successfully!")
    else:
        logging.error("Process failed!")
        exit(1)


if __name__ == "__main__":
    main()
