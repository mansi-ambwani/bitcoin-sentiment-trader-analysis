import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

pd.set_option('display.max_columns', None)

# ---------- Load ----------
sentiment = pd.read_csv('/mnt/user-data/uploads/fear_greed_index.csv')
trades = pd.read_csv('/mnt/user-data/uploads/historical_data.csv')

# ---------- Clean ----------
sentiment['date'] = pd.to_datetime(sentiment['date']).dt.date
trades['datetime'] = pd.to_datetime(trades['Timestamp IST'], format='%d-%m-%Y %H:%M')
trades['date'] = trades['datetime'].dt.date

# keep only rows within sentiment date range
min_d, max_d = sentiment['date'].min(), sentiment['date'].max()
trades = trades[(trades['date'] >= min_d) & (trades['date'] <= max_d)]

# ---------- Merge ----------
merged = trades.merge(sentiment[['date', 'classification', 'value']], on='date', how='left')
print("Merged shape:", merged.shape)
print("Unmatched dates:", merged['classification'].isna().sum())

merged.to_csv('/home/claude/analysis/merged.csv', index=False)

# ---------- Order sentiment categories ----------
order = ['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed']
merged['classification'] = pd.Categorical(merged['classification'], categories=order, ordered=True)

# ---------- Daily account-level aggregation ----------
daily = merged.groupby(['date', 'Account']).agg(
    total_pnl=('Closed PnL', 'sum'),
    total_volume=('Size USD', 'sum'),
    n_trades=('Closed PnL', 'count'),
    avg_size=('Size USD', 'mean')
).reset_index()
daily = daily.merge(sentiment[['date','classification','value']], on='date', how='left')
daily['classification'] = pd.Categorical(daily['classification'], categories=order, ordered=True)
daily['win'] = daily['total_pnl'] > 0

print("\n--- Daily account-level stats by sentiment class ---")
print(daily.groupby('classification', observed=True).agg(
    avg_daily_pnl=('total_pnl','mean'),
    median_daily_pnl=('total_pnl','median'),
    win_rate=('win','mean'),
    avg_volume=('total_volume','mean'),
    n=('total_pnl','count')
))

# ---------- Trade-level analysis (only closed positions, i.e. nonzero PnL) ----------
closed = merged[merged['Closed PnL'] != 0].copy()
closed['win'] = closed['Closed PnL'] > 0
closed['return_pct'] = closed['Closed PnL'] / closed['Size USD'] * 100

print("\n--- Trade-level stats by sentiment (closed trades only) ---")
trade_stats = closed.groupby('classification', observed=True).agg(
    avg_pnl=('Closed PnL','mean'),
    median_pnl=('Closed PnL','median'),
    win_rate=('win','mean'),
    avg_return_pct=('return_pct','mean'),
    avg_trade_size=('Size USD','mean'),
    n_trades=('Closed PnL','count')
)
print(trade_stats)

# ---------- Statistical test: does PnL differ across sentiment classes? ----------
groups = [closed[closed['classification']==c]['Closed PnL'].values for c in order]
kw_stat, kw_p = stats.kruskal(*groups)
print(f"\nKruskal-Wallis test on Closed PnL across sentiment classes: H={kw_stat:.2f}, p={kw_p:.4f}")

# ---------- Long/Short bias by sentiment ----------
closed['is_long'] = closed['Direction'].isin(['Open Long','Close Long','Buy'])
long_short = closed.groupby('classification', observed=True)['Side'].value_counts(normalize=True).unstack()
print("\n--- Buy/Sell ratio by sentiment ---")
print(long_short)

# ---------- Position size (proxy for risk appetite) ----------
print("\n--- Avg position size (Size USD) by sentiment, all trades ---")
print(merged.groupby('classification', observed=True)['Size USD'].agg(['mean','median','std']))

trade_stats.to_csv('trade_stats.csv')
daily_stats = daily.groupby('classification', observed=True).agg(
    avg_daily_pnl=('total_pnl','mean'), win_rate=('win','mean'), avg_volume=('total_volume','mean')
)
daily_stats.to_csv('daily_stats.csv')
