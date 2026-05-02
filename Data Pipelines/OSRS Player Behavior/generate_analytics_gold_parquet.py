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

# Column name mappings
COLUMN_MAPPING = {
    'timestamp': 'snapshot_ts',
    'player': 'player_id',
    'skill': 'data_category_name',
}

############### HELPER FUNCTIONS ###############

def add_calculated_levels(df):
    # Only operate on relevant rows
    mask = df['metric'].apply(check_metric_has_level)

    # Convert XP → level in a vectorized way
    df.loc[mask, 'level'] = df.loc[mask, 'value'].astype(int).apply(calculate_level_from_xp)

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
    Extract: Player-Level Aggregates (Core Gold Table)
    Grain: 1 row per player (latest snapshot assumed)
    
    Derived fields:
    - total_xp: sum of all skill XP
    - avg_level: mean level across skills
    - maxed_skills_count: count of skills at 99+ (assuming maxed at 99)
    - top_skill: skill with highest XP
    - weakest_skill: skill with lowest XP
    - top_activity: activity with highest #
    - weakest_activity: acitivty with lowest #
    - overall_rank: player's overall rank (if available)
    '''
    logging.info("Extracting Player-Level Aggregates...")
    
    # Validate required columns
    required_cols = ['player_id', 'value', 'data_category_name']
    if not all(col in df.columns for col in required_cols):
        logging.warning(f"Missing required columns. Available: {df.columns.tolist()}")
        return pd.DataFrame()
    
    aggregates = []
    df = df[df['player_id'].notna()]
    df = df[df["metric"] != "overall"] # drop overall rows b/c they mess with data as its already an aggregation

    for player_id in df['player_id'].unique():
        player_data = df[df['player_id'] == player_id]
        if player_data.empty:
            continue
        first_row = player_data.iloc[0]
        total_xp = player_data['value'].sum()
        
        # Get average level and maxed count from calculated levels
        if 'level' in df.columns:
            level_data = player_data[player_data['level'].notna()]
            avg_level = level_data['level'].mean() if not level_data.empty else 0
            maxed_count = len(level_data[level_data['level'] >= 99])
            rank_data = player_data[player_data['rank'].notna()]
            avg_rank = rank_data['rank'].mean() if not rank_data.empty else 0
        else:
            avg_level = 0
            maxed_count = 0
            avg_rank = 0
        
        # Find top and weakest skills

        # Only operate on relevant rows
        mask = df['metric'].apply(check_metric_has_level)
        # Convert XP → level in a vectorized way
        #df.loc[mask, 'level'] = df.loc[mask, 'value'].astype(int).apply(calculate_level_from_xp)
        top_skill = 'unknown'
        weakest_skill = 'unknown'
        top_activity = 'unknown'
        weakest_activity = 'unknown'

        if not player_data.empty:
            player_data_skills = player_data.loc[mask, 'value']
            if not player_data_skills.empty:
                top_skill_idx = player_data_skills.idxmax()
                weakest_skill_idx = player_data_skills.idxmin()
                top_skill = player_data.loc[top_skill_idx, 'metric']
                weakest_skill = player_data.loc[weakest_skill_idx, 'metric']

            player_data_activities = player_data.loc[~mask, 'value']
            if not player_data_activities.empty:
                top_activity_idx = player_data_activities.idxmax()
                weakest_activity_idx = player_data_activities.idxmin()
                top_activity = player_data.loc[top_activity_idx, 'metric']
                weakest_activity = player_data.loc[weakest_activity_idx, 'metric']
        
        agg_row = {
            'player_id': player_id,
            'username': first_row['username'] if 'username' in df.columns else 'unknown',
            'display_name': first_row['display_name'] if 'display_name' in df.columns else 'unknown',
            'total_xp': total_xp,
            'avg_level': avg_level,
            'maxed_skills_count': maxed_count,
            'top_skill': top_skill,
            'weakest_skill': weakest_skill,
            'top_activity': top_activity,
            'weakest_activity': weakest_activity,
            'overall_rank': avg_rank,
            #'snapshot_date': first_row['snapshot_ts'] if 'snapshot_ts' in df.columns else None
        }
        #print(agg_row)
        aggregates.append(agg_row)
    
    result_df = pd.DataFrame(aggregates)
    logging.info(f"Created {len(result_df)} player aggregates")
    return result_df


def extract_player_progression(df):
    logging.info("Extracting Player Progression...")

    required_cols = ['player_id', 'value', 'snapshot_ts', 'metric']
    if not all(col in df.columns for col in required_cols):
        logging.warning("Missing required columns for progression")
        return pd.DataFrame()

    skill_df = df[df['metric'].isin(default_filters['skill_names'])].copy()

    if skill_df.empty:
        logging.warning("No skill data available for progression")
        return pd.DataFrame()

    progression = []

    # group by player AND skill
    for (player_id, skill), group in skill_df.groupby(['player_id', 'metric']):
        group = group.sort_values('snapshot_ts').reset_index(drop=True)

        for idx in range(len(group)):
            row = group.iloc[idx]

            xp_gained = 0
            level_gained = 0
            xp_growth_rate = 0

            if idx > 0:
                prev_row = group.iloc[idx - 1]

                xp_gained = row['value'] - prev_row['value']

                if 'level' in row and pd.notna(row['level']) and pd.notna(prev_row.get('level')):
                    level_gained = row['level'] - prev_row['level']

                if prev_row['value'] > 0:
                    xp_growth_rate = (xp_gained / prev_row['value']) * 100

            progression.append({
                'player_id': player_id,
                'username': row.get('username', 'unknown'),
                'snapshot_ts': row['snapshot_ts'],
                'skill': skill,
                'total_xp': row['value'],
                'level': row.get('level'),
                'xp_gained': xp_gained,
                'level_gained': level_gained,
                'xp_growth_rate': xp_growth_rate
            })

    result_df = pd.DataFrame(progression)
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
    
    skill_aggregates = []
    
    for skill in skill_df['metric'].unique():
        skill_data = skill_df[skill_df['metric'] == skill]
        
        avg_xp = skill_data['value'].mean()
        median_xp = skill_data['value'].median()
        p99_xp = skill_data['value'].quantile(0.99)
        player_count = skill_data['player_id'].nunique()
        std_xp = skill_data['value'].std()
        #snapshot_date = skill_data['snapshot_ts']
        
        avg_level = 0
        if 'level' in skill_data.columns:
            level_data = skill_data[skill_data['level'].notna()]
            avg_level = level_data['level'].mean() if not level_data.empty else 0
        
        skill_row = {
            'skill': skill,
            'avg_xp_per_skill': avg_xp,
            'median_xp': median_xp,
            'top_1_percent_xp': p99_xp,
            'player_count': player_count,
            'xp_std_dev': std_xp,
            'avg_level': avg_level,
            #'snapshot_date': snapshot_date
        }
        skill_aggregates.append(skill_row)
    
    result_df = pd.DataFrame(skill_aggregates)
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
    
    leaderboards = []
    
    for skill in skill_df['metric'].unique():
        skill_data = skill_df[skill_df['metric'] == skill].copy()
        
        # Sort by XP descending and get top N
        cols_to_get = ['player_id', 'username', 'value', 'rank']
        if 'level' in skill_data.columns:
            cols_to_get.append('level')
        
        top_players = skill_data.nlargest(top_n, 'value')[cols_to_get].reset_index(drop=True)
        
        top_players['leaderboard_rank'] = range(1, len(top_players) + 1)
        top_players['skill'] = skill
        
        leaderboards.append(top_players)
    
    result_df = pd.concat(leaderboards, ignore_index=True) if leaderboards else pd.DataFrame()
    logging.info(f"Created leaderboard data for {len(result_df)} entries")
    return result_df


def extract_player_segmentation(df):
    '''
    Extract: Player Segmentation Table
    Grain: player
    
    Derived classifications:
    - player_type: "combat", "skiller", "balanced"
    - activity_tier: "casual", "active", "hardcore"
    - progress_stage: "early", "mid", "late", "endgame"
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
    
    segmentation = []
    
    # Define XP thresholds for activity tiers
    casual_threshold = 1_000_000      # 1M total XP
    active_threshold = 10_000_000     # 10M total XP
    
    # Define level thresholds for progress stages
    early_level = 30
    mid_level = 60
    late_level = 85
    
    combat_skills = ['attack', 'strength', 'defence', 'hitpoints', 'ranged', 'magic']
    
    for player_id in skill_df['player_id'].unique():
        player_data = skill_df[skill_df['player_id'] == player_id]
        
        total_xp = player_data['value'].sum()
        
        # Get average level from calculated levels
        avg_level = 0
        if 'level' in skill_df.columns:
            level_data = player_data[player_data['level'].notna()]
            avg_level = level_data['level'].mean() if not level_data.empty else 0
        
        # Classify player type
        combat_xp = player_data[player_data['metric'].isin(combat_skills)]['value'].sum()
        skilling_xp = total_xp - combat_xp
        
        if total_xp > 0:
            combat_ratio = combat_xp / total_xp
            if combat_ratio > 0.6:
                player_type = "combat-focused"
            elif combat_ratio < 0.4:
                player_type = "skiller"
            else:
                player_type = "balanced"
        else:
            player_type = "new"
        
        # Classify activity tier
        if total_xp < casual_threshold:
            activity_tier = "casual"
        elif total_xp < active_threshold:
            activity_tier = "active"
        else:
            activity_tier = "hardcore"
        
        # Classify progress stage
        if avg_level < early_level:
            progress_stage = "early"
        elif avg_level < mid_level:
            progress_stage = "mid"
        elif avg_level < late_level:
            progress_stage = "late"
        else:
            progress_stage = "endgame"
        
        seg_row = {
            'player_id': player_id,
            'username': player_data['username'].iloc[0] if 'username' in df.columns else 'unknown',
            'player_type': player_type,
            'activity_tier': activity_tier,
            'progress_stage': progress_stage,
            'total_xp': total_xp,
            'avg_level': avg_level
        }
        segmentation.append(seg_row)
    
    result_df = pd.DataFrame(segmentation)
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
    
    efficiency = []
    
    for player_id in skill_df['player_id'].unique():
        player_data = skill_df[skill_df['player_id'] == player_id]
        
        for skill in player_data['metric'].unique():
            skill_data = player_data[player_data['metric'] == skill]
            
            xp = skill_data['value'].iloc[0]
            level = skill_data['level'].iloc[0] if 'level' in skill_data.columns and pd.notna(skill_data['level'].iloc[0]) else 1
            
            # Efficiency: XP per level
            xp_per_level = xp / max(level, 1)
            xp_to_next = max(0, (level + 1) * xp_per_level - xp)
            
            eff_row = {
                'player_id': player_id,
                'skill': skill,
                'xp': xp,
                'level': level,
                'xp_per_level': xp_per_level,
                'xp_to_next_level': xp_to_next
            }
            efficiency.append(eff_row)
    
    result_df = pd.DataFrame(efficiency)
    
    # Calculate percentile for each skill
    if 'xp_per_level' in result_df.columns:
        result_df['efficiency_percentile'] = result_df.groupby('skill')['xp_per_level'].rank(pct=True) * 100
    
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
    
    # Calculate combat level for each player
    combat_skills = ['attack', 'strength', 'defence', 'hitpoints', 'prayer', 'ranged', 'magic']
    combat_cols = [f"{skill}_xp" for skill in combat_skills if f"{skill}_xp" in wide_xp.columns]
    
    if len(combat_cols) == len(combat_skills):
        def calc_combat_for_row(row):
            xp_values = [int(row[col]) if pd.notna(row[col]) else 0 for col in combat_cols]
            return combat_level_from_xp(*xp_values)
        
        wide_xp['combat_level'] = wide_xp.apply(calc_combat_for_row, axis=1)
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
    
    ranking_changes = []
    
    # Sort by player, skill, and timestamp
    skill_df_sorted = skill_df.sort_values(['player_id', 'metric', 'snapshot_ts'])
    
    for player_id in skill_df_sorted['player_id'].unique():
        for skill in skill_df_sorted['metric'].unique():
            player_skill_data = skill_df_sorted[
                (skill_df_sorted['player_id'] == player_id) &
                (skill_df_sorted['metric'] == skill)
            ].reset_index(drop=True)
            
            if len(player_skill_data) < 2:
                continue
            
            for idx in range(1, len(player_skill_data)):
                prev_row = player_skill_data.iloc[idx - 1]
                curr_row = player_skill_data.iloc[idx]
                
                rank_change = int(prev_row['rank']) - int(curr_row['rank']) if 'rank' in prev_row else 0
                
                change_row = {
                    'player_id': player_id,
                    'skill': skill,
                    'snapshot_ts': curr_row['snapshot_ts'],
                    'rank': curr_row['rank'],
                    'rank_change': rank_change,
                    'xp': curr_row['value'],
                    'level': curr_row['level'] if 'level' in curr_row and pd.notna(curr_row['level']) else None
                }
                ranking_changes.append(change_row)
    
    result_df = pd.DataFrame(ranking_changes)
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
        df = add_calculated_levels(df)
        #logging.info(f"Data shape after level calculation: {df.shape}")
    
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
