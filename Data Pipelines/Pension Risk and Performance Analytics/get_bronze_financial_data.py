import requests
import time
import yfinance as yf
import pandas as pd
import numpy as np
from fredapi import Fred
from urllib.parse import urlencode

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)

# ----------------------------
# CONFIG
# ----------------------------
FY_START = 2010
FY_START_STR = "2010-01-01"
FY_END   = 2024
FY_END_STR = "2024-12-31"
DEFAULT_FY_END_MONTH = 6   # June 30 — most public plans use this


# ============================================================
# COLUMN RENAME MAPS  —  API names → Power BI-friendly names
# ============================================================

PPD_RENAME = {
    # ── Identity ──
    "ppd_id":                "plan_id",
    "PlanName":              "plan_name",
    "fy":                    "fiscal_year",
    # ── Exposure: Actual Allocation ──
    "EQDomesticTotal_Actl":  "equity_domestic_actual_pct",
    "EQIntlTotal_Actl":      "equity_intl_actual_pct",
    "EQTotal_Actl":          "equity_total_actual_pct",
    "FITotal_Actl":          "fixed_income_actual_pct",
    "RETotal_Actl":          "real_estate_actual_pct",
    "PETotal_Actl":          "private_equity_actual_pct",
    "HFTotal_Actl":          "hedge_fund_actual_pct",
    "CashTotal_Actl":        "cash_actual_pct",
    "COMDTotal_Actl":        "commodities_actual_pct",
    "AltMiscTotal_Actl":     "alt_misc_actual_pct",
    "OtherTotal_Actl":       "other_actual_pct",
    # ── Exposure: Target Allocation ──
    "EQTotal_Trgt":          "equity_total_target_pct",
    "FITotal_Trgt":          "fixed_income_target_pct",
    "RETotal_Trgt":          "real_estate_target_pct",
    "PETotal_Trgt":          "private_equity_target_pct",
    "HFTotal_Trgt":          "hedge_fund_target_pct",
    "CashTotal_Trgt":        "cash_target_pct",
    "COMDTotal_Trgt":        "commodities_target_pct",
    "AltMiscTotal_Trgt":     "alt_misc_target_pct",
    "OtherTotal_Trgt":       "other_target_pct",
    # ── Funding ──
    "ActFundedRatio_GASB":   "funded_ratio_gasb",
    "ActFundedRatio_GASB67": "funded_ratio_gasb67",
    "ActLiabilities_GASB":   "actuarial_liabilities_gasb",
    "TotalPensionLiability": "total_pension_liability",
    "UAAL_GASB":             "unfunded_liability_gasb",
    "NetPensionLiability":   "net_pension_liability",
    "NetPosition":           "net_position",
    # ── Returns ──
    "InvestmentReturn_1yr":  "return_1yr",
    "InvestmentReturn_3yr":  "return_3yr",
    "InvestmentReturn_5yr":  "return_5yr",
    "InvestmentReturn_10yr": "return_10yr",
    # ── Assets ──
    "MktAssets_net":         "net_market_assets",
}

MACRO_RENAME = {
    "CPI":                  "cpi_index",
    "10yr_rate":            "treasury_10yr_rate",
    "fed_funds":            "fed_funds_rate",
    "unemployment_rate":    "unemployment_rate",        # already clean
    "underemployment_u6":   "underemployment_u6_rate",
    "job_openings_rate":    "job_openings_rate",        # already clean
    "inflation_mom":        "inflation_mom_pct",
    "inflation_yoy":        "inflation_yoy_pct",
    "u6_minus_u3":          "labor_slack_u6_minus_u3",
    "yield_curve_proxy":    "yield_curve_10yr_minus_ff",
}

# Wide-format ticker columns → prefixed so Power BI recognizes them as returns
TICKER_RETURN_RENAME = {
    "SPY": "return_spy",
    "EFA": "return_efa",
    "EEM": "return_eem",
    "AGG": "return_agg",
    "VNQ": "return_vnq",
    "PSP": "return_psp",
    "TIP": "return_tip",
    "SHV": "return_shv",
}


