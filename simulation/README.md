Ya buat simulasi

Input parameter:
- λ (bisa diubah)
- μ (bisa diubah)  
- c = jumlah nozzle (bisa diubah)
- durasi simulasi
- distribusi yang dipakai (dari hasil Kode 2)

Output per simulasi:
- Rata-rata Wq (waktu tunggu)
- Rata-rata Lq (panjang antrian)
- ρ (utilisasi nozzle)
- Timeline: grafik panjang antrian vs waktu
- Perbandingan dengan nilai empiris (dari data kalian)

Skenario yang perlu dijalankan minimal:
| Skenario | Deskripsi |
| ------- | -------- |
| S1 | Sesi 2 — Sore peak (parameter dari data nyata) |
| S2 | Sesi 3 — Malam peak (paling padat) |
| S3 | Sesi 4 — Malam sepi |
| S4 | Hipotetis: tambah 1 nozzle di kondisi Sesi 3 |
| S5 | Hipotetis: λ naik 50% (misal ada event di Sudirman) |

Ringkasan Urutan Pembuatan
generate_interarrival / generate_service   ← buat duluan, paling simple
        │
        ▼
    customer()                             ← proses SimPy satu pelanggan
        │
        ▼
    arrival_generator()                    ← spawn pelanggan + catat timeline
        │
        ▼
    run_simulation()                       ← rakit semuanya jadi satu simulasi
        │
        ▼
    SCENARIOS + run_all_scenarios()        ← jalankan 5 skenario sekaligus
        │
        ▼
    compare_with_empirical()               ← bandingkan dengan data nyata