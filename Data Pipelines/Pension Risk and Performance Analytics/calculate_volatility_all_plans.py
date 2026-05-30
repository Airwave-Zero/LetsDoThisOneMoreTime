import pandas as pd
import numpy as np


def _clean_corr_matrix(corr_file):
    """Load a correlation CSV and handle duplicate columns by averaging."""
    corr = pd.read_csv(corr_file, index_col=0)
    corr.columns = corr.columns.str.replace(r'\.\d+$', '', regex=True)
    corr = corr.T.groupby(level=0).mean().T
    corr = corr.groupby(level=0).mean()
    return corr


def get_last_known_equity_ratio(df, plan_name):
    """
    Find the most recent year where both domestic and intl equity are reported
    for the given plan. Returns domestic/(domestic+intl). Defaults to 0.50.
    """
    plan_data = df[df["plan_name"] == plan_name].sort_values(
        "fiscal_year", ascending=False
    )
    for _, row in plan_data.iterrows():
        dom = row.get("equity_domestic_actual_pct", 0) or 0
        intl = row.get("equity_intl_actual_pct", 0) or 0
        if dom > 0 and intl > 0:
            return dom / (dom + intl)
    return 0.50


def get_plan_weights(df, plan_name, year):
    """
    Extract and map allocation weights for ANY plan to the 7 risk-rollup
    asset classes used in the covariance matrix.

    Parameters:
        df:         DataFrame from gold_annual_peer_context.csv
        plan_name:  Exact plan name string (e.g. "Alabama ERS")
        year:       Fiscal year (e.g. 2024)

    Returns:
        dict with keys: 'Domestic Equity', 'International Equity',
                        'Fixed Income', 'Private Equity', 'Real Estate',
                        'Inflation-Linked', 'Cash'
        Returns None if the plan-year doesn't exist or total weight < 1%.
    """
    row_df = df[(df["plan_name"] == plan_name) & (df["fiscal_year"] == year)]
    if row_df.empty:
        return None

    row = row_df.iloc[0]

    def safe(val):
        try:
            v = float(val)
            return v if not np.isnan(v) else 0.0
        except (TypeError, ValueError):
            return 0.0

    eq_domestic  = safe(row.get("equity_domestic_actual_pct", 0))
    eq_intl      = safe(row.get("equity_intl_actual_pct", 0))
    equity_total = safe(row.get("equity_total_actual_pct", 0))
    fixed_income = safe(row.get("fixed_income_actual_pct", 0))
    real_estate  = safe(row.get("real_estate_actual_pct", 0))
    private_eq   = safe(row.get("private_equity_actual_pct", 0))
    hedge_fund   = safe(row.get("hedge_fund_actual_pct", 0))
    cash         = safe(row.get("cash_actual_pct", 0))
    commodities  = safe(row.get("commodities_actual_pct", 0))
    alt_misc     = safe(row.get("alt_misc_actual_pct", 0))

    # 1. Split equity into domestic & international
    if eq_domestic > 0 and eq_intl > 0:
        domestic_eq = eq_domestic
        intl_eq = eq_intl
    elif equity_total > 0:
        ratio = get_last_known_equity_ratio(df, plan_name)
        domestic_eq = equity_total * ratio
        intl_eq = equity_total * (1 - ratio)
    else:
        domestic_eq = 0.0
        intl_eq = 0.0

    # 2. Real estate IPS fallback — OCERS-specific only
    is_ocers = "Orange County" in plan_name
    if is_ocers and real_estate == 0:
        real_estate = 0.068
        commodities = max(0, commodities - 0.068)

    # 3. Map commodities → Inflation-Linked
    inflation_linked = commodities

    # 4. Build mapped weights
    mapped = {
        "Domestic Equity":      domestic_eq,
        "International Equity": intl_eq,
        "Fixed Income":         fixed_income,
        "Private Equity":       private_eq,
        "Real Estate":          real_estate,
        "Inflation-Linked":     inflation_linked,
        "Cash":                 cash,
    }

    # 5. Redistribute hedge_fund + alt_misc pro-rata
    unmapped = hedge_fund + alt_misc
    mapped_sum = sum(mapped.values())

    if mapped_sum < 0.01:
        return None

    if unmapped > 0 and mapped_sum > 0:
        for k in mapped:
            mapped[k] += unmapped * (mapped[k] / mapped_sum)

    return mapped


