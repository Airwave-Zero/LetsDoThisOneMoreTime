import os
import pandas as pd
import logging
from datetime import datetime
import glob
import numpy as np
from pathlib import Path
from utils import project_paths
from utils.generic_util import default_filters, calculate_level_from_xp, combat_level_from_xp, check_metric_has_level
import time

gold_parquet_folder_path = project_paths.gold_parquet_folder_path
gold_parquet_analytics_path = project_paths.gold_parquet_analytics_path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

############### HELPER FUNCTIONS ###############

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
    #logging.info(f"Columns: {combined_df.columns.tolist()}")
    return combined_df

############### EXTRACTION METHODS ###############

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
    result_df = skill_df[[
        'player_id', 'username', 'snapshot_ts', 'metric', 'value', 'level',
        'xp_gained', 'level_gained', 'xp_growth_rate'
    ]].copy()
    result_df.rename(columns={'metric': 'skill', 'value': 'total_xp'}, inplace=True)

    logging.info(f"Created {len(result_df)} progression records")
    return result_df


def extract_skill_level_aggregates(df):
    '''
    Extract: Skill-Level Aggregates
    Grain: (skill, date)
    
    Derived fields:
    - avg_xp_per_skill: mean XP across players
    - median_xp: median XP
    - top_1_percent_xp: 99th percentile XP
    - player_count_per_skill: number of players training skill
    - xp_std_dev: standard deviation of XP
    - avg_level: average level across players
    '''
    logging.info("Extracting Skill-Level Aggregates...")
    
    required_cols = ['metric', 'value']
    if not all(col in df.columns for col in required_cols):
        logging.warning("Missing required columns for skill aggregates")
        return pd.DataFrame()
    
    # Filter for skills only
    skill_df = df[df['metric'].isin(default_filters['skill_names'])].copy()
    
    if skill_df.empty:
        logging.warning("No skill data for skill aggregates")
        return pd.DataFrame()
    
    # Vectorized groupby aggregation
    skill_agg = skill_df.groupby('metric')['value'].agg([
        ('avg_xp_per_skill', 'mean'),
        ('median_xp', 'median'),
        ('xp_std_dev', 'std')
    ]).reset_index()
    skill_agg.rename(columns={'metric': 'skill'}, inplace=True)
    
    # Add player count and percentile  
    player_counts = skill_df.groupby('metric')['player_id'].nunique().reset_index()
    player_counts.rename(columns={'metric': 'skill', 'player_id': 'player_count'}, inplace=True)
    skill_agg = skill_agg.merge(player_counts, on='skill', how='left')
    
    p99_xp = skill_df.groupby('metric')['value'].quantile(0.99).reset_index()
    p99_xp.rename(columns={'metric': 'skill', 'value': 'top_1_percent_xp'}, inplace=True)
    skill_agg = skill_agg.merge(p99_xp, on='skill', how='left')
    
    # Add average level if available
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
    
    # Filter for skills only
    skill_df = df[df['metric'].isin(default_filters['skill_names'])].copy()
    
    if skill_df.empty:
        logging.warning("No skill data for leaderboards")
        return pd.DataFrame()
    
    # Vectorized leaderboard extraction
    cols_to_get = ['player_id', 'username', 'value', 'rank', 'metric']
    if 'level' in skill_df.columns:
        cols_to_get.append('level')
   
    # Sort so the best rows per skill come first
    skill_df = skill_df.sort_values(
        by=['metric', 'value'],
        ascending=[True, False]
    )
    # Take top N rows per skill
    result_df = (
        skill_df.groupby('metric', group_keys=False)
        .head(top_n)
        .copy()
    )
    # Keep only desired columns
    result_df = result_df[cols_to_get]

    # Add leaderboard rank within each skill
    result_df['leaderboard_rank'] = result_df.groupby('metric').cumcount() + 1

    # Rename metric -> skill
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
    
    # Filter for skills only
    skill_df = df[df['metric'].isin(default_filters['skill_names'])].copy()
    
    if skill_df.empty:
        logging.warning("No skill data for segmentation")
        return pd.DataFrame()
    
    # Define thresholds
    casual_threshold = 1_000_000      # 1M total XP
    active_threshold = 10_000_000     # 10M total XP
    early_level = 30
    mid_level = 60
    late_level = 85
    combat_skills = ['attack', 'strength', 'defence', 'hitpoints', 'ranged', 'magic']
    
    # Vectorized aggregations per player
    player_agg = skill_df.groupby('player_id').agg({
        'value': 'sum',
        'username': 'first'
    }).reset_index()
    player_agg.rename(columns={'value': 'total_xp'}, inplace=True)
    
    # Calculate average levels
    if 'level' in skill_df.columns:
        level_agg = skill_df[skill_df['level'].notna()].groupby('player_id')['level'].mean().reset_index()
        level_agg.rename(columns={'level': 'avg_level'}, inplace=True)
        player_agg = player_agg.merge(level_agg, on='player_id', how='left')
        player_agg['avg_level'] = player_agg['avg_level'].fillna(0)
    else:
        player_agg['avg_level'] = 0
    
    # Calculate combat XP ratio per player using merge with a combat skill filter
    combat_df = skill_df[skill_df['metric'].isin(combat_skills)].groupby('player_id')['value'].sum().reset_index()
    combat_df.rename(columns={'value': 'combat_xp'}, inplace=True)
    player_agg = player_agg.merge(combat_df, on='player_id', how='left')
    player_agg['combat_xp'] = player_agg['combat_xp'].fillna(0)
    
    # Vectorized player type classification
    combat_ratio = player_agg['combat_xp'] / player_agg['total_xp'].clip(lower=1)
    player_agg['player_type'] = np.select(
        [combat_ratio > 0.6, combat_ratio < 0.4],
        ['combat-focused', 'skiller'],
        default='balanced'
    )
    player_agg['player_type'] = np.where(player_agg['total_xp'] == 0, 'new', player_agg['player_type'])
    
    # Vectorized activity tier classification
    player_agg['activity_tier'] = np.select(
        [player_agg['total_xp'] < casual_threshold, player_agg['total_xp'] < active_threshold],
        ['casual', 'active'],
        default='hardcore'
    )
    
    # Vectorized progress stage classification
    player_agg['progress_stage'] = np.select(
        [player_agg['avg_level'] < early_level, 
         player_agg['avg_level'] < mid_level, 
         player_agg['avg_level'] < late_level],
        ['early', 'mid', 'late'],
        default='endgame'
    )
    
    # Select final columns
    result_df = player_agg[[
        'player_id', 'username', 'player_type', 'activity_tier', 'progress_stage', 'total_xp', 'avg_level'
    ]]
    
    logging.info(f"Segmented {len(result_df)} players")
    return result_df


