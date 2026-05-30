# 📊 Analisis Data

Direktori ini berisi *Jupyter Notebook* yang memuat eksplorasi data, pengujian, dan pencarian parameter dasar sebelum dimasukkan ke dalam *engine* simulasi.

## 📂 Berkas Utama

### `01_statistik_deskriptif.ipynb`
Tujuan utama notebook ini adalah mencari parameter dasar antrian dari setiap sesi observasi:
- `λ` (Arrival Rate) didapatkan dari rata-rata *Interarrival Time*.
- `μ` (Service Rate) didapatkan dari *1 / rata-rata Waktu Pelayanan*.
- Mengkalkulasi metrik eksisting di lapangan seperti panjang antrian nyata (`Lq`) dan waktu antri nyata (`Wq`) sebagai *baseline* pembanding bagi akurasi simulasi.

### `02_fitting_distribusi.ipynb`
Membuktikan secara statistik model apa yang paling cocok untuk fenomena antrian ini:
- Menguji apakah *Interarrival Time* mengikuti distribusi **Eksponensial** (syarat *Poisson Arrival* dalam teori antrian).
- Menguji bentuk distribusi *Service Time* (apakah *Normal*, *Eksponensial*, atau *General*).
- Menghasilkan nilai *p-value* dan visualisasi *Goodness of Fit*. Kesimpulan dari file ini yang mendasari penggunaan model antrian **M/G/1** di *engine* simulasi.