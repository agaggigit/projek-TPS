Buat file .ipynb

Yang 01_statistik_deskriptif.ipynb
Output yang diharapkan:
┌──────────┬──────┬──────┬──────┬────────┬──────┐
│ Sesi     │  λ   │  μ   │  ρ   │  Lq    │  Wq  │
├──────────┼──────┼──────┼──────┼────────┼──────┤
│ Sesi 2   │ ...  │ ...  │ ...  │  6.0   │ 264s │
│ Sesi 3   │ ...  │ ...  │ ...  │ 11.92  │ 515s │
│ Sesi 4   │ ...  │ ...  │ ...  │  6.33  │ 299s │
└──────────┴──────┴──────┴──────┴────────┴──────┘

Yang 02_fitting_distribusi.ipynb
Yang diuji:
- Interarrival time  →  apakah ~ Eksponensial? (= kedatangan Poisson)
- Service time       →  apakah ~ Eksponensial? atau ~ Normal? atau lainnya?

Output:
- Nilai p-value tiap uji
- Grafik perbandingan: histogram data vs kurva distribusi teoritis
- Kesimpulan: model M/M/1 atau M/G/1