# ----------------------------
# PPD API variable lists (must match API field names exactly)
# ----------------------------
exposure_params = (
    "ppd_id,PlanName,fy,"
    "EQDomesticTotal_Actl,EQIntlTotal_Actl,EQTotal_Actl,FITotal_Actl,RETotal_Actl,"
    "PETotal_Actl,HFTotal_Actl,CashTotal_Actl,COMDTotal_Actl,AltMiscTotal_Actl,OtherTotal_Actl,"
    "EQTotal_Trgt,FITotal_Trgt,RETotal_Trgt,PETotal_Trgt,HFTotal_Trgt,CashTotal_Trgt,"
    "COMDTotal_Trgt,AltMiscTotal_Trgt,OtherTotal_Trgt"
)
exposure_numeric_cols = [
    "EQDomesticTotal_Actl","EQIntlTotal_Actl","EQTotal_Actl","FITotal_Actl",
    "RETotal_Actl","PETotal_Actl","HFTotal_Actl","CashTotal_Actl",
    "COMDTotal_Actl","AltMiscTotal_Actl","OtherTotal_Actl",
    "EQTotal_Trgt","FITotal_Trgt","RETotal_Trgt","PETotal_Trgt",
    "HFTotal_Trgt","CashTotal_Trgt","COMDTotal_Trgt","AltMiscTotal_Trgt","OtherTotal_Trgt"
]
funding_params = (
    "ppd_id,PlanName,fy,"
    "ActFundedRatio_GASB,ActFundedRatio_GASB67,ActLiabilities_GASB,"
    "TotalPensionLiability,UAAL_GASB,NetPensionLiability,NetPosition"
)
funding_numeric_cols = [
    "ActFundedRatio_GASB","ActFundedRatio_GASB67","ActLiabilities_GASB",
    "TotalPensionLiability","UAAL_GASB","NetPensionLiability","NetPosition"
]
yearly_returns_params = "ppd_id,PlanName,fy,InvestmentReturn_1yr,InvestmentReturn_3yr,InvestmentReturn_5yr,InvestmentReturn_10yr"
returns_numeric_cols = [
    "InvestmentReturn_1yr","InvestmentReturn_3yr",
    "InvestmentReturn_5yr","InvestmentReturn_10yr"
]

total_assets_params = "ppd_id,PlanName,fy,MktAssets_net"
assets_numeric_cols = ["MktAssets_net"]

# ----------------------------
# Market proxies (yfinance)
# ----------------------------
tickers = ["SPY", "EFA", "EEM", "AGG", "VNQ", "PSP", "TIP", "SHV"]
ETF_TO_ASSET_CLASS = {
    "SPY": "Domestic Equity",
    "EFA": "International Equity",
    "EEM": "International Equity",
    "AGG": "Fixed Income",
    "VNQ": "Real Estate",
    "PSP": "Private Equity",
    "TIP": "Inflation-Linked",
    "SHV": "Cash",
}

with open("api_private.txt") as f:
    fred_api_key = f.read().strip()


# ============================================================
# URL BUILDER
# ============================================================
def build_public_plans_url(variables_csv, fy_start=FY_START, fy_end=FY_END, fmt="json"):
    base = "https://publicplansdata.org/api/"
    params = {
        "q": "QVariables",
        "variables": variables_csv,
        "filterfystart": fy_start,
        "filterfyend": fy_end,
        "format": fmt,
    }
    return base + "?" + urlencode(params)


def fetch_json_data(url, retries=3, sleep_s=0.5):
    for _ in range(retries):
        try:
            r = requests.get(url, timeout=60)
            if r.status_code == 200:
                return r.json()
            time.sleep(sleep_s)
        except Exception as e:
            print(f"Exception occurred: {e}")
            time.sleep(sleep_s)
    return None


