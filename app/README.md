# ⛽ Web App Simulasi Antrian SPBU

Direktori ini berisi kode sumber untuk antarmuka pengguna interaktif berbasis [Streamlit](https://streamlit.io/) yang berfungsi sebagai dasbor simulasi antrian.

## 📂 Struktur Direktori

Kode aplikasi telah dirapikan (di-refactor) menjadi arsitektur berbasis komponen agar lebih mudah dipelihara:

- `streamlit_app.py`: Titik masuk utama aplikasi (Main Entry Point). Bertanggung jawab me-load data observasi (`load_observation_data`), memanggil engine simulasi, dan merender komponen UI.
- `components/`: Kumpulan modul UI terpisah:
  - `sidebar.py`: Panel kontrol di sebelah kiri untuk mengatur kedatangan (Arrival Rate), Durasi, Jumlah Nozzle, dan Seed.
  - `charts.py`: Menyediakan fungsi untuk me-render metrik KPI (Wq, Lq, Utilisasi), grafik antrian dinamis menggunakan Plotly/Streamlit Line Chart, dan analisis sensitivitas.
  - `animation.py`: *Wrapper* Python untuk menanamkan animasi HTML 3D (menggunakan **Three.js**) ke dalam antarmuka Streamlit. Merender denah SPBU beserta pergerakan motor secara dinamis.

## 🚀 Fitur Utama

1. **Pemodelan Data Dinamis**: Menarik parameter langsung dari file *raw data* observasi secara otomatis.
2. **Kalkulasi Engine SimPy**: Menggunakan `run_mg1_simulation` dari modul `simulation/engine.py` untuk mensimulasikan antrian sesuai parameter.
3. **Analisis Metrik & Sensitivitas**: Menyajikan performa antrian dan membandingkan 3 skenario berbeda (Sepi, Normal, Ramai) dalam tabel ringkas.
4. **Animasi 3D Interaktif**: Visualisasi *real-time* (Three.js) yang dapat dimainkan (play/pause/scrub) untuk melihat pergerakan historis motor di dalam sistem antrian.

## 🛠️ Cara Menjalankan

Dari *root directory* proyek, jalankan:
```bash
python -m streamlit run app/streamlit_app.py
```
Aplikasi akan terbuka otomatis di browser pada `http://localhost:8501`.