def extract_skill_efficiency_metrics(df):
    '''
    Extract: Skill Efficiency Metrics (Advanced Gold)
    Grain: (player, skill)
    
    Derived fields:
    - xp_per_level: efficiency metric
    - xp_to_next_level: XP remaining to next level
    - efficiency_percentile: percentile ranking of efficiency
    '''
    logging.info("Extracting Skill Efficiency Metrics...")
    
    required_cols = ['player_id', 'metric', 'value']
    if not all(col in df.columns for col in required_cols):
        logging.warning("Missing required columns for efficiency metrics")
        return pd.DataFrame()
    
    # Filter for skills only
    skill_df = df[df['metric'].isin(default_filters['skill_names'])].copy()
    
    if skill_df.empty:
        logging.warning("No skill data for efficiency metrics")
        return pd.DataFrame()
    
    # Vectorized efficiency calculation
    result_df = skill_df.groupby(['player_id', 'metric']).agg({
        'value': 'first',
        'level': 'first'
    }).reset_index()
    
    # Fill missing levels with 1
    result_df['level'] = result_df['level'].fillna(1).astype(int)
    result_df['level'] = result_df['level'].clip(lower=1)
    
    # Vectorized efficiency calculations
    result_df['xp_per_level'] = result_df['value'] / result_df['level']
    result_df['xp_to_next_level'] = ((result_df['level'] + 1) * result_df['xp_per_level'] - result_df['value']).clip(lower=0)
    
    # Calculate percentile for each skill
    result_df['efficiency_percentile'] = result_df.groupby('metric')['xp_per_level'].rank(pct=True) * 100
    
    # Rename and select columns
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
    
    # Filter for skills only
    skill_df = df[df['metric'].isin(default_filters['skill_names'])].copy()
    
    if skill_df.empty:
        logging.warning("No skill data for wide format")
        return pd.DataFrame()
    
    # Pivot: rows = player_id, columns = skill, values = xp
    wide_xp = skill_df.pivot_table(
        index='player_id',
        columns='metric',
        values='value',
        aggfunc='first'
    ).reset_index()
    
    # Rename columns to include suffix
    wide_xp.columns = [
        col if col == 'player_id' else f"{col}_xp"
        for col in wide_xp.columns
    ]
    
    # Also pivot calculated levels if available
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
    
    # Calculate combat level for each player (vectorized)
    combat_skills = ['attack', 'strength', 'defence', 'hitpoints', 'prayer', 'ranged', 'magic']
    combat_cols = [f"{skill}_xp" for skill in combat_skills if f"{skill}_xp" in wide_xp.columns]
    
    if len(combat_cols) == len(combat_skills):
        # Vectorize combat level calculation with np.vectorize
        combat_level_vec = np.vectorize(combat_level_from_xp)
        
        # Extract XP values as arrays and fill NaN with 0
        combat_xp_arrays = [wide_xp[col].fillna(0).astype(int).values for col in combat_cols]
        
        # Apply vectorized function
        wide_xp['combat_level'] = combat_level_vec(*combat_xp_arrays)
        logging.info("Added combat level calculations to wide format")
    else:
        logging.warning(f"Missing some combat skills for combat level calculation. Found: {combat_cols}")
    
    logging.info(f"Created wide format table with {len(wide_xp)} players")
    return wide_xp