def load_public_plans_json(json_obj, numeric_cols):
    """Converts PPD API JSON → clean DataFrame with normalized column names."""
    if json_obj is None:
        return pd.DataFrame()

    records = json_obj[1:]
    df = pd.DataFrame(records)

    id_cols = ["ppd_id", "PlanName", "fy"]
    data_cols = [c for c in df.columns if c not in id_cols]

    df = df.dropna(subset=data_cols, how="all")
    df = df.drop_duplicates(subset=id_cols, keep="first")

    # numeric conversion uses original API names (before rename)
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["fy"]     = pd.to_numeric(df["fy"], errors="coerce").astype("Int64")
    df["ppd_id"] = pd.to_numeric(df["ppd_id"], errors="coerce").astype("Int64")

    df = df.rename(columns=PPD_RENAME)
    return df


def get_public_plans_data():
    exposure_url       = build_public_plans_url(exposure_params)
    funding_url        = build_public_plans_url(funding_params)
    yearly_returns_url = build_public_plans_url(yearly_returns_params)
    total_assets_url   = build_public_plans_url(total_assets_params)

    return (
        fetch_json_data(exposure_url),
        fetch_json_data(funding_url),
        fetch_json_data(yearly_returns_url),
        fetch_json_data(total_assets_url),
    )


# ============================================================
# yfinance
# ============================================================
def get_yfinance_data(start_str, end_str, interval_str, dimension_type):
    df_prices = yf.download(tickers, start=start_str, end=end_str, interval=interval_str)
    df_drilldown = df_prices[dimension_type].pct_change()
    df_drilldown.to_csv(f"bronze_yfinance_{dimension_type}_changes.csv")

    df_renamed = df_drilldown.rename(columns=ETF_TO_ASSET_CLASS)
    df_renamed_corr = df_renamed.corr()
    df_renamed_corr.to_csv(f"bronze_yfinance_{dimension_type}_corr.csv")

    return df_prices, df_drilldown, df_renamed_corr


# ============================================================
# FRED  (derived cols computed with old names, then renamed at the end)
# ============================================================
def get_fred_data():
    fred = Fred(api_key=fred_api_key)

    cpi        = fred.get_series("CPIAUCSL")
    rates_10y  = fred.get_series("DGS10")
    fed_funds  = fred.get_series("FEDFUNDS")
    unrate     = fred.get_series("UNRATE")
    u6rate     = fred.get_series("U6RATE")
    jtsjor     = fred.get_series("JTSJOR")

    df_macro = pd.DataFrame({
        "CPI": cpi, "10yr_rate": rates_10y, "fed_funds": fed_funds,
        "unemployment_rate": unrate, "underemployment_u6": u6rate,
        "job_openings_rate": jtsjor,
    })
    df_macro = df_macro.resample("ME").last()

    # derived columns (use old names — rename happens below)
    df_macro["inflation_mom"]     = df_macro["CPI"].pct_change()
    df_macro["inflation_yoy"]     = df_macro["CPI"].pct_change(12)
    df_macro["u6_minus_u3"]       = df_macro["underemployment_u6"] - df_macro["unemployment_rate"]
    df_macro["yield_curve_proxy"] = df_macro["10yr_rate"] - df_macro["fed_funds"]

    df_macro.index.name = "date"
    df_macro = df_macro.reset_index()

    df_macro = df_macro.rename(columns=MACRO_RENAME)
    df_macro.to_csv("bronze_fred_macro_data.csv", index=False)
    return df_macro


# ============================================================
# PPD consolidation helpers  (all use NORMALIZED names)
# ============================================================
PPD_KEYS = ["plan_id", "plan_name", "fiscal_year"]


def merge_ppd_annual(df_exp, df_fund, df_ret, df_assets):
    """Merge all 4 PPD tables into one wide annual table."""
    out = df_exp.merge(df_fund,   on=PPD_KEYS, how="outer", suffixes=("", "_fund"))
    out = out.merge(df_ret,       on=PPD_KEYS, how="outer", suffixes=("", "_ret"))
    out = out.merge(df_assets,    on=PPD_KEYS, how="outer", suffixes=("", "_assets"))
    return out


