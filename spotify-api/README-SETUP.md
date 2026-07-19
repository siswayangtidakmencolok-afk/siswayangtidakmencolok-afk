# 🎵 Spotify Now Playing — Setup Guide

## Step 1: Buat Spotify App

1. Buka https://developer.spotify.com/dashboard
2. Login dengan akun Spotify kamu
3. Klik **"Create app"**
4. Isi:
   - App name: `GitHub README Widget`
   - Redirect URI: `http://localhost:3000`  ← wajib persis ini
5. Setelah dibuat, catat **Client ID** dan **Client Secret**

---

## Step 2: Dapatkan Refresh Token (SEKALI SAJA)

Buka browser, pergi ke URL ini (ganti `YOUR_CLIENT_ID`):

```
https://accounts.spotify.com/authorize?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=http://localhost:3000&scope=user-read-currently-playing,user-read-recently-played
```

Setelah klik "Allow", browser akan redirect ke:
```
http://localhost:3000/?code=XXXXXX
```

Salin kode `XXXXXX` di URL tersebut.

Lalu jalankan perintah ini di terminal (ganti `CLIENT_ID`, `CLIENT_SECRET`, `CODE`):

**Windows PowerShell:**
```powershell
$body = "grant_type=authorization_code&code=CODE&redirect_uri=http://localhost:3000"
$creds = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("CLIENT_ID:CLIENT_SECRET"))
Invoke-RestMethod -Method Post -Uri "https://accounts.spotify.com/api/token" `
  -Headers @{Authorization="Basic $creds"; "Content-Type"="application/x-www-form-urlencoded"} `
  -Body $body
```

Hasilnya akan ada `refresh_token` — **SIMPAN INI!**

---

## Step 3: Deploy ke Vercel

1. Buka https://vercel.com dan login
2. Klik **"Add New → Project"**
3. Import repository GitHub kamu: `siswayangtidakmencolok-afk`
4. **Root Directory:** set ke `spotify-api`
5. Klik **"Environment Variables"** dan tambahkan:

| Key | Value |
|-----|-------|
| `SPOTIFY_CLIENT_ID` | Client ID dari Step 1 |
| `SPOTIFY_CLIENT_SECRET` | Client Secret dari Step 1 |
| `SPOTIFY_REFRESH_TOKEN` | Refresh token dari Step 2 |

6. Klik **Deploy**!

Vercel URL kamu akan seperti: `https://fhazwan-spotify-now-playing.vercel.app`

---

## Step 4: Update README

Di `README.md`, ganti placeholder URL:
```markdown
[![Spotify](https://fhazwan-spotify-now-playing.vercel.app/api/spotify)](https://open.spotify.com/user/YOUR_SPOTIFY_USERNAME)
```

Dengan URL Vercel deployment kamu yang sebenarnya.

---

## ✅ Selesai!

Widget akan otomatis update setiap kali README dimuat. Kalau sedang tidak main musik, akan tampil lagu fallback (Cook Pardon - Lvbel C5).
