from pathlib import Path
import json
import sys

import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT_DIR / "data" / "TPS fulltank - Rekap.csv"

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from simulation.engine import run_mg1_simulation
from app.components.animation import show_animation
from app.components.charts import show_summary, show_charts, show_sensitivity_analysis
from app.components.sidebar import render_sidebar

st.set_page_config(
    page_title="Simulasi Antrian Pertamax Motor",
    layout="wide",
)

@st.cache_data
def load_observation_data():
    data = pd.read_csv(DATA_PATH)

    data["_service_seconds"] = pd.to_numeric(
        data["Rerata Waktu Pelayanan (s)"].replace("-", np.nan),
        errors="coerce",
    )
    data["_interarrival_seconds"] = pd.to_numeric(
        data["Interarrival Time (s)"].replace("-", np.nan),
        errors="coerce",
    )

    calibration_data = data.dropna(subset=["_service_seconds", "_interarrival_seconds"])

    recap_service_times = (calibration_data["_service_seconds"] / 60).tolist()
    raw_service_times = []
    for service_path in sorted((ROOT_DIR / "data").glob("sesi*/*Waktu Pelayanan.csv")):
        service_data = pd.read_csv(service_path)
        if "Detik" not in service_data.columns:
            continue
        service_seconds = pd.to_numeric(service_data["Detik"], errors="coerce").dropna()
        raw_service_times.extend((service_seconds[service_seconds > 0] / 60).tolist())

    service_times = raw_service_times or recap_service_times
    mean_interarrival_minute = calibration_data["_interarrival_seconds"].mean() / 60
    arrival_rate = 1 / mean_interarrival_minute

    return data.drop(columns=["_service_seconds", "_interarrival_seconds"]), service_times, arrival_rate


def run_simulation(arrival_rate, service_times, simulation_time, seed, num_nozzles):
    return run_mg1_simulation(
        arrival_rate=arrival_rate,
        service_times=service_times,
        simulation_time=simulation_time,
        seed=seed,
        num_servers=num_nozzles,
        max_queue=15,
        service_distribution="gamma",
    )


st.title("Simulasi dan Analisis Antrian Pertamax Motor")
st.caption("SPBU Pertamina Jalan Sudirman - model M/G/1 dari data observasi")

try:
    observation_data, service_times, default_arrival_rate = load_observation_data()
except FileNotFoundError:
    st.error(f"File data tidak ditemukan: {DATA_PATH}")
    st.stop()
except KeyError as exc:
    st.error(f"Kolom data tidak sesuai: {exc}")
    st.stop()

if not service_times:
    st.error("Kolom waktu pelayanan tidak punya nilai numerik yang bisa dipakai.")
    st.stop()

arrival_rate, simulation_time, num_nozzles, seed, run_button = render_sidebar(default_arrival_rate)

st.markdown("### Data Observasi")
left, right = st.columns([2, 1])
with left:
    st.dataframe(observation_data, use_container_width=True, hide_index=True)
with right:
    st.metric("Arrival rate dari data", f"{default_arrival_rate:.3f} motor/menit")
    st.metric("Sampel waktu pelayanan", f"{len(service_times)} sesi")
    st.metric("Rata-rata pelayanan", f"{np.mean(service_times):.2f} menit")

if run_button or "simulation_output" not in st.session_state:
    st.session_state.simulation_output = run_simulation(
        arrival_rate=arrival_rate,
        service_times=service_times,
        simulation_time=simulation_time,
        seed=int(seed),
        num_nozzles=num_nozzles,
    )
    st.session_state.last_params = {
        "arrival_rate": arrival_rate,
        "simulation_time": simulation_time,
        "seed": int(seed),
        "num_nozzles": num_nozzles,
    }

output = st.session_state.simulation_output
params = st.session_state.last_params
summary = output["summary"]
results = output["results"]
queue_log = output["queue_log"]

st.markdown("### Hasil Simulasi")
st.caption(
    "Parameter aktif: "
    f"arrival_rate={params['arrival_rate']:.3f} motor/menit, "
    f"durasi={params['simulation_time']} menit, "
    f"nozzle={params['num_nozzles']}, seed={params['seed']}"
)

if not summary:
    st.warning("Belum ada motor yang selesai dilayani pada simulasi ini.")
else:
    show_summary(summary)

show_charts(results, queue_log)
show_animation(
    results,
    queue_log,
    params["num_nozzles"],
    params["simulation_time"],
    summary.get("jumlah_motor_ditolak", 0),
)
show_sensitivity_analysis(
    run_simulation_fn=run_simulation,
    base_arrival_rate=params["arrival_rate"],
    service_times=service_times,
    simulation_time=params["simulation_time"],
    seed=params["seed"],
    num_nozzles=params["num_nozzles"],
)
