"""
Generate animated SVG for IDX Stock Portfolio
Stocks: ASII (Astra International) & ARCI (Archi Indonesia - Gold Mining)
Outputs to: output/stock_portfolio.svg
"""

import yfinance as yf
import datetime
import os
import json

# ─── CONFIG ───────────────────────────────────────────────────────────────────
STOCKS = [
    {"ticker": "ASII.JK", "name": "Astra International", "emoji": "🚗", "sector": "Otomotif & Diversified"},
    {"ticker": "ARCI.JK", "name": "Archi Indonesia",     "emoji": "⛏️",  "sector": "Gold Mining"},
]

OUTPUT_DIR = "output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "stock_portfolio.svg")

# ─── FETCH DATA ───────────────────────────────────────────────────────────────
def fetch_stock(ticker):
    try:
        data = yf.Ticker(ticker)
        hist  = data.history(period="5d", interval="1d")
        info  = data.fast_info

        if hist.empty:
            return None

        price_now  = float(hist["Close"].iloc[-1])
        price_prev = float(hist["Close"].iloc[-2]) if len(hist) >= 2 else price_now
        change_pct = ((price_now - price_prev) / price_prev) * 100
        change_abs = price_now - price_prev

        # Sparkline from last 5 days
        closes = [float(c) for c in hist["Close"].tolist()]

        return {
            "price":      price_now,
            "prev":       price_prev,
            "change_pct": change_pct,
            "change_abs": change_abs,
            "closes":     closes,
        }
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return None

# ─── SPARKLINE SVG ────────────────────────────────────────────────────────────
def sparkline_path(closes, x_offset, y_offset, width=80, height=30):
    if len(closes) < 2:
        return ""
    mn = min(closes)
    mx = max(closes)
    rng = mx - mn or 1
    pts = []
    for i, c in enumerate(closes):
        x = x_offset + (i / (len(closes) - 1)) * width
        y = y_offset + height - ((c - mn) / rng) * height
        pts.append(f"{x:.1f},{y:.1f}")
    return "M " + " L ".join(pts)

# ─── GENERATE SVG ─────────────────────────────────────────────────────────────
def generate_svg(stocks_data):
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7)))
    ts  = now.strftime("%d %b %Y • %H:%M WIB")

    card_w  = 480
    card_h  = 80
    gap     = 16
    padding = 20
    total_h = padding + len(stocks_data) * (card_h + gap) + 50 + padding
    total_w = 540

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{total_w}" height="{total_h}" viewBox="0 0 {total_w} {total_h}">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%"   stop-color="#0d1117"/>
      <stop offset="100%" stop-color="#161b22"/>
    </linearGradient>
    <linearGradient id="card_up" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%"   stop-color="#0f2027"/>
      <stop offset="100%" stop-color="#1a2f1a"/>
    </linearGradient>
    <linearGradient id="card_dn" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%"   stop-color="#2f0f0f"/>
      <stop offset="100%" stop-color="#1a0f0f"/>
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
      <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <style>
      @keyframes pulse {{
        0%,100% {{ opacity:1; }}
        50%      {{ opacity:0.5; }}
      }}
      .live {{ animation: pulse 2s ease-in-out infinite; }}
    </style>
  </defs>

  <!-- Background -->
  <rect width="{total_w}" height="{total_h}" rx="16" fill="url(#bg)"/>

  <!-- Header -->
  <text x="28" y="36" font-family="Segoe UI,system-ui,sans-serif" font-size="15" font-weight="700" fill="#EC4899">📈 My Stock Portfolio — IDX</text>
  <circle cx="{total_w-50}" cy="28" r="5" fill="#22c55e" class="live"/>
  <text x="{total_w-40}" y="33" font-family="monospace" font-size="11" fill="#22c55e">LIVE</text>
'''

    for i, (meta, sd) in enumerate(zip(STOCKS, stocks_data)):
        if sd is None:
            continue

        y_card  = padding + 20 + i * (card_h + gap)
        up      = sd["change_pct"] >= 0
        color   = "#22c55e" if up else "#ef4444"
        sign    = "+" if up else ""
        grad    = "card_up" if up else "card_dn"
        arrow   = "▲" if up else "▼"
        spark   = sparkline_path(sd["closes"], total_w - 120, y_card + 10, width=90, height=50)

        svg += f'''
  <!-- Card {i}: {meta["ticker"]} -->
  <rect x="16" y="{y_card}" width="{card_w}" height="{card_h}" rx="10" fill="url(#{grad})" stroke="{color}" stroke-width="1" stroke-opacity="0.4"/>

  <!-- Emoji & Name -->
  <text x="32" y="{y_card+24}" font-family="Segoe UI Emoji,sans-serif" font-size="18">{meta["emoji"]}</text>
  <text x="56" y="{y_card+22}" font-family="Segoe UI,system-ui,sans-serif" font-size="13" font-weight="700" fill="#f0f6fc">{meta["ticker"].replace(".JK","")}</text>
  <text x="56" y="{y_card+38}" font-family="Segoe UI,system-ui,sans-serif" font-size="10" fill="#8b949e">{meta["name"]}</text>
  <text x="56" y="{y_card+52}" font-family="Segoe UI,system-ui,sans-serif" font-size="10" fill="#8b949e">{meta["sector"]}</text>

  <!-- Price -->
  <text x="220" y="{y_card+28}" font-family="'Courier New',monospace" font-size="16" font-weight="700" fill="#f0f6fc" filter="url(#glow)">Rp {sd["price"]:,.0f}</text>
  <text x="220" y="{y_card+46}" font-family="monospace" font-size="11" fill="{color}">{arrow} {sign}{sd["change_pct"]:.2f}%  ({sign}{sd["change_abs"]:,.0f})</text>

  <!-- Sparkline -->
  <path d="{spark}" fill="none" stroke="{color}" stroke-width="2" stroke-opacity="0.9"/>
'''

    # Footer timestamp
    svg += f'''
  <!-- Footer -->
  <text x="28" y="{total_h - 12}" font-family="monospace" font-size="10" fill="#484f58">🕐 Last updated: {ts}</text>
  <text x="{total_w - 120}" y="{total_h - 12}" font-family="monospace" font-size="10" fill="#484f58">via yfinance</text>
</svg>'''

    return svg

# ─── MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Fetching stock data...")
    stocks_data = [fetch_stock(s["ticker"]) for s in STOCKS]

    for meta, sd in zip(STOCKS, stocks_data):
        if sd:
            sign = "+" if sd["change_pct"] >= 0 else ""
            print(f"  {meta['ticker']}: Rp {sd['price']:,.0f}  ({sign}{sd['change_pct']:.2f}%)")
        else:
            print(f"  {meta['ticker']}: FAILED to fetch")

    svg = generate_svg(stocks_data)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(svg)

    print(f"\n✅ SVG written to {OUTPUT_FILE}")
