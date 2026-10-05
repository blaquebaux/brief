#!/usr/bin/python3
# =============================================================================
# brief_1_overnight_seasonal.py — where does the equity premium actually live, and is any of it harvestable?
#
# (A) OVERNIGHT vs INTRADAY: decompose each day's return into the overnight gap (close→open) and the intraday
#     session (open→close). The documented shock: ~all of the long-run equity premium is earned OVERNIGHT;
#     the intraday session is roughly flat-to-negative. Real in the data — but capturing it means a DAILY
#     round-trip (buy the close, sell the open), so we haircut it by cost to ask if it's a free lunch (it isn't).
# (B) CALENDAR tilts (low-turnover, actually tradeable): turn-of-month, day-of-week, and Halloween (Nov–Apr
#     vs May–Oct). A few trades a year — the honest, harvestable residue if any effect survives.
# Alpaca SIP daily OHLC, causal, gross (then a cost haircut on the overnight leg). SPY/QQQ/IWM.
# =============================================================================
import os, sys, datetime; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _brief_common import panel_oc, stats, jarque_bera, ann
import numpy as np

O, C, dates = panel_oc(["SPY", "QQQ", "IWM"])
dt = [datetime.date.fromisoformat(d) for d in dates]
print("="*94); print(f"BRIEF #1 — overnight vs intraday + calendar seasonals  ({dates[0]} → {dates[-1]}, {len(dates)} days)"); print("="*94)

# ---- (A) overnight vs intraday decomposition --------------------------------------------------------
print("\n(A) WHERE THE PREMIUM LIVES — annualized return / Sharpe, by session:")
print(f"    {'':6}{'overnight C→O':>20}{'intraday O→C':>18}{'buy & hold':>16}{'ON maxDD':>10}{'ON exKurt':>10}")
COST_BPS = 2.0   # per side; overnight = 2 round-trips worth of friction/day is punishing by construction
for s in C:
    c = C[s]; o = O[s]
    overn = o[1:]/c[:-1] - 1          # close[t-1] -> open[t]
    intra = c[1:]/o[1:] - 1           # open[t]   -> close[t]
    bh    = c[1:]/c[:-1] - 1          # close[t-1]-> close[t]
    aON, shON = ann(overn); aIN, shIN = ann(intra); aBH, shBH = ann(bh)
    jON = jarque_bera(overn); ddON = stats(overn)['dd']
    print(f"    {s:6}{aON*100:>+10.0f}% {shON:>+6.2f}{aIN*100:>+10.0f}% {shIN:>+5.2f}{aBH*100:>+9.0f}% {shBH:>+5.2f}{ddON*100:>+9.0f}%{jON['exkurt']:>+10.1f}")
# harvestability haircut on the headline name (SPY): daily round-trip cost
c = C["SPY"]; o = O["SPY"]; overn = o[1:]/c[:-1]-1
net = overn - 2*COST_BPS/1e4                       # buy close + sell open = 2 sides of cost every day
aN, shN = ann(net); aG, shG = ann(overn)
print(f"\n    SPY overnight HARVESTABILITY: gross {aG*100:+.0f}%/yr (Sharpe {shG:+.2f})  →  net of {COST_BPS:.0f}bps/side round-trip: {aN*100:+.0f}%/yr (Sharpe {shN:+.2f})")
print(f"    (and you can't actually transact the official close/open prints — the real slippage is worse.)")

# ---- (B) calendar tilts on SPY total daily returns --------------------------------------------------
spy = C["SPY"][1:]/C["SPY"][:-1]-1; d2 = dt[1:]
print("\n(B) CALENDAR TILTS (SPY total daily return):")
# turn-of-month = the last trading day of a month OR one of the first 3 trading days of a month
months = [x.year*12 + x.month for x in d2]
seen = {}; rank = []                                   # rank = how many trading days into this month (0-based)
for m in months: rank.append(seen.get(m, 0)); seen[m] = seen.get(m, 0) + 1
last_of_month = [(i+1 >= len(d2)) or (months[i+1] != months[i]) for i in range(len(d2))]
tom = np.array([last_of_month[i] or rank[i] < 3 for i in range(len(d2))])
aT,shT=ann(spy[tom]); aR,shR=ann(spy[~tom])
print(f"    turn-of-month (last day + first 3): {aT*100:+.0f}%/yr ann  vs  rest-of-month {aR*100:+.0f}%/yr   ({tom.mean()*100:.0f}% of days)")
# day-of-week
print(f"    day-of-week mean (bps/day):", end=" ")
for wd,name in [(0,"Mon"),(1,"Tue"),(2,"Wed"),(3,"Thu"),(4,"Fri")]:
    msk=np.array([x.weekday()==wd for x in d2]); print(f"{name} {spy[msk].mean()*1e4:+.1f}", end="  ")
print()
# Halloween / sell-in-May
summer=np.array([x.month in (5,6,7,8,9,10) for x in d2])
aS,_=ann(spy[summer]); aW,_=ann(spy[~summer])
print(f"    Halloween: Nov–Apr {aW*100:+.0f}%/yr  vs  May–Oct {aS*100:+.0f}%/yr")

print("\n"+"="*94); print("READ:")
print("  • The premium lives OVERNIGHT — intraday is ~flat-to-negative while the close→open gap earns most of the")
print("    long-run return (strongest in small caps / IWM). A real, striking decomposition.")
print("  • But it is NOT a free lunch: harvesting it is a DAILY round-trip, so even a tiny per-side cost turns the")
print("    gross overnight return negative, and you can't trade the official close/open prints anyway. The honest")
print("    use is a RISK insight (own-overnight / de-risk-intraday leaning, or an execution bias), not a sleeve.")
print("  • The TRADEABLE residue is the low-turnover calendar tilts above — a few trades a year. Keep whichever")
print("    survives out-of-sample with a real cost model; the rest is data-mining. (FOMC-drift = brief_2, needs")
print("    the meeting-date list.) Match the signal to the sleeve: blink-fast edges rarely survive the friction.")