def extract_ranking_change_table(df):
    '''
    Extract: Ranking Change Table (Delta-Based)
    Grain: (player, skill, date)
    
    Requires multiple snapshots over time.
    '''
    logging.info("Extracting Ranking Change Table...")
    
    required_cols = ['player_id', 'metric', 'rank', 'snapshot_ts']
    if not all(col in df.columns for col in required_cols):
        logging.warning("Missing required columns for ranking changes")
        return pd.DataFrame()
    
    # Filter for skills only
    skill_df = df[df['metric'].isin(default_filters['skill_names'])].copy()
    
    if skill_df.empty:
        logging.warning("No skill data for ranking changes")
        return pd.DataFrame()
    
    # Vectorized rank change calculation
    skill_df = skill_df.sort_values(['player_id', 'metric', 'snapshot_ts']).reset_index(drop=True)
    
    # Calculate rank changes using groupby + shift
    skill_df['rank_change'] = skill_df.groupby(['player_id', 'metric'])['rank'].shift(1) - skill_df['rank']
    
    # Remove rows where rank_change is NaN (first occurrence per group)
    result_df = skill_df[skill_df['rank_change'].notna()].copy()
    
    # Select and rename columns
    result_df = result_df[[
        'player_id', 'metric', 'snapshot_ts', 'rank', 'rank_change', 'value', 'level'
    ]].copy()
    result_df.rename(columns={'metric': 'skill', 'value': 'xp'}, inplace=True)
    result_df['rank_change'] = result_df['rank_change'].astype(int)
    logging.info(f"Created {len(result_df)} ranking change records")
    return result_df


############### MAIN ORCHESTRATION ###############

