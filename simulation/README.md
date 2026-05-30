# ⚙️ Engine Simulasi Antrian SPBU

Direktori ini memuat inti *engine* simulasi antrian kendaraan menggunakan library **SimPy**.

## 🧠 Konsep Model

Engine ini mengimplementasikan model antrian **M/G/1** (atau M/G/c jika nozzle > 1):
- **Markovian Arrival (M)**: Kedatangan motor bersifat independen dengan rata-rata *arrival rate* ($\lambda$), dimodelkan sebagai distribusi Eksponensial (`random.exponential`).
- **General Service Time (G)**: Waktu pelayanan ditarik secara *Empirical* (sampel acak dari *raw data* observasi) atau di-*fitting* menggunakan distribusi Gamma, menyesuaikan dengan durasi pelayanan riil di SPBU.
- **c Servers**: Jumlah pompa (nozzle) aktif yang dapat disesuaikan.

## 📂 Berkas Utama

- `engine.py`: Mengandung fungsi `run_mg1_simulation()`.

## 🔄 Alur Pemrosesan (Data Flow)

1. **Input Parameter:** 
   Fungsi ini dipanggil oleh antarmuka Streamlit dengan mengoper $\lambda$ (motor per menit) dan *array* durasi waktu pelayanan empiris.
2. **Setup Lingkungan:**
   SimPy membuat `Environment` dan membatasi antrian menggunakan `Resource` dengan kapasitas *nozzle*.
3. **Pembangkitan Entitas (Motor):**
   Proses akan terus melahirkan entitas "pelanggan" berdasarkan jarak waktu interarrival eksponensial. Jika antrian sudah mencapai batas maksimal (misalnya 15), motor akan ditolak (*rejected*).
4. **Pemrosesan & Pencatatan:**
   Waktu mulai menunggu, waktu dilayani, dan waktu selesai dihitung secara absolut oleh *internal clock* SimPy. Modul ini merekam log tersebut ke dalam *array*.
5. **Output (Return):**
   Engine mengembalikan *Dictionary* yang berisi:
   - `summary`: Metrik rata-rata (Lq, Wq, Utilisasi).
   - `results`: *DataFrame* log historis setiap pelanggan yang selesai.
   - `queue_log`: *DataFrame* yang mencatat panjang antrian setiap detik/menitnya.