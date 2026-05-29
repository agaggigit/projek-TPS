# ⛽ Projek Pemodelan dan Simulasi (TPS) — Antrian SPBU

Proyek ini adalah simulasi sistem antrian pada Stasiun Pengisian Bahan Bakar Umum (SPBU) menggunakan pemodelan matematika **M/M/c** (atau adaptasinya) yang diimplementasikan dalam Python.

## 🎯 Tujuan Proyek
- Menghitung dan menganalisis metrik performa antrian seperti $W_q$ (waktu tunggu antrian), $L_q$ (panjang antrian), dan $\rho$ (utilisasi pompa).
- Menguji kecocokan distribusi data empiris.
- Menyediakan Dasbor Interaktif berbasis Streamlit lengkap dengan **Animasi 2D Top-Down** untuk memvisualisasikan lalu lintas kendaraan di SPBU secara *real-time*.

## 📂 Struktur Utama

- **`analysis/`**: Jupyter Notebook untuk pemrosesan data historis dan uji *goodness-of-fit* (Eksponensial/Normal).
- **`simulation/`**: *Engine* berbasis **SimPy** yang melakukan kalkulasi *discrete-event simulation* dan pelacakan historis setiap *customer*.
- **`app/`**: Dasbor web Streamlit yang mencakup antarmuka parameter, grafik Plotly, dan kanvas animasi HTML5.

## 🚀 Memulai

Untuk panduan instalasi lengkap, prasyarat, dan cara menjalankan aplikasi, silakan baca **[SETUP.md](SETUP.md)**.