def add_fiscal_year(date_series, fy_end_month=DEFAULT_FY_END_MONTH):
    d  = pd.to_datetime(date_series)
    fy = d.dt.year.where(d.dt.month <= fy_end_month, d.dt.year + 1)
    return fy.astype(int)

def ppd_annual_to_monthly(df_ppd_annual, fy_end_month=DEFAULT_FY_END_MONTH):
    df = df_ppd_annual.copy()

    df["date"] = pd.to_datetime(
        df["fiscal_year"].astype(str) + f"-{fy_end_month:02d}-28"
    ) + pd.offsets.MonthEnd(0)

    df = df.sort_values(["plan_id", "plan_name", "date"]).set_index("date")

    monthly_frames = []
    for (pid, plan), g in df.groupby(["plan_id", "plan_name"]):
        gm = g.resample("ME").ffill()
        gm["plan_id"]   = pid
        gm["plan_name"] = plan
        monthly_frames.append(gm)

    out = pd.concat(monthly_frames).reset_index()
    out["date"] = pd.to_datetime(out["date"]) + pd.offsets.MonthEnd(0)
    return out

def monthly_returns_to_fy(df_monthly, fy_end_month=DEFAULT_FY_END_MONTH):
    df = df_monthly.copy()
    df["fiscal_year"] = add_fiscal_year(df["date"], fy_end_month)
    value_cols = [c for c in df.columns if c not in ("date", "fiscal_year")]
    fy_ret = (
        df.groupby("fiscal_year")[value_cols]
          .apply(lambda x: (1 + x).prod(skipna=True) - 1)
          .reset_index()
    )
    return fy_ret


def monthly_macro_to_fy(df_macro, fy_end_month=DEFAULT_FY_END_MONTH):
    df = df_macro.copy()
    df["fiscal_year"] = add_fiscal_year(df["date"], fy_end_month)

    # references use the NEW normalized names
    agg_map = {}
    for c in ["treasury_10yr_rate", "fed_funds_rate", "unemployment_rate",
              "underemployment_u6_rate", "job_openings_rate",
              "yield_curve_10yr_minus_ff"]:
        if c in df.columns:
            agg_map[c] = "mean"
    for c in ["cpi_index", "inflation_yoy_pct"]:
        if c in df.columns:
            agg_map[c] = "last"

    return df.groupby("fiscal_year").agg(agg_map).reset_index()


# ============================================================
# OHLC + Risk features
# ============================================================
def make_ohlc_levels_tidy(df_prices: pd.DataFrame) -> pd.DataFrame:
    df = df_prices.copy()
    df.index = pd.to_datetime(df.index) + pd.offsets.MonthEnd(0)
    df.index.name = "date"

    if df.columns.names != ["Price", "Ticker"]:
        df.columns = df.columns.set_names(["Price", "Ticker"])

    tidy = df.stack("Ticker").reset_index()
    tidy = tidy.rename(columns={"Ticker": "ticker"})

    rename_map = {
        "Open": "open", "High": "high", "Low": "low",
        "Close": "close", "Adj Close": "adj_close", "Volume": "volume",
    }
    tidy = tidy.rename(columns=rename_map)

    keep = ["date", "ticker", "open", "high", "low", "close", "adj_close", "volume"]
    keep = [c for c in keep if c in tidy.columns]
    tidy = tidy[keep].sort_values(["ticker", "date"]).reset_index(drop=True)
    return tidy


def _window_max_drawdown(prices: np.ndarray) -> float:
    if len(prices) == 0:
        return np.nan
    peak = np.maximum.accumulate(prices)
    dd = prices / peak - 1.0
    return np.nanmin(dd)


