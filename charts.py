import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

merged = pd.read_csv('merged.csv', parse_dates=['date'])
order = ['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed']
merged['classification'] = pd.Categorical(merged['classification'], categories=order, ordered=True)
closed = merged[merged['Closed PnL'] != 0].copy()
closed['classification'] = pd.Categorical(closed['classification'], categories=order, ordered=True)
closed['return_pct'] = closed['Closed PnL'] / closed['Size USD'] * 100
closed['win'] = closed['Closed PnL'] > 0

colors = ['#8B0000','#D2691E','#808080','#2E8B57','#006400']

# ---- Chart 1: Avg return % and win rate by sentiment (dual bar) ----
stats = closed.groupby('classification', observed=True).agg(
    avg_return_pct=('return_pct','mean'),
    win_rate=('win','mean')
).reindex(order)

fig, ax1 = plt.subplots(figsize=(8,5))
x = np.arange(len(order))
ax1.bar(x, stats['avg_return_pct'], color=colors, alpha=0.85)
ax1.set_ylabel('Avg Return per Trade (%)')
ax1.set_xticks(x)
ax1.set_xticklabels(order, rotation=20)
ax1.axhline(0, color='black', linewidth=0.8)
ax1.set_title('Average Trade Return (%) by Market Sentiment')
plt.tight_layout()
plt.savefig('chart1_return_by_sentiment.png', dpi=150)
plt.close()

# ---- Chart 2: Win rate by sentiment ----
fig, ax = plt.subplots(figsize=(8,5))
ax.bar(x, stats['win_rate']*100, color=colors, alpha=0.85)
ax.set_ylabel('Win Rate (%)')
ax.set_xticks(x)
ax.set_xticklabels(order, rotation=20)
ax.set_ylim(0,100)
ax.set_title('Trader Win Rate by Market Sentiment')
for i,v in enumerate(stats['win_rate']*100):
    ax.text(i, v+1, f'{v:.1f}%', ha='center')
plt.tight_layout()
plt.savefig('chart2_winrate_by_sentiment.png', dpi=150)
plt.close()

# ---- Chart 3: Boxplot of PnL by sentiment (clipped for readability) ----
fig, ax = plt.subplots(figsize=(8,5))
data_to_plot = [closed[closed['classification']==c]['Closed PnL'].clip(-2000,2000) for c in order]
bp = ax.boxplot(data_to_plot, labels=order, patch_artist=True, showfliers=False)
for patch, c in zip(bp['boxes'], colors):
    patch.set_facecolor(c)
    patch.set_alpha(0.7)
ax.set_ylabel('Closed PnL per trade (USD, clipped at ±2000)')
ax.set_title('Distribution of Trade PnL by Market Sentiment')
plt.xticks(rotation=20)
plt.tight_layout()
plt.savefig('chart3_pnl_boxplot.png', dpi=150)
plt.close()

# ---- Chart 4: Position size by sentiment ----
size_stats = merged.groupby('classification', observed=True)['Size USD'].mean().reindex(order)
fig, ax = plt.subplots(figsize=(8,5))
ax.bar(x, size_stats, color=colors, alpha=0.85)
ax.set_ylabel('Avg Position Size (USD)')
ax.set_xticks(x)
ax.set_xticklabels(order, rotation=20)
ax.set_title('Average Position Size by Market Sentiment')
plt.tight_layout()
plt.savefig('chart4_positionsize_by_sentiment.png', dpi=150)
plt.close()

# ---- Chart 5: Time series overlay - daily sentiment value vs daily total PnL ----
sentiment_daily = merged[['date','value']].drop_duplicates().sort_values('date')
pnl_daily = merged.groupby('date')['Closed PnL'].sum().reset_index()
ts = sentiment_daily.merge(pnl_daily, on='date', how='inner').sort_values('date')

fig, ax1 = plt.subplots(figsize=(11,5))
ax1.plot(ts['date'], ts['value'], color='#444444', label='Fear & Greed Index', linewidth=1.2)
ax1.set_ylabel('Fear & Greed Index (0-100)')
ax1.set_xlabel('Date')
ax2 = ax1.twinx()
ax2.bar(ts['date'], ts['Closed PnL'], color='#2E8B57', alpha=0.4, width=1, label='Daily Total PnL')
ax2.set_ylabel('Daily Total Closed PnL (USD)')
ax1.set_title('Market Sentiment vs Daily Trader PnL (2024)')
fig.legend(loc='upper left', bbox_to_anchor=(0.1,0.88))
plt.tight_layout()
plt.savefig('chart5_sentiment_vs_pnl_timeseries.png', dpi=150)
plt.close()

print("Charts saved.")
