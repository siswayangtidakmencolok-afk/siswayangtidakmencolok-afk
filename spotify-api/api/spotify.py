"""
Spotify Now Playing — Vercel Serverless API
Returns an SVG image showing currently playing track (or a beautiful fallback).

Environment Variables needed in Vercel:
  SPOTIFY_CLIENT_ID     — from developer.spotify.com
  SPOTIFY_CLIENT_SECRET — from developer.spotify.com
  SPOTIFY_REFRESH_TOKEN — generated once (see README-SETUP.md)

Embed in GitHub README:
  ![Now Playing](https://YOUR-APP.vercel.app/api/spotify)
"""

import os
import base64
import json
import urllib.request
import urllib.parse
import urllib.error
from http.server import BaseHTTPRequestHandler


# ─── FALLBACK SONG (shown when not playing anything) ──────────────────────────
FALLBACK = {
    "name":    "Cook Pardon",
    "artist":  "Lvbel C5",
    "album":   "Portofolio Fhazwan",
    "cover":   "",          # leave blank for gradient cover
    "track_id": "06KyNuuMOX1ROXRhj787tj",
    "is_playing": False,
}

# ─── SPOTIFY API HELPERS ──────────────────────────────────────────────────────
def get_access_token():
    client_id     = os.environ.get("SPOTIFY_CLIENT_ID", "")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET", "")
    refresh_token = os.environ.get("SPOTIFY_REFRESH_TOKEN", "")

    if not all([client_id, client_secret, refresh_token]):
        return None

    creds   = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    payload = urllib.parse.urlencode({
        "grant_type":    "refresh_token",
        "refresh_token": refresh_token,
    }).encode()

    req = urllib.request.Request(
        "https://accounts.spotify.com/api/token",
        data=payload,
        headers={
            "Authorization": f"Basic {creds}",
            "Content-Type":  "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read())["access_token"]
    except Exception:
        return None


def get_now_playing(token):
    req = urllib.request.Request(
        "https://api.spotify.com/v1/me/player/currently-playing",
        headers={"Authorization": f"Bearer {token}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status == 204:
                return None          # nothing playing
            data = json.loads(resp.read())
            item = data.get("item", {})
            if not item:
                return None
            return {
                "name":       item["name"],
                "artist":     ", ".join(a["name"] for a in item["artists"]),
                "album":      item["album"]["name"],
                "cover":      item["album"]["images"][0]["url"] if item["album"]["images"] else "",
                "track_id":   item["id"],
                "is_playing": data.get("is_playing", False),
                "progress_ms": data.get("progress_ms", 0),
                "duration_ms": item.get("duration_ms", 1),
            }
    except urllib.error.HTTPError as e:
        if e.code in (204, 401, 403):
            return None
        raise
    except Exception:
        return None


# ─── SVG GENERATOR ────────────────────────────────────────────────────────────
def build_svg(track):
    is_playing  = track.get("is_playing", False)
    name        = track["name"][:32] + ("…" if len(track["name"]) > 32 else "")
    artist      = track["artist"][:36] + ("…" if len(track["artist"]) > 36 else "")
    album       = track["album"][:38] + ("…" if len(track["album"]) > 38 else "")
    track_id    = track.get("track_id", "")
    spotify_url = f"https://open.spotify.com/track/{track_id}" if track_id else "https://open.spotify.com"

    progress_ms = track.get("progress_ms", 0)
    duration_ms = track.get("duration_ms", 1)
    progress_pct = min((progress_ms / duration_ms) * 100, 100) if duration_ms else 0

    def fmt_ms(ms):
        s = ms // 1000
        return f"{s // 60}:{s % 60:02d}"

    progress_str = fmt_ms(progress_ms)
    duration_str = fmt_ms(duration_ms)

    # Colors
    accent   = "#1DB954"   # Spotify green
    bg_dark  = "#0d1117"
    bg_card  = "#161b22"
    text_pri = "#f0f6fc"
    text_sec = "#8b949e"
    bar_bg   = "#30363d"

    status_dot  = accent if is_playing else "#8b949e"
    status_text = "Now Playing" if is_playing else "Recently Played"
    status_anim = 'class="pulse"' if is_playing else ""

    # Equalizer bars animation (only when playing)
    eq_bars = ""
    if is_playing:
        heights = [12, 20, 8, 16, 10, 18, 14]
        delays  = [0, 0.15, 0.3, 0.1, 0.25, 0.05, 0.2]
        for idx, (h, d) in enumerate(zip(heights, delays)):
            bx = 20 + idx * 8
            eq_bars += f'''
    <rect x="{bx}" y="{45 - h}" width="5" height="{h}" rx="2" fill="{accent}">
      <animate attributeName="height" values="{h};{max(4,h-8)};{h+4};{h}" dur="0.8s" begin="{d}s" repeatCount="indefinite"/>
      <animate attributeName="y" values="{45-h};{45-max(4,h-8)};{45-h-4};{45-h}" dur="0.8s" begin="{d}s" repeatCount="indefinite"/>
    </rect>'''
    else:
        # Static bars
        heights = [6, 10, 4, 8, 5, 9, 7]
        for idx, h in enumerate(heights):
            bx = 20 + idx * 8
            eq_bars += f'<rect x="{bx}" y="{45-h}" width="5" height="{h}" rx="2" fill="{text_sec}" opacity="0.5"/>'

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="480" height="130" viewBox="0 0 480 130">
  <defs>
    <linearGradient id="bg_grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%"   stop-color="#0d1117"/>
      <stop offset="100%" stop-color="#1a1f2e"/>
    </linearGradient>
    <linearGradient id="cover_grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%"   stop-color="#1DB954"/>
      <stop offset="100%" stop-color="#191414"/>
    </linearGradient>
    <linearGradient id="bar_fill" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%"   stop-color="#1DB954"/>
      <stop offset="100%" stop-color="#1ed760"/>
    </linearGradient>
    <clipPath id="card_clip">
      <rect width="480" height="130" rx="14"/>
    </clipPath>
    <clipPath id="cover_clip">
      <rect x="16" y="16" width="90" height="90" rx="8"/>
    </clipPath>
    <style>
      @keyframes pulse {{
        0%,100% {{ opacity:1; r:5; }}
        50%      {{ opacity:0.4; r:4; }}
      }}
      @keyframes scan {{
        0%   {{ transform: translateX(-100%); }}
        100% {{ transform: translateX(200%); }}
      }}
      .pulse {{ animation: pulse 1.5s ease-in-out infinite; }}
      .scan  {{ animation: scan 2.5s linear infinite; }}
    </style>
  </defs>

  <!-- Background -->
  <rect width="480" height="130" rx="14" fill="url(#bg_grad)" clip-path="url(#card_clip)"/>
  <!-- Left accent stripe -->
  <rect width="4" height="130" fill="{accent}" opacity="0.8"/>

  <!-- Album Cover (gradient placeholder if no image) -->
  <rect x="16" y="16" width="90" height="90" rx="8" fill="url(#cover_grad)" clip-path="url(#cover_clip)"/>
  <text x="61" y="68" text-anchor="middle" font-size="28" font-family="Segoe UI Emoji">🎵</text>

  <!-- Equalizer (bottom-left of cover) -->
  <g transform="translate(18, 55)">{eq_bars}
  </g>

  <!-- Spotify logo -->
  <text x="16" y="116" font-family="Segoe UI Emoji" font-size="14">🟢</text>
  <text x="34" y="116" font-family="'Segoe UI',sans-serif" font-size="10" font-weight="700" fill="{accent}">Spotify</text>

  <!-- Status dot + label -->
  <circle cx="122" cy="24" r="5" fill="{status_dot}" {status_anim}/>
  <text x="133" y="29" font-family="'Segoe UI',sans-serif" font-size="11" fill="{status_dot}" font-weight="600">{status_text}</text>

  <!-- Track name -->
  <text x="122" y="55" font-family="'Segoe UI',system-ui,sans-serif" font-size="16" font-weight="700" fill="{text_pri}">{name}</text>

  <!-- Artist -->
  <text x="122" y="73" font-family="'Segoe UI',sans-serif" font-size="12" fill="{text_sec}">{artist}</text>

  <!-- Album -->
  <text x="122" y="89" font-family="'Segoe UI',sans-serif" font-size="10" fill="{text_sec}" opacity="0.8">💿 {album}</text>

  <!-- Progress bar -->
  <rect x="122" y="100" width="330" height="4" rx="2" fill="{bar_bg}"/>
  <rect x="122" y="100" width="{330 * progress_pct / 100:.1f}" height="4" rx="2" fill="url(#bar_fill)"/>

  <!-- Progress time -->
  <text x="122" y="118" font-family="monospace" font-size="9" fill="{text_sec}">{progress_str}</text>
  <text x="448" y="118" font-family="monospace" font-size="9" fill="{text_sec}" text-anchor="end">{duration_str}</text>
</svg>'''

    return svg


# ─── VERCEL HANDLER ───────────────────────────────────────────────────────────
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        token = get_access_token()
        track = None

        if token:
            track = get_now_playing(token)

        if not track:
            track = FALLBACK

        svg = build_svg(track)

        self.send_response(200)
        self.send_header("Content-Type", "image/svg+xml")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(svg.encode("utf-8"))

    def log_message(self, format, *args):
        pass
