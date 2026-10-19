# Quantitative research and trading strategy backtests
# Bollinger Band Mean Reversion (v1)

**Status:** Tested. No edge found.
**Asset:** BTC-USD, daily candles, 2020–2025

This strategy tests a common idea: when a daily candle wicks outside its Bollinger Bands, price has overextended and should snap back toward the average. Over six years of Bitcoin data, the strategy lost money after costs and trailed buy-and-hold by a wide margin.

The failure is still informative. Breaking the results down shows *why* it failed, and those reasons say something useful about when band-based mean reversion should and shouldn't be trusted.

---

## Hypothesis

A wick beyond a Bollinger Band marks a short-term overreaction. Price should revert toward the middle band (the 20-day average) often enough, and far enough, to profit after costs.

## Rules

| Setting | Value |
|---|---|
| Bands | 20-day simple moving average, ±2 standard deviations (population, `ddof=0`) |
| Long signal | Yesterday's low was below yesterday's lower band |
| Short signal | Yesterday's high was above yesterday's upper band |
| Both bands pierced | Long takes priority |
| Entry | Today's open |
| Stop (long) | Signal candle's low − 0.5% |
| Stop (short) | Signal candle's high + 0.5% |
| Target 1 | Signal day's middle band: close 50% of the position |
| Target 2 | Signal day's opposite band: close the remaining 50% |
| After target 1 | Stop moves to breakeven (entry price), effective from the next day |
| Same-day stop and target | Stop is assumed to hit first (conservative) |
| Positions | One at a time. New signals are ignored while a trade is open |
| Costs | 0.10% per round trip on each exit |
| Sizing | Full capital per trade, compounded |

All settings were chosen before running the test and were **not** tuned to the results.

## Data

- Daily OHLCV for BTC-USD from Yahoo Finance (`yfinance`), 2 Jan 2020 to 31 Dec 2025
- Validated before use: duplicate dates dropped; rows with missing prices, low above high, open or close outside the day's range, or negative volume stop the run
- The first 20 days are used to warm up the bands, so trading begins in late January 2020

---

## Results

| Metric | Strategy | Buy & Hold BTC |
|---|---|---|
| Growth of $1 | **$0.36** | **$12.53** |
| Max drawdown | −82.8% | −76.6% |
| Number of trades | 249 | — |
| Win rate | 22.9% | — |
| Average win | +8.49% | — |
| Average loss | −2.85% | — |
| Expectancy per trade | **−0.26%** | — |

![Equity curve: strategy vs buy and hold](results/equity_curve.png)

With wins about three times the size of losses, the strategy needed to win roughly 25% of the time to break even. It won 22.9%: close, but on the wrong side. It also suffered a deeper drawdown than simply holding Bitcoin, while returning a small fraction of it.

### By direction

| Direction | Trades | Win rate | Expectancy | Total P&L |
|---|---|---|---|---|
| Long | 114 | 28.1% | +0.26% | +30.1 |
| Short | 135 | 18.5% | −0.70% | −93.9 |

### By year

| Year | Trades | Win rate | Expectancy | Total P&L |
|---|---|---|---|---|
| 2020 | 34 | 8.8% | +0.35% | +12.0 |
| 2021 | 42 | 21.4% | −0.69% | −29.0 |
| 2022 | 31 | 12.9% | −2.02% | −62.6 |
| 2023 | 48 | 31.3% | −0.02% | −1.0 |
| 2024 | 47 | 29.8% | +0.90% | +42.3 |
| 2025 | 47 | 25.5% | −0.54% | −25.5 |

### By how trades ended

| Outcome | Trades | Share | Expectancy |
|---|---|---|---|
| Stopped out before target 1 | 192 | 77% | −2.84% |
| Target 1, then stopped at breakeven | 24 | 10% | +3.70% |
| Target 1, then target 2 | 33 | 13% | +11.93% |

*Total P&L figures are sums of per-trade returns in percentage points, useful for comparing groups. The equity curve shows the compounded result.*

---

## What the failure teaches

Each point below is an observation from this test and the hypothesis it suggests. They are starting points for further testing, not proven rules.

### 1. In a trend, price walks the band instead of reverting