def generate_gold_parquets(input_directory, output_directory):
    '''
    Main orchestration function:
    1. Find and load parquet files
    2. Run all extraction methods
    3. Combine results
    4. Write output parquets
    '''
    logging.info(f"Starting gold layer generation from {input_directory}")
    
    # Ensure output directory exists
    os.makedirs(output_directory, exist_ok=True)
    
    # Step 1: Find and load parquet files
    parquet_files = find_parquet_files(input_directory)
    if not parquet_files:
        logging.error("No parquet files found, exiting")
        return False
    
    #final_df = pd.DataFrame()
    for each_df_name in parquet_files:
        df = pd.read_parquet(each_df_name)
    # df = load_and_concatenate_parquets(parquet_files)
    # if df is None or df.empty:
    #     logging.error("Failed to load parquet files, exiting")
    #     return False
    
        #logging.info(f"Loaded data shape: {df.shape}")
        #logging.info(f"Columns: {df.columns.tolist()}")
    
    # Step 1.5: Calculate levels from XP for all skill rows
        if 'level' not in df.columns:
            logging.info('Levels not yet calculated for snapshots, calculating now.')
            df = add_calculated_levels(df)
        # Step 2: Run extraction methods
        extraction_results = {}
        
        try:
            extraction_results['player_aggregates'] = extract_player_level_aggregates(df)
            extraction_results['player_progression'] = extract_player_progression(df)
            extraction_results['skill_aggregates'] = extract_skill_level_aggregates(df)
            extraction_results['leaderboards'] = extract_leaderboard_snapshots(df)
            extraction_results['player_segmentation'] = extract_player_segmentation(df)
            extraction_results['skill_efficiency'] = extract_skill_efficiency_metrics(df)
            extraction_results['wide_format'] = extract_wide_format_table(df)
            extraction_results['ranking_changes'] = extract_ranking_change_table(df)
        except Exception as e:
            logging.error(f"Error during extraction: {e}", exc_info=True)
            return False
    
        # Step 3: Write output parquets
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for name, result_df in extraction_results.items():
            if result_df.empty:
                logging.warning(f"Skipping {name}: empty dataframe")
                continue
            replaced_filename = os.path.basename(each_df_name).replace('.parquet', '')
            output_file = os.path.join(output_directory, f"gold_{name}_{replaced_filename}_private.parquet")
            
            try:
                result_df.to_parquet(output_file, index=False, engine="pyarrow", compression="snappy")
                logging.info(f"Saved {name}: {output_file} ({len(result_df)} rows)")
            except Exception as e:
                logging.error(f"Failed to save {name}: {e}")
                continue    
    
        # Step 4: Create main wide-format gold table
        logging.info("Creating main gold analytics table...")
        
        if not extraction_results['wide_format'].empty and not extraction_results['player_segmentation'].empty:
            gold_table = extraction_results['wide_format'].merge(
                extraction_results['player_segmentation'][
                    ['player_id', 'username', 'player_type', 'activity_tier', 'progress_stage']
                ],
                on='player_id',
                how='left'
            )
            output_file = os.path.join(output_directory, f"gold_main_players_{timestamp}_private.parquet")
            gold_table.to_parquet(output_file, index=False, engine="pyarrow", compression="snappy")
            logging.info(f"Saved main gold table: {output_file} ({len(gold_table)} rows)") 
    logging.info("Gold layer generation complete!")
    return True

############### MAIN ENTRY POINT ###############

def main():
    # Input directory - the combined backup folder
    input_dir = r"C:\Users\Gabriel\Desktop\LetsDoThisOneMoreTime\Data Pipelines\OSRS Player Behavior\combined 14-57-09-530"
    
    # Output directory for gold parquets
    start_time = time.time()
    print(f"start time:{time.strftime("%Y-%m-%d | %H:%M:%S")}")
    output_dir = gold_parquet_analytics_path
    success = generate_gold_parquets(input_dir, output_dir)
    end_time = time.time()
    elapsed_time = end_time - start_time
    file_write_string = f"{time.strftime("%Y-%m-%d")}: Total time taken: {elapsed_time:.2f} seconds ; {elapsed_time/60:.2f} minutes."
    print(file_write_string)
    if success:
        logging.info("Process completed successfully!")
    else:
        logging.error("Process failed!")
        exit(1)


if __name__ == "__main__":
    main()