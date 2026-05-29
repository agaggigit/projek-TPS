# ⛽ Web App Simulasi Antrian SPBU

Direktori ini berisi kode sumber untuk antarmuka pengguna interaktif (berbasis [Streamlit](https://streamlit.io/)) yang berfungsi sebagai dasbor simulasi.

## 📂 Struktur Direktori

- `streamlit_app.py`: Titik masuk utama aplikasi (Main Entry Point). Menghubungkan engine simulasi, sidebar, chart, dan animasi 2D.
- `scenarios.py`: Berisi preset parameter/skenario simulasi (contoh: Sesi Sibuk, Sesi Sepi) yang dapat dipilih pengguna.
- `components/`: Kumpulan modul UI untuk mempermudah pembacaan kode.
  - `sidebar.py`: Panel kontrol di sebelah kiri untuk mengatur $\lambda$, $\mu$, dan konfigurasi lainnya.
  - `charts.py`: Visualisasi metrik KPI dan grafik antrian dinamis menggunakan Plotly.
  - `animation.py`: *Wrapper* Python untuk menanamkan animasi HTML ke dalam antarmuka Streamlit.
  - `animation_2d.html`: *Engine* visualisasi utama berbasis HTML5 Canvas dan JavaScript. Merender denah SPBU beserta lalu lintas motor dengan 60FPS.

## 🚀 Fitur Utama

1. **Konfigurasi Real-time**: Mengubah tingkat kedatangan ($\lambda$), tingkat pelayanan ($\mu$), dan jumlah pompa secara dinamis dari sidebar.
2. **Kalkulasi Engine**: Menjalankan *script* `simulation/engine.py` secara asinkron setiap kali simulasi dijalankan.
3. **Analisis Metrik**: Tabel komprehensif menampilkan $W_q$, $L_q$, $\rho$, dan tren riwayat waktu mengantri.
4. **Animasi 2D Interaktif**: Visualisasi nyata bagaimana motor masuk, antri, dilayani di setiap *island*, lalu pergi meninggalkan SPBU. Animasi dapat dipercepat atau diperlambat melalui slider HUD.

## 🎨 Modifikasi Asset Animasi

Secara *default*, animasi `animation_2d.html` merender motor dan pompa sebagai bentuk geometris (kotak warna-warni). Anda dapat menggantinya dengan gambar (PNG/JPG) Anda sendiri.

Cara mengganti:
1. Buka `app/components/animation_2d.html`
2. Cari bagian **KONFIGURASI ASSET** di baris atas kode JavaScript.
3. Ganti nilai `null` dengan path relatif atau URL gambar Anda, contoh:
   ```javascript
   const ASSET_VEHICLE = 'http://localhost:8000/motor.png';
   const ASSET_BACKGROUND = 'http://localhost:8000/denah_spbu_custom.jpg';
   ```

## 🛠️ Cara Menjalankan

Dari *root directory* proyek, jalankan:
```bash
python -m streamlit run app/streamlit_app.py
```
Aplikasi akan terbuka otomatis di browser pada `http://localhost:8501`.