def build_monthly_risk_features(df_ohlc_tidy: pd.DataFrame, ticker_to_asset_class: dict) -> pd.DataFrame:
    df = df_ohlc_tidy.copy()
    df = df.sort_values(["ticker", "date"]).reset_index(drop=True)

    df["asset_class"] = df["ticker"].map(ticker_to_asset_class)
    df["close_ret"] = df.groupby("ticker")["close"].pct_change()
    df["running_peak_close"] = df.groupby("ticker")["close"].cummax()
    df["drawdown_from_peak"] = (df["close"] / df["running_peak_close"]) - 1.0
    df["close_from_month_high"] = (df["close"] / df["high"]) - 1.0
    df["close_from_month_low"] = (df["close"] / df["low"]) - 1.0
    df["hl_range_pct"] = (df["high"] - df["low"]) / df["close"]
    df["log_hl_range"] = np.log(df["high"] / df["low"])
    df["parkinson_vol_proxy"] = np.sqrt((1.0 / (4.0 * np.log(2.0))) * (df["log_hl_range"] ** 2))
    df["vol_3m"] = df.groupby("ticker")["close_ret"].rolling(3).std().reset_index(level=0, drop=True)
    df["vol_12m"] = df.groupby("ticker")["close_ret"].rolling(12).std().reset_index(level=0, drop=True)
    df["max_drawdown_12m"] = (
        df.groupby("ticker")["close"]
          .rolling(12, min_periods=2)
          .apply(_window_max_drawdown, raw=True)
          .reset_index(level=0, drop=True)
    )
    df["is_peak"] = df["close"].eq(df["running_peak_close"])
    df["peak_segment"] = df.groupby("ticker")["is_peak"].cumsum()
    df["months_since_peak"] = df.groupby(["ticker", "peak_segment"]).cumcount()
    df["is_underwater"] = df["drawdown_from_peak"] < 0
    df["recovered_this_month"] = df["months_since_peak"] == 0
    return df


def build_asset_class_rollup(df_risk: pd.DataFrame) -> pd.DataFrame:
    return (
        df_risk.groupby(["date", "asset_class"])
               .agg(
                   avg_close_ret=("close_ret", "mean"),
                   avg_hl_range_pct=("hl_range_pct", "mean"),
                   avg_drawdown=("drawdown_from_peak", "mean"),
                   worst_drawdown=("drawdown_from_peak", "min"),
                   avg_parkinson=("parkinson_vol_proxy", "mean"),
                   avg_vol_12m=("vol_12m", "mean"),
                   worst_max_dd_12m=("max_drawdown_12m", "min"),
                   avg_months_since_peak=("months_since_peak", "mean"),
                   max_months_since_peak=("months_since_peak", "max"),
               )
               .reset_index()
    )

def build_dim_date(start=FY_START_STR, end=FY_END_STR, fy_end_month=6):
    df = pd.DataFrame({
        "date": pd.date_range(start=start, end=end, freq="ME")
    })

    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.strftime("%b")
    df["year_month"] = df["date"].dt.strftime("%Y-%m")

    # Fiscal year logic (same as your pipeline)
    df["fiscal_year"] = np.where(
        df["date"].dt.month <= fy_end_month,
        df["date"].dt.year,
        df["date"].dt.year + 1
    )

    return df

def build_dim_plan(df_ppd_annual):
    return (
        df_ppd_annual[["plan_id", "plan_name"]]
        .drop_duplicates()
        .sort_values("plan_name")
        .reset_index(drop=True)
    )

def build_dim_asset_class():
    asset_classes = [
        "Domestic Equity",
        "International Equity",
        "Fixed Income",
        "Real Estate",
        "Private Equity",
        "Hedge Funds",
        "Cash",
        "Commodities",
        "Alternative Misc",
        "Other"
    ]
    return pd.DataFrame({
        "asset_class_id": range(1, len(asset_classes) + 1),
        "asset_class": asset_classes
    })

def build_dim_ticker(ticker_to_asset_class: dict) -> pd.DataFrame:
    return (pd.DataFrame({
                "ticker": list(ticker_to_asset_class.keys()),
                "asset_class": list(ticker_to_asset_class.values())
            })
            .drop_duplicates()
            .sort_values("ticker")
            .reset_index(drop=True))


