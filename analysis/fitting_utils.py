import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def uji_dsitribusi(data, distribution):
    distribution_object = getattr(stats, distribution)
    
    # Kunci loc=0 untuk eksponensial
    if distribution == "expon":
        params = distribution_object.fit(data, floc=0)
    elif distribution == "gamma":
        # Untuk gamma, jika ada data bernilai tepat 0, floc=0 akan error.
        # Jadi kita kunci di angka negatif yang saaaangat kecil (-0.00001)
        params = distribution_object.fit(data, floc=-1e-5)
    else:
        params = distribution_object.fit(data)

    # Uji K-S 
    # H0: Data mengikuti distribusi teoritis
    # H1: Data tidak mengikuti distribusi teoritis
    stat, p_value = stats.kstest(data, distribution, args=params)
    
    hasil_uji = "Diterima" if p_value > 0.05 else "Ditolak"
    print(f"Distribusi {distribution}: p-value = {p_value:.4f} (H0 {hasil_uji})")

    return distribution_object, params, p_value

def plot_histogram_fit(data, hasil_semua, nama_data):
    plt.figure(figsize=(7, 4))
    
    # Histogram data asli
    ax = sns.histplot(data, stat='density', alpha=0.4, color='steelblue', label='Data Asli')
    
    # Simpan batas atas sumbu-Y dari histogram asli
    ylim = ax.get_ylim()
    
    x = np.linspace(min(data), max(data), 100)
    warna = ['red', 'green', 'orange']

    # Looping untuk menggambar garis kurva setiap distribusi
    for i, h in enumerate(hasil_semua):
        distribution = h["distribusi"]
        param = h["params"]
        distribution_object = getattr(stats, distribution)
        
        pdf_fitted = distribution_object.pdf(x, *param[:-2], loc=param[-2], scale=param[-1])
        
        # Garis lurus jika diterima, putus-putus jika ditolak
        style = "-" if h["is_diterima"] else "--"
        
        plt.plot(x, pdf_fitted, style, label=f'{distribution} (p={h["p_value"]:.3f})', color=warna[i], linewidth=2)

    # Kembalikan batas sumbu-Y agar garis yang meledak (seperti gamma) tidak merusak skala
    ax.set_ylim(ylim)

    plt.title(f'Histogram dan Fitting: {nama_data}', fontsize=12)
    plt.xlabel('Waktu (Detik)')
    plt.ylabel('Kepadatan (Density)')
    plt.legend()
    plt.tight_layout()
    plt.show()

def uji_data(data, nama_data):
    jenis_distribusi = ['expon', 'norm', 'gamma']
    hasil_semua = []

    for distribusi in jenis_distribusi:
        objek_distribusi, params, p_value = uji_dsitribusi(data, distribusi)
    
        hasil_semua.append({
            "distribusi": distribusi,
            "params": params,
            "p_value": p_value,
            "is_diterima": p_value > 0.05
        })

    # Panggil fungsi plot di LUAR loop agar semua distribusi tergabung dalam 1 gambar
    plot_histogram_fit(data, hasil_semua, nama_data)

    return hasil_semua

def buat_kesimpulan(datasets):
    summary = []

    for sesi, dfs in datasets.items():
        print(f"\n{'='*40}")
        print(f"  {sesi}")
        print(f"{'='*40}")
        
        arr_interarrival = dfs["interarrival"]["Detik"].dropna().values
        hasil_interarrival = uji_data(arr_interarrival, f"Interarrival - {sesi}")

        if "service" in dfs:
            arr_service = dfs["service"]["Detik"].dropna().values
            hasil_service = uji_data(arr_service, f"Service Time - {sesi}")
        else:
            hasil_service = None

        interarrival_expon = [h for h in hasil_interarrival if h["distribusi"] == "expon"][0]
        interarrival_model = "M" if interarrival_expon["is_diterima"] else "G"

        if hasil_service:
            service_expon = [h for h in hasil_service if h["distribusi"] == "expon"][0]
            service_model = "M" if service_expon["is_diterima"] else "G"
            model_antrian = f"{interarrival_model}/{service_model}/1"
        else:
            service_expon = None
            service_model = "-"
            model_antrian = "Belum bisa ditentukan"

        summary.append({
            "Sesi": sesi,
            "Interarrival Expon p-value": round(interarrival_expon["p_value"], 4),
            "Model Kedatangan": interarrival_model,
            "Service Expon p-value": round(service_expon["p_value"], 4) if service_expon else "-",
            "Model Pelayanan": service_model,
            "Model Antrian": model_antrian,
        })

    return pd.DataFrame(summary)