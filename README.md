# bitcoin-sentiment-trader-analysis
Analysis of Hyperliquid trader performance across Bitcoin Fear &amp; Greed sentiment regimes
Bitcoin Sentiment and Trader Performance Analysis

This project looks at whether Bitcoin market sentiment (Fear and Greed Index) is related to how traders perform, using historical trade data from Hyperliquid.

What is in this repo

analysis.py - loads the two datasets, cleans them, merges trades with the sentiment index by date, and calculates performance stats including a Kruskal-Wallis significance test across sentiment categories.

charts.py - generates the charts used in the analysis.

chart1_return_by_sentiment.png, chart2_winrate_by_sentiment.png, chart3_pnl_boxplot.png, chart4_positionsize_by_sentiment.png, chart5_sentiment_vs_pnl_timeseries.png - the charts themselves.

Bitcoin_Sentiment_Trader_Analysis.docx - the full written report with methodology, findings, and conclusions.

Key finding

Win rate and average return per trade were both highest during Extreme Greed (89.2 percent win rate, 7.67 percent average return) and lowest during Extreme Fear (76.2 percent win rate, 0.89 percent average return). This difference was tested using a Kruskal-Wallis test and was statistically significant (p less than 0.0001).

Position size also varied by sentiment. Traders used smaller average position sizes during Extreme Greed (around 2,780 dollars) compared to Fear (around 8,041 dollars), suggesting the best results came from being more selective rather than sizing up.

How to run it

Install pandas, numpy, matplotlib, and scipy, then run analysis.py followed by charts.py in the same folder as the two source CSV files (fear_greed_index.csv and historical_data.csv).

Notes

Sentiment is applied at the daily level, so it does not capture changes in sentiment within a single day.

This analysis is based on 32 trading accounts, so results may not generalize to the wider market.

PnL figures reflect only closed (realized) trades.
