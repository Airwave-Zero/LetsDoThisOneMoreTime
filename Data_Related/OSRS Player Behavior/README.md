# OSRS Player Progression & Behavior Analysis

## Overview

This ETL project analyzes player progression in Old School RuneScape using publicly available data, observations, and derived calculations to better understand how accounts spend their time and progress over days, weeks, and months.

The core focus is on:
- Experience gains
- Activity distribution
- Progression patterns over time  

Rather than ranking players or judging performance, the project tracks how these metrics evolve over time to surface behavioral patterns that **may appear unusual or difficult to sustain under normal play conditions over longer periods of time**.

---

## Disclaimer

This project does **not** attempt to label or ban players.

Any “suspicious” classification is:
- Analytical only
- Relative to the scoped dataset
- Intended to surface patterns for further inspection  

It does **not** make definitive claims about automation or rule-breaking. 

---

## Goals

- Build an **automatic, repeatable, and cloud-friendly** ETL pipeline for OSRS player data  
- Snapshot player stats to enable **time-based analysis**
- Analyze progression trends over time rather than single-point lookups
- Compare players **only within the collected dataset** to reduce bias
- Experiment with anomaly-style scoring for unrealistic or highly constrained behaviors

---

## Data Sources

This project combines multiple data sources to lower selection bias and increase coverage.

### 1. Wise Old Man – Clan / Group Members
- Players discovered through tracked clans and groups
- Provides structured progression data across time
- Represents semi-organized and social player segments  

### 2. Wise Old Man – Leaderboards
- Top daily, weekly, and monthly XP records by skill and account type
- Captures extreme but legitimate play patterns
- Used as a reference point for high-efficiency behavior

### 3. OSRS HiScores (Specific lookups + Leaderboards)
- Direct lookups from the official OSRS HiScores
- Enables frequent refreshes (6-hour, daily, etc.) without overloading the Wise Old Man API
- Allows lookup of **any player**, not just those who have updated stats via Wise Old Man  
- Useful for detecting long gaps between official stat updates vs local snapshot timing

### 4. Observational Username Collection (RuneLite Plugin)
- Auto-recorded usernames observed in historically bot-heavy areas (e.g. Edgeville yew trees)
- Used strictly **to gather types of players from different sources**
- Observation alone does not imply suspicious behavior

**Each username is still just data, no assumptions or claims are made.**  

---

## Design Choices

### Snapshot-Based Analysis

Storing periodic snapshots allows analysis of:
- XP deltas between snapshots
- Progression consistency (days, weeks, etc.)
- Activity concentration/spread

---

### Dataset-Scoped Comparisons

All analysis is performed **only within the collected dataset**, which helps avoid:
- Misclassifying niche or unconventional playstyles
- Comparing casual players against extreme leaderboard outliers
- Overgeneralizing from incomplete or biased samples

---

### Risk Scoring, Not Classification

The project produces **relative anomaly scores**, not strict labels or accusations.

Scores can be derived from combinations of signals such as:
- Lack of variety in account activity
- Highly consistent or repetitive progression patterns
- Repeated observation in constrained or high-risk locations
- Narrow focus on a single skill or activity over long periods  

---

## Local Architecture & Technologies

### Core Technologies

- **Python** – scraping, API calls, ingestion, and feature generation
- **Dagster** – orchestration and scheduled pipelines
- **CSV** – raw ingestion format
- **dbt** – cleaning, transforming, and modeling analytical tables  
- **Parquet** – OLAP-oriented analytical storage
- **DuckDB** – fast local analytical queries
- **Power BI** – visualization and exploratory analysis
- **GitHub** – version control and documentation  

---

## Future Plans

- Introduce machine learning for clustering or anomaly-assistance  
- Migrate orchestration to **Azure Data Factory**
- Store analytical data in **Azure Blob Storage** (Parquet-based data lake)
- Use **Azure Functions** for lightweight ingestion and refresh jobs
- Publish a public dashboard with aggregated, non-identifying metrics

---

## Disclaimer (again...)

All data used in this project is sourced from:
- Public APIs (WiseOldMan, OSRS HiScores)
- Passive in-game observation

This project is intended for **technical exploration and data engineering practice only** and does not make claims about individual players.