import pandas as pd
from engine import run_mg1_simulation

df = pd.read_csv("../data/TPS fulltank - Rekap.csv")

kolom_service = "Rerata Waktu Pelayanan (s)"
kolom_interarrival = "Interarrival Time (s)"

# ubah teks jadi angka
df[kolom_service] = pd.to_numeric(df[kolom_service], errors="coerce")
df[kolom_interarrival] = pd.to_numeric(df[kolom_interarrival], errors="coerce")

# buang baris yang kosong / gagal dibaca
df = df.dropna(subset=[kolom_service, kolom_interarrival])

# detik ke menit
service_times = (df[kolom_service] / 60).tolist()

mean_interarrival_minute = df[kolom_interarrival].mean() / 60
arrival_rate = 1 / mean_interarrival_minute

hasil = run_mg1_simulation(
    arrival_rate=arrival_rate,
    service_times=service_times,
    simulation_time=120
)

print("Arrival rate:", arrival_rate)
print("Service times:", service_times)
print(hasil["summary"])
print(hasil["results"].head())

hasil["results"].to_csv("../data/hasil_simulasi_motor.csv", index=False)
hasil["queue_log"].to_csv("../data/queue_log_motor.csv", index=False)