**Observed:** 77% of trades were stopped out before price ever reached the middle band. On the chart, strong moves (the 2021 rally, the 2022 decline) show price riding along one band for weeks, generating signal after signal, each of which failed.

**Suggests:** A touch of the band is not a reversal signal on its own. In a trending market, a band touch is often a sign of *strength* in the trend's direction, not exhaustion.

### 2. Fading the dominant trend is expensive

**Observed:** Shorts lost heavily (−0.70% per trade) while longs were roughly flat. Bitcoin rose about 12× over the period, so every short fought the long-term trend.

**Suggests:** Only trading in the direction of the larger trend (for example, longs only when price is above a long-term moving average) may remove the worst trades.

### 3. When reversion does happen, it pays well

**Observed:** Every trade that reached target 1 ended profitable. Trades reaching both targets averaged +11.9%. The problem was never the size of the wins, only how rarely entries survived long enough to get them.

**Suggests:** Because the payoff is lopsided, even a modest improvement in entry quality could matter. The open question is whether stopped trades would have reverted with more room (stop too tight) or never reverted at all (signal too weak). Those call for different fixes.

### 4. The long side's profit came from one trade

**Observed:** A single long entered on 14 March 2020, during the COVID crash, contributed about +72 to the long side's total. All 114 longs together made +30, so **the other 113 longs lost about 42 combined.**

**Suggests:** Results that hinge on one historic event are fragile. Always check whether a strategy's profit survives with its best trade removed.

### 5. Market regime decides the outcome

**Observed:** The best years (2020, 2024) included choppy, range-bound stretches. The worst (2021, 2022) were dominated by sustained trends. 2022, a near-continuous decline, was the worst year at −2.02% per trade.

**Suggests:** Mean reversion likely needs a way to recognise trending conditions and stand aside, rather than trading every signal.

### 6. Targets set during volatile moves can become unreachable

**Observed:** The longest trade lasted 142 days (June to November 2022). After a sharp drop, the bands were very wide and the middle band sat far above price. Since targets were fixed on the signal day, target 1 was out of reach for months, and the trade drifted until it was eventually stopped out.

**Suggests:** Targets that adapt as the bands move, or a time-based exit, may handle post-crash conditions better than fixed levels.

---

## Limitations

- **One asset, one period, one parameter set.** Findings may not hold for other assets, timeframes or settings.
- **Daily candles hide the order of events.** When a day's range touches both the stop and a target, the test assumes the stop hit first. This is conservative but not exact.
- **Spot prices, not perpetual futures.** Yahoo's BTC-USD is an aggregated spot price. Funding rates, which matter for multi-day perpetual positions, are not modelled.
- **Simplified costs.** A flat 0.10% per round trip. Real costs depend on the exchange, fee tier and slippage.
- **Equity is updated only when trades close.** Swings during open trades are not captured, so the true drawdown was likely somewhat worse than reported.
- **Full capital on every trade.** No position sizing or risk-per-trade limit.
- **Known edge cases not yet handled:**
  - If the entry opens beyond target 1 (price already reverted overnight), the trade is still taken and target 1 is filled at a worse-than-entry price.
  - One stopped-out trade shows a small profit, most likely because the entry opened beyond the stop. Both cases are rare but should be fixed.

## Next steps

1. **Diagnose the stop-outs.** For the 192 stopped trades, check whether price reached the middle band within 20 days of the exit. This decides whether to test a wider stop or a stricter entry.
2. **Test one change at a time,** with v1 as the baseline:
   - A trend filter (trade only in the direction of a long-term moving average)
   - An ATR-based stop
   - A stricter entry (the signal candle must close back inside the band)
3. **Fix the two edge cases** above.
4. **Test other assets** (ETH, SOL) to see which findings generalise.
5. **Hold out recent data** when testing any v2 change, so improvements are checked on data they weren't designed around.

---

## Reproducing the results

From the repository root:

```bash
pip install -r requirements.txt
python3 -m strategies.bb_mean_reversion.strategy
```

Outputs are saved to `strategies/bb_mean_reversion/results/`:

- `bb_mean_reversion_summary.csv`: headline metrics
- `trade_log.csv`: every exit, with entry and exit details
- `equity_curve.png`: strategy vs buy-and-hold

---

*This is a research project for educational purposes. Nothing here is investment advice or a recommendation to trade.*