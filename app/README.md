Buat aplikasinya

Komponen UI yang harus ada:
┌─────────────────────────────────────────────┐
│  SIDEBAR (input)        │  MAIN AREA         │
│  ─────────────────      │  ─────────────     │
│  λ slider               │  Animasi antrian   │
│  μ slider               │  (motor datang,    │
│  Nozzle aktif (1/2/3)   │   mengantri,       │
│  Durasi simulasi        │   dilayani)        │
│  Pilih skenario preset  │                    │
│                         │  Grafik Lq vs waktu│
│                         │  Tabel hasil:      │
│                         │  Wq, Lq, ρ         │
└─────────────────────────────────────────────┘

Skenario yang perlu ada di UI:
- Sesi 2 — Sore peak
- Sesi 3 — Malam peak (default)
- Sesi 4 — Malam sepi
- Skenario kustom (input manual λ, μ, jumlah nozzle)
- Opsional: simulasi skenario tambahan (tambah nozzle, λ naik 50%)