# Blaque Baux Brief

**The premia you earn in a blink — overnight, seasonal, calendar. Real in the decomposition, mostly gone in the friction.**

Brief is a member of the Blaque Baux family. It tests the most-documented **calendar anomalies** — the overnight
(close→open) return, turn-of-month, day-of-week, Halloween (sell-in-May), and the pre-FOMC drift — which are
orthogonal to trend/value/carry. The family's question is never "is the effect there?" but "does it survive the
*turnover*?" A blink-fast edge that needs a daily round-trip usually doesn't.

> **Not investment advice.** Educational/research software. See [DISCLAIMER](DISCLAIMER.md) and [LICENSE](LICENSE).

```bash
python3 research/brief_1_overnight_seasonal.py   # needs Alpaca data keys in the environment
```

## The headline finding (honest)

[`research/brief_1_overnight_seasonal.py`](research/brief_1_overnight_seasonal.py) — 2016→2026, SIP daily OHLC:

**Where the equity premium actually lives — annualized return / Sharpe, by session:**

| | overnight (C→O) | intraday (O→C) | buy & hold |
|---|---|---|---|
| SPY | **+9% (+0.82)** | +6% (+0.46) | +16% |
| QQQ | **+13% (+0.93)** | +8% (+0.45) | +21% |
| IWM | **+15% (+1.05)** | **−2% (−0.10)** | +13% |

The premium is earned **overnight** — strongest in small caps, where the intraday session is actually *negative*.
A real, striking decomposition.

**But it is not a free lunch.** Harvesting it means a **daily round-trip** (buy the close, sell the open), so
SPY's +9% gross overnight return goes to **−1%/yr** at just 2bps/side — and you can't transact the official
close/open prints anyway. It's a **risk/execution insight** (lean your holdings overnight, bias execution toward
the open), not a tradeable sleeve.

**The calendar tilts have decayed.** In this sample turn-of-month (+16% vs +15%), Halloween (+16% vs +15%), and
day-of-week are all weak-to-noise — the classic effects faded post-publication, exactly as the anomaly-decay
literature predicts.

## Verdict

**An honest near-null on tradeability, with a genuine decomposition insight.** The overnight premium is real but
un-harvestable net of friction; the seasonal tilts have decayed. Brief's value is the *risk lens*, not an alpha
sleeve — *match the signal to the sleeve: blink-fast edges rarely survive the friction.* Pre-FOMC drift (needs the
scheduled meeting-date list) is the one remaining leg worth a dedicated `brief_2`.

## Status
**Research — near-null on tradeability; kept as a decomposition/execution insight.** No live rail.

## Layout
```
research/  _brief_common.py            — OHLC panel + fat-tail toolkit
           brief_1_overnight_seasonal.py — overnight-vs-intraday + turn-of-month/day-of-week/Halloween
```

## The Blaque Baux family
One sleeve of the **Blaque Baux** family. The [core repo](https://github.com/blaquebaux/base) is the
base/blueprint and holds the [full family roster](https://github.com/blaquebaux/base#the-blaquebaux-family).

## License
[MIT](LICENSE). (c) 2026 Carter Warrens.