# ============================================================
# MAIN
# ============================================================
def main():
    # ── Source 1: Public Plans (annual) ──────────────────────
    exposure_obj, funding_obj, yearly_returns_obj, total_assets_obj = get_public_plans_data()

    df_exp    = load_public_plans_json(exposure_obj,        exposure_numeric_cols)
    df_fund   = load_public_plans_json(funding_obj,         funding_numeric_cols)
    df_ret    = load_public_plans_json(yearly_returns_obj,  returns_numeric_cols)
    df_assets = load_public_plans_json(total_assets_obj,    assets_numeric_cols)

    df_exp.to_csv("bronze_pplans_exposure.csv",  index=False)
    df_fund.to_csv("bronze_pplans_funding.csv",  index=False)
    df_ret.to_csv("bronze_pplans_returns.csv",   index=False)
    df_assets.to_csv("bronze_pplans_assets.csv", index=False)

    # Merge into one wide annual table
    df_ppd_annual = merge_ppd_annual(df_exp, df_fund, df_ret, df_assets)
    df_ppd_annual.to_csv("silver_ppd_annual.csv", index=False)

    # ── Source 2: yfinance (monthly) ─────────────────────────
    df_raw, df_close_ret, df_close_corr = get_yfinance_data(FY_START_STR, FY_END_STR, "1mo", "Close")
    _,      df_high_ret,  df_high_corr  = get_yfinance_data(FY_START_STR, FY_END_STR, "1mo", "High")
    _,      df_low_ret,   df_low_corr   = get_yfinance_data(FY_START_STR, FY_END_STR, "1mo", "Low")

    df_close_ret.index.name = "date"
    df_close_ret = df_close_ret.reset_index()
    df_close_ret["date"] = pd.to_datetime(df_close_ret["date"]) + pd.offsets.MonthEnd(0)

    df_close_ret = df_close_ret.rename(columns=TICKER_RETURN_RENAME)

    df_ohlc = make_ohlc_levels_tidy(df_raw)
    df_ohlc.to_csv("bronze_yfinance_ohlc_levels.csv", index=False)

    df_risk = build_monthly_risk_features(df_ohlc, ETF_TO_ASSET_CLASS)
    df_risk.to_csv("gold_market_risk_features_monthly.csv", index=False)

    df_roll = build_asset_class_rollup(df_risk)
    df_roll.to_csv("gold_market_risk_assetclass_rollup.csv", index=False)

    dim_ticker = build_dim_ticker(ETF_TO_ASSET_CLASS)
    dim_ticker.to_csv("silver_dim_ticker.csv", index=False)

    # ── Source 3: FRED (monthly) ─────────────────────────────
    df_macro = get_fred_data()  

    # ── Bronze: market + macro monthly ───────────────────────
    df_market_macro = df_close_ret.merge(df_macro, on="date", how="left")
    df_market_macro.to_csv("bronze_final_data.csv", index=False)

    # ══════════════════════════════════════════════════════════
    # OPTION A — Monthly panel: PPD (forward-filled) + market + macro
    # ══════════════════════════════════════════════════════════
    df_ppd_monthly = ppd_annual_to_monthly(df_ppd_annual)
    df_ppd_monthly.to_csv("silver_ppd_monthly_ffill.csv", index=False)

    df_monthly_panel = (
        df_ppd_monthly
        .merge(df_close_ret, on="date", how="left")
        .merge(df_macro,     on="date", how="left")
    )
    df_monthly_panel.to_csv("gold_monthly_plan_panel.csv", index=False)

    # ══════════════════════════════════════════════════════════
    # OPTION B — Annual peer context: PPD + FY-aggregated market + macro
    # ══════════════════════════════════════════════════════════
    df_mkt_fy   = monthly_returns_to_fy(df_close_ret)
    df_macro_fy = monthly_macro_to_fy(df_macro)

    df_annual_peer = (
        df_ppd_annual
        .merge(df_mkt_fy,   on="fiscal_year", how="left", suffixes=("", "_mkt"))
        .merge(df_macro_fy, on="fiscal_year", how="left", suffixes=("", "_macro"))
    )
    df_annual_peer.to_csv("gold_annual_peer_context.csv", index=False)

    
    dim_date = build_dim_date()
    dim_date.to_csv("dim_date.csv", index=False)

    dim_plan = build_dim_plan(df_ppd_annual)
    dim_plan.to_csv("dim_plan.csv", index=False)

    dim_asset_class = build_dim_asset_class()
    dim_asset_class.to_csv("dim_asset_class.csv", index=False)

    print("  bronze_pplans_*.csv                    — raw PPD tables")
    print("  bronze_final_data.csv                  — monthly market + macro")
    print("  bronze_fred_macro_data.csv             — FRED macro indicators")
    print("  bronze_yfinance_ohlc_levels.csv        — ETF OHLC prices (tidy)")
    print("  silver_ppd_annual.csv                  — merged annual PPD (all 4 tables)")
    print("  silver_ppd_monthly_ffill.csv           — annual PPD forward-filled to monthly")
    print("  silver_dim_ticker.csv                  — ticker → asset class lookup")
    print("  gold_monthly_plan_panel.csv            — Option A: monthly PPD + market + macro")
    print("  gold_annual_peer_context.csv           — Option B: annual PPD + FY market + FY macro")
    print("  gold_market_risk_features_monthly.csv  — ETF risk features (monthly)")
    print("  gold_market_risk_assetclass_rollup.csv — asset class risk rollup")


def calculate_volatility_all_years():
    # Load correlation matrix (stays the same across years in your current setup)
    corr = pd.read_csv("bronze_yfinance_Close_corr.csv", index_col=0)
    corr.columns = corr.columns.str.replace(r'\.\d+$', '', regex=True)
    corr = corr.T.groupby(level=0).mean().T
    corr = corr.groupby(level=0).mean()

    # Load risk rollup for volatility
    gold = pd.read_csv("gold_market_risk_assetclass_rollup.csv")
    latest_vol = gold.groupby("asset_class")["avg_vol_12m"].mean()

    assets = corr.columns
    vols = latest_vol[assets].values
    cov_matrix = corr.values * np.outer(vols, vols)

    # --- Loop through years ---
    all_summaries = []
    all_breakdowns = []

    for year in range(2010, 2025):
        try:
            weight_map = get_ocers_weights_from_panel("gold_monthly_plan_panel.csv", year=year)
            weights = np.array([weight_map[a] for a in assets])

            # Portfolio risk
            port_var = weights @ cov_matrix @ weights
            port_vol = np.sqrt(port_var)
            port_vol_annual = port_vol * np.sqrt(12)

            all_summaries.append({
                "year": year,
                "portfolio_vol_monthly": port_vol,
                "portfolio_vol_annual": port_vol_annual,
            })

            # Marginal & total contribution
            marginal = cov_matrix @ weights
            contribution = weights * marginal

            for i, asset in enumerate(assets):
                all_breakdowns.append({
                    "year": year,
                    "asset_class": asset,
                    "weight": weights[i],
                    "marginal_contribution": marginal[i],
                    "risk_contribution": contribution[i],
                    "pct_of_total_risk": contribution[i] / port_var,
                })

        except Exception as e:
            print(f"Skipping {year}: {e}")

    # Save
    summary_df = pd.DataFrame(all_summaries)
    breakdown_df = pd.DataFrame(all_breakdowns)

    summary_df.to_csv("portfolio_risk_summary_by_year.csv", index=False)
    breakdown_df.to_csv("portfolio_risk_breakdown_by_year.csv", index=False)

    print(summary_df.to_string(index=False))
    return summary_df, breakdown_df