def calculate_volatility_all_plans(
    corr_file="bronze_yfinance_Close_corr.csv",
    panel_file="gold_annual_peer_context.csv",
    risk_file="gold_market_risk_assetclass_rollup.csv",
    plan_filter=None,
    save_prefix="all_plans"
):
    """
    Calculate portfolio risk for every plan-year in the peer context panel.

    Parameters:
        corr_file:    Path to correlation matrix CSV (Close, High, or Low)
        panel_file:   Path to gold_annual_peer_context.csv (or DataFrame)
        risk_file:    Path to gold_market_risk_assetclass_rollup.csv
        plan_filter:  None = all plans; str = single plan; list = multiple
        save_prefix:  Prefix for output CSV filenames

    Returns:
        summary_df:   (plan_name, year, portfolio_vol_monthly, portfolio_vol_annual)
        breakdown_df: Per-asset risk contribution details
    """
    corr = _clean_corr_matrix(corr_file)

    gold = pd.read_csv(risk_file)
    latest_vol = gold.groupby("asset_class")["avg_vol_12m"].mean()

    assets = corr.columns.tolist()
    vols = latest_vol[assets].values
    cov_matrix = corr.values * np.outer(vols, vols)

    if isinstance(panel_file, str):
        df = pd.read_csv(panel_file)
    else:
        df = panel_file

    if plan_filter is not None:
        if isinstance(plan_filter, str):
            plan_filter = [plan_filter]
        df = df[df["plan_name"].isin(plan_filter)]

    combos = df[["plan_name", "fiscal_year"]].drop_duplicates()

    all_summaries = []
    all_breakdowns = []
    skipped = 0

    for _, combo_row in combos.iterrows():
        pname = combo_row["plan_name"]
        year = combo_row["fiscal_year"]

        try:
            weight_map = get_plan_weights(df, pname, year)
            if weight_map is None:
                skipped += 1
                print(f"  Skipping {pname} ({year}): No valid weights")
                continue

            weights = np.array([weight_map[a] for a in assets])

            port_var = weights @ cov_matrix @ weights
            port_vol = np.sqrt(port_var)
            port_vol_annual = port_vol * np.sqrt(12)

            all_summaries.append({
                "plan_name": pname,
                "year": year,
                "portfolio_vol_monthly": port_vol,
                "portfolio_vol_annual": port_vol_annual,
            })

            marginal = cov_matrix @ weights
            contribution = weights * marginal

            for i, asset in enumerate(assets):
                all_breakdowns.append({
                    "plan_name": pname,
                    "year": year,
                    "asset_class": asset,
                    "weight": weights[i],
                    "marginal_contribution": marginal[i],
                    "risk_contribution": contribution[i],
                    "pct_of_total_risk": contribution[i] / port_var if port_var > 0 else 0,
                })

        except Exception as e:
            skipped += 1
            continue

    summary_df = pd.DataFrame(all_summaries)
    breakdown_df = pd.DataFrame(all_breakdowns)

    summary_df.to_csv(f"{save_prefix}_risk_summary.csv", index=False)
    breakdown_df.to_csv(f"{save_prefix}_risk_breakdown.csv", index=False)

    print(f"  Processed: {len(combos)-skipped}/{len(combos)} plan-years | "
          f"{summary_df['plan_name'].nunique()} plans | Skipped: {skipped}")

    return summary_df, breakdown_df


# All 253 plans, standard Close correlation
summary, breakdown = calculate_volatility_all_plans()

'''
# Just OCERS
summary, breakdown = calculate_volatility_all_plans(
    plan_filter="Orange County (CA) ERS"
)

# Compare specific peers
summary, breakdown = calculate_volatility_all_plans(
    plan_filter=["Orange County (CA) ERS", "California PERF", "California Teachers"],
    save_prefix="ca_peer_comparison"
)
'''
