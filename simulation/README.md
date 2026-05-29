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

---

## 🗃️ Alur Pengambilan Data (Data Flow)

Parameter yang digunakan dalam simulasi ini (`λ`, `μ`, `Lq`, `Wq`) **tidak dibuat secara sembarangan**, melainkan diekstrak langsung dari hasil analisis statistik data riil.

1. **Sumber Data:** Nilai-nilai empiris di-generate oleh file notebook `analysis/01_statistik_deskriptif.ipynb`.
2. **Pemetaan Parameter:**
   - `λ (Arrival Rate)` pada notebook dimasukkan ke parameter `lam` pada tiap skenario.
   - `μ (Service Rate)` pada notebook dimasukkan ke parameter `mu` (dengan konversi `1 / Rata-rata Waktu Pelayanan`).
   - `Lq` (Panjang Antrian) dan `Wq` (Waktu Tunggu) dari notebook digunakan sebagai **Data Empiris (Emp)** di fungsi `compare_with_empirical()` untuk mengukur tingkat akurasi (error) simulasi terhadap kenyataan.
3. **Penyisipan ke Engine:** Data-data tersebut di-*hardcode* di dalam *dictionary* `scenarios` dan `empirical_data` pada `simulation/engine.py`. 

*(Jika di masa depan ada update data mentah baru, Anda hanya perlu menjalankan ulang notebook `01`, lalu meng-update angka-angkanya ke dalam fungsi `run_all_scenarios` di `engine.py`)*.