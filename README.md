# ⛽ Projek Pemodelan dan Simulasi (TPS) — Antrian SPBU Pertamax Motor

Proyek ini adalah simulasi sistem antrian pada Stasiun Pengisian Bahan Bakar Umum (SPBU) menggunakan pendekatan **M/G/1** yang diimplementasikan dengan **SimPy** dan disajikan dalam dasbor interaktif berbasis **Streamlit** beserta animasi **3D**.

## 🎯 Tujuan Proyek
- Menghitung dan menganalisis metrik performa antrian riil seperti $W_q$ (waktu tunggu), $L_q$ (panjang antrian), dan $\rho$ (utilisasi server/nozzle).
- Melakukan *Discrete-Event Simulation* menggunakan library SimPy untuk mendapatkan estimasi yang mendekati kenyataan.
- Menyediakan Dasbor Interaktif yang memvisualisasikan lalu lintas antrian motor SPBU secara 3D (Three.js).

## 📂 Struktur Repositori

- **`analysis/`**: Jupyter Notebook untuk pemrosesan data historis dan pengujian kecocokan distribusi.
- **`app/`**: Dasbor web Streamlit, mencakup UI komponen terpisah (sidebar, chart) dan animasi 3D.
- **`data/`**: Direktori untuk menyimpan data mentah observasi (CSV) serta *log* hasil simulasi.
- **`simulation/`**: Mesin (engine) simulasi *discrete-event* berbasis `simpy` yang memodelkan antrian secara matematis.

## 🚀 Memulai

Untuk panduan instalasi lengkap, prasyarat lingkungan, dan cara menjalankan aplikasi, silakan baca **[SETUP.md](SETUP.md)**.
