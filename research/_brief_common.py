#!/usr/bin/python3
# =============================================================================
# _brief_common.py — shared helpers for Blaque Baux BRIEF (calendar / seasonal / overnight premia).
# Alpaca SIP daily OHLC bars; reads ALPACA_KEY_ID / ALPACA_SECRET_KEY from env. Read-only.
#
# BRIEF = the premia you earn in a blink: the OVERNIGHT (close→open) return, turn-of-month, day-of-week,
# the pre-FOMC drift, and the Halloween (sell-in-May) seasonal. These are the most-documented calendar
# anomalies — orthogonal to trend/value/carry — but the honest question is always HARVESTABILITY: an effect
# that is real in the decomposition can be un-tradeable once you price the turnover (overnight = a daily
# round-trip; calendar tilts = a few trades a year). Verdicts lean on Sharpe AFTER a cost haircut, and on
# Jarque-Bera + max-drawdown because these anomalies hide fat tails (the crash happens overnight too).
# =============================================================================
import os, json, urllib.request, math, datetime
import numpy as np

H = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"], "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET_KEY"]}
START, END = "2016-01-01", "2026-08-01"
_cache = {}

def bars_oc(s):
    """date -> (open, close), split/div-adjusted."""
    if s in _cache: return _cache[s]
    u = (f"https://data.alpaca.markets/v2/stocks/bars?symbols={s}&timeframe=1Day"
         f"&start={START}&end={END}&adjustment=all&feed=sip&limit=10000")
    try:
        d = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=40))
        _cache[s] = {b["t"][:10]: (b["o"], b["c"]) for b in d.get("bars", {}).get(s, [])}
    except Exception:
        _cache[s] = {}
    return _cache[s]

def panel_oc(syms):
    """Aligned OHLC panel: returns (O, C, dates) with O[t],C[t] the open/close on dates[t]."""
    D = {s: bars_oc(s) for s in syms}; D = {s: v for s, v in D.items() if len(v) > 250}
    if not D: return {}, {}, []
    u = list(D); dates = sorted(set.intersection(*[set(D[s]) for s in u]))
    O = {s: np.array([D[s][d][0] for d in dates], float) for s in u}
    C = {s: np.array([D[s][d][1] for d in dates], float) for s in u}
    return O, C, dates

# --- fat-tail toolkit (family-canonical; numpy-only) ---------------------------------------------
def stats(r):
    r = np.asarray(r, float); r = r[np.isfinite(r)]
    if len(r) < 30 or r.std() == 0: return dict(sh=float('nan'), cagr=float('nan'), dd=float('nan'), vol=float('nan'))
    cum = np.cumprod(1 + r)
    return dict(sh=r.mean()/r.std()*math.sqrt(252), cagr=cum[-1]**(252/len(r))-1,
                dd=(cum/np.maximum.accumulate(cum)-1).min(), vol=r.std()*math.sqrt(252))

def jarque_bera(r):
    r = np.asarray(r, float); r = r[np.isfinite(r)]; n = len(r)
    if n < 30 or r.std() == 0: return dict(jb=float('nan'), p=float('nan'), skew=float('nan'), exkurt=float('nan'))
    z = (r - r.mean()) / r.std(); sk = float(np.mean(z**3)); ku = float(np.mean(z**4) - 3.0)
    jb = n/6.0*(sk**2 + ku**2/4.0)
    return dict(jb=jb, p=math.exp(-jb/2.0), skew=sk, exkurt=ku)

def ann(r):
    """annualized arithmetic return + Sharpe of a daily-return stream (for the seasonal legs)."""
    r = np.asarray(r, float); r = r[np.isfinite(r)]
    if len(r) < 20 or r.std() == 0: return (float('nan'), float('nan'))
    return (r.mean()*252, r.mean()/r.std()*math.sqrt(252))

def jensens_alpha(r, rb, rf=0.0):
    r = np.asarray(r, float); rb = np.asarray(rb, float); m = np.isfinite(r) & np.isfinite(rb)
    r, rb = r[m], rb[m]
    if len(r) < 30 or np.var(rb) == 0: return dict(alpha_ann=float('nan'), beta=float('nan'))
    beta = float(np.cov(r, rb)[0, 1] / np.var(rb))
    return dict(alpha_ann=(r.mean() - beta*rb.mean())*252, beta=beta)
