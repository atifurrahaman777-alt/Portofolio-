# Laporan Unslop — Mann'zz Portfolio & Tools

> **Status:** tampilan selesai dirapikan dan dinaikkan jadi "karya desain", bukan sekadar bersih. Arah: **ruang kerja developer yang tenang dan teliti** — permukaan netral, tipografi display + mono, aksen mengikuti 6 tema yang sudah dipilih. Verifikasi lokal: 9 halaman · desktop 1440×900 & mobile 390×844 · nol overflow · nol error JS · 6 tema × terang/gelap lolos.

## Perubahan terakhir

**Beranda**
- Hero baru: identitas, kicker, judul besar, lede, aksi, 3 statistik, dan terminal hidup dengan animasi baris + kursor.
- Intro + komunitas jadi dua kartu sejajar; judul proyek diberi indeks `01`–`04` dan tag asli.
- Proyek **02 dan 03 sejajar**: kartu lebar sama, tinggi sama, tag rata bawah. Di layar ≤760 px keduanya jadi satu kolom penuh (sebelumnya dua kolom timpang 142 px vs 176 px).

**Semua permukaan**
- Panel masuk jadi sheet modal terpusat: kicker, judul, deskripsi, tab segmen, pembatas "atau", tombol provider, penutup layar.
- Pemutar musik jadi kartu pemutar: cover persegi, meta display, progress mono, kontrol bundar; mini-player ikut dirapikan.
- Tab game/alat/sosial jadi katalog berindeks (`01`, `02`, …) dengan label file mono; header section memakai garis tipis.
- Game page: nav segmen, papan & kontrol seragam; teks remaining diterjemahkan (Mudah/Sedang/Sulit, Kamu menang, Bot menang, Waktu, dll.).
- Editor, temp mail, downloader, amfind, amprem, chat, reactch memakai satu sistem kartu, input, dan tipografi yang sama. Halaman terkunci mendapat kartu gate "Akses terbatas" yang rapi.
- `clean.css` memakai cache-buster `?v=8` di semua halaman.

## Tema terang / gelap — lebih jelas

| Token | Terang | Gelap |
| --- | --- | --- |
| Kanvas | `#e7ecf3` | `#080a10` |
| Permukaan | `#ffffff` | `#1b2130` |
| Permukaan timbul | `#e4eaf2` | `#262e3d` |
| Garis | `#c5cedb` | `#434e60` |
| Teks utama | `#0f172a` | `#f4f6fa` |
| Teks sekunder | `#3c4656` | `#bac3d2` |

- Kontras kanvas ↔ permukaan naik dari 1.13 menjadi **1.19** (terang) dan dari 1.14 menjadi **1.23** (gelap), jadi batas kartu/header terlihat tanpa bayangan tebal.
- Kontras teks ↔ permukaan: **17.85** (terang) dan **14.85** (gelap) — jauh di atas batas 4.5 WCAG AA.
- Tombol tema di header kini menampilkan label **Terang / Gelap** (desktop) selain ikon; di mobile tetap ringkas ikon saja.
- Enam aksen (`mono`, `biru`, `hijau`, `kuning`, `pink`, `oranye`) dan `on-accent` tetap berfungsi di kedua mode.

## Verifikasi akhir

| Pemeriksaan | Hasil |
| --- | --- |
| 9 halaman × desktop & mobile | `docW` sama dengan viewport, 0 overflow |
| Error JS | 0 di semua halaman |
| Beranda desktop / mobile | 0 bold, 0 uppercase, tinggi 2296 / 3064 px |
| Proyek 02 & 03 desktop | lebar 317 px each, tag sejajar di `y=1461` |
| Proyek 02 & 03 mobile | lebar 334 px each, satu kolom |
| 6 aksen × 2 mode | lolos, kontras teks ≥ 14.8 |
| Halaman terkunci | kartu gate tampil rapi di desktop & mobile |

## Catatan
- File `fix*.py`, backup `index.html.before-*`, dan perubahan user yang belum di-commit tidak dihapus.
- Sisa bold di `games.html` (45) dan `editor.html` (72) adalah teks tombol/syntax editor yang memang perlu penekanan, bukan dekorasi.