def get_last_known_equity_ratio(df, plan_name="Orange County (CA) ERS"):
    """Find the most recent year where both domestic and intl are reported."""
    
    plan_data = df[df["plan_name"].str.contains(plan_name, case=False, regex=False)].sort_values(
        "fiscal_year", ascending=False
    )

    for _, row in plan_data.iterrows():
        dom = row.get("equity_domestic_actual_pct", 0) or 0
        intl = row.get("equity_intl_actual_pct", 0) or 0
        if dom > 0 and intl > 0:
            total = dom + intl
            ratio = dom / total
            print(f"  Last known equity split: {row['fiscal_year']} → "
                  f"domestic {ratio:.3f} / intl {1-ratio:.3f}")
            return ratio
    print("  No domestic/intl split found — defaulting to 50/50")
    return 0.50

def get_ocers_weights_from_panel(panel_input, year=2024):
    """Extract and map OCERS weights to risk rollup asset classes."""

    if isinstance(panel_input, str):
        df = pd.read_csv(panel_input)
    else:
        df = panel_input

    # Filter to OCERS, target year

    # In get_ocers_weights_from_panel:
    ocers = df[(df["plan_name"].str.contains("Orange County (CA) ERS", case=False, regex=False)) &
            (df["fiscal_year"] == year)].iloc[0]


    # Raw values from the panel
    eq_domestic  = ocers["equity_domestic_actual_pct"] or 0
    eq_intl      = ocers["equity_intl_actual_pct"] or 0
    equity_total = ocers["equity_total_actual_pct"] or 0
    fixed_income = ocers["fixed_income_actual_pct"] or 0
    real_estate  = ocers["real_estate_actual_pct"] or 0
    private_eq   = ocers["private_equity_actual_pct"] or 0
    hedge_fund   = ocers["hedge_fund_actual_pct"] or 0
    cash         = ocers["cash_actual_pct"] or 0
    commodities  = ocers["commodities_actual_pct"] or 0
    alt_misc     = ocers["alt_misc_actual_pct"] or 0

    # --- MAPPING TO RISK ROLLUP'S 7 CLASSES ---

    # 1. Split equity — use raw data when available, fallback to last known ratio
    if eq_domestic > 0 and eq_intl > 0:
        # BEST: both reported (OCERS 2010–2016)
        domestic_eq = eq_domestic
        intl_eq = eq_intl
        print(f"  {year}: Using reported split → dom={domestic_eq:.3f}, intl={intl_eq:.3f}")
    elif equity_total > 0:
        # FALLBACK: only total reported (OCERS 2017+)
        ratio = get_last_known_equity_ratio(df)
        domestic_eq = equity_total * ratio
        intl_eq = equity_total * (1 - ratio)
        print(f"  {year}: Using last known ratio ({ratio:.3f}) → "
              f"dom={domestic_eq:.3f}, intl={intl_eq:.3f}")
    else:
        domestic_eq = 0
        intl_eq = 0

    # 2. Real estate: use IPS target if reported as 0
    if real_estate == 0:
        real_estate = 0.068
        commodities = max(0, commodities - 0.068)

    # 3. Map commodities → Inflation-Linked
    inflation_linked = commodities

    # 4. Redistribute hedge_fund + alt_misc pro-rata across mapped classes
    unmapped = hedge_fund + alt_misc
    mapped = {
        "Domestic Equity":      domestic_eq,
        "International Equity": intl_eq,
        "Fixed Income":         fixed_income,
        "Private Equity":       private_eq,
        "Real Estate":          real_estate,
        "Inflation-Linked":     inflation_linked,
        "Cash":                 cash,
    }

    mapped_sum = sum(mapped.values())
    if unmapped > 0 and mapped_sum > 0:
        for k in mapped:
            mapped[k] += unmapped * (mapped[k] / mapped_sum)

    # Verify
    total = sum(mapped.values())
    print(f"  Total weight: {total:.4f}")

    for k, v in mapped.items():
        print(f"    {k}: {v:.4f}")

    return mapped



if __name__ == "__main__":
    #main()
    calculate_volatility_all_years()