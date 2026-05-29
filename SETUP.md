# 🛠️ Panduan Setup Projek TPS — Simulasi Antrian SPBU

Ikuti langkah-langkah di bawah ini **secara berurutan** untuk menyiapkan lingkungan pengembangan projek ini dari awal.

---

## Prasyarat

Pastikan hal-hal berikut sudah terinstall di komputer kamu sebelum memulai:

| Kebutuhan | Versi Minimal | Link Download |
|---|---|---|
| **Python** | 3.10+ | https://www.python.org/downloads/ |
| **VS Code** / Antigravity IDE | Terbaru | https://code.visualstudio.com/ |
| **Git** | Terbaru | https://git-scm.com/downloads |

> **Cek instalasi Python:** Buka terminal dan ketik `python --version`. Jika muncul versi, berarti sudah terinstall.

---

## Langkah 1 — Clone Repository

Buka terminal, lalu jalankan:

```bash
git clone https://github.com/agaggigit/projek-TPS.git
cd projek-TPS
```

---

## Langkah 2 — Install Semua Library Python

Jalankan perintah berikut di dalam folder projek:

```bash
pip install -r requirements.txt
```

Perintah ini akan menginstall semua library yang dibutuhkan:
- `pandas`, `numpy`, `scipy` — untuk analisis data
- `matplotlib`, `seaborn` — untuk visualisasi grafik
- `jupyter`, `ipykernel` — untuk menjalankan file `.ipynb`
- `streamlit` — untuk menjalankan aplikasi interaktif
- `simpy` — untuk engine simulasi antrian

> ⏳ Proses ini memerlukan koneksi internet dan mungkin memakan waktu beberapa menit.

---

## Langkah 3 — Setup Jupyter di VS Code / Antigravity IDE

Agar file `.ipynb` bisa dijalankan langsung di dalam editor:

1. Buka **Extensions** (`Ctrl+Shift+X`)
2. Cari dan install ekstensi **"Jupyter"** (by Microsoft)
3. Tekan `Ctrl+Shift+P` → ketik **`Python: Select Interpreter`**
4. Pilih **`Python 3.x.x` (yang ada di `C:\Program Files\Python3xx\python.exe`)**
5. Tekan `Ctrl+Shift+P` → ketik **`Developer: Reload Window`**

---

## Langkah 4 — Siapkan Data

Letakkan file data mentah (format `.csv`) ke dalam folder `data/`.

```
data/
├── sesi2_sore.csv      # Data sesi 2 (sore peak)
├── sesi3_malam.csv     # Data sesi 3 (malam peak)
└── sesi4_malam.csv     # Data sesi 4 (malam sepi)
```

Format kolom CSV yang dibutuhkan (sesuaikan dengan data kamu):

| Kolom | Keterangan |
|---|---|
| `waktu_kedatangan` | Timestamp kedatangan motor (detik atau HH:MM:SS) |
| `waktu_mulai_layanan` | Timestamp mulai dilayani |
| `waktu_selesai_layanan` | Timestamp selesai dilayani |

---

## Langkah 5 — Jalankan Analisis (Notebook)

Buka folder `analysis/` dan jalankan notebook secara berurutan:

### 📓 `01_statistik_deskriptif.ipynb`
Menghitung parameter dasar antrian (λ, μ, ρ, Lq, Wq) dari data mentah.

```
Buka file → Pilih kernel Python 3.x → Run All Cells
```

### 📓 `02_fitting_distribusi.ipynb`
Menguji apakah data mengikuti distribusi Eksponensial/Normal untuk menentukan model (M/M/1 atau M/G/1).

```
Buka file → Pilih kernel Python 3.x → Run All Cells
```

---

## Langkah 6 — Jalankan Aplikasi Streamlit

Setelah analisis selesai, jalankan aplikasi interaktif simulasi antrian:

```bash
streamlit run app/streamlit_app.py
```

Aplikasi akan otomatis terbuka di browser di alamat: `http://localhost:8501`

---

## Struktur Folder Projek

```
projek-TPS/
│
├── 📄 SETUP.md              ← Panduan ini
├── 📄 requirements.txt      ← Daftar library Python
│
├── 📁 data/                 ← Data mentah CSV (taruh di sini)
├── 📁 assets/               ← Aset gambar untuk aplikasi
│
├── 📁 analysis/             ← Analisis statistik (Jupyter Notebook)
│   ├── 01_statistik_deskriptif.ipynb
│   └── 02_fitting_distribusi.ipynb
│
├── 📁 simulation/           ← Engine simulasi antrian
│   └── engine.py
│
└── 📁 app/                  ← Aplikasi Streamlit
    ├── streamlit_app.py
    ├── scenarios.py
    └── components/
```

---

## Troubleshooting

### ❌ `ModuleNotFoundError: No module named 'pandas'`
→ Jalankan ulang: `pip install -r requirements.txt`

### ❌ `Python Environment Tools (PET) failed`
→ Tekan `Ctrl+Shift+P` → **`Python: Select Interpreter`** → pilih Python yang benar → **`Developer: Reload Window`**

### ❌ Kernel tidak muncul di notebook
→ Pastikan `ipykernel` sudah terinstall: `pip install ipykernel --upgrade`

### ❌ `fatal: refusing to merge unrelated histories`
→ Jalankan: `git pull origin main --allow-unrelated-histories`
