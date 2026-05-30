# 📁 Repositori Data

Direktori ini berfungsi sebagai *database* lokal untuk keperluan analisis historis dan pencatatan (*logging*) keluaran simulasi.

## 📂 Konten Direktori

1. **Data Observasi Mentah (`sesi*/` dan `TPS fulltank - Rekap.csv`)**:
   Kumpulan file CSV yang merupakan rekaman langsung (observasi riil) kendaraan masuk dan keluar di lapangan. Data ini dibaca secara otomatis oleh `streamlit_app.py` untuk mengolah parameter kedatangan dan sebaran sampel durasi pelayanan (peluang *Empirical*).

2. **Output Simulasi**:
   Ketika Anda menekan tombol "Jalankan Simulasi" di antarmuka web, hasil pergerakan historis (antrian vs waktu) akan diekspor dan dicatat di direktori ini (misalnya `hasil_simulasi_motor.csv` atau `queue_log_motor.csv`). Ini bisa digunakan sebagai arsip sekunder untuk *data mining* lebih lanjut.