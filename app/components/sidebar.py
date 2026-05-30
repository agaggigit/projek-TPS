import streamlit as st

def render_sidebar(default_arrival_rate):
    with st.sidebar:
        st.header("Parameter Simulasi")
        arrival_rate = st.slider(
            "Arrival rate (motor/menit)",
            min_value=0.1,
            max_value=float(max(3.0, default_arrival_rate * 2)),
            value=float(default_arrival_rate),
            step=0.01,
        )
        simulation_time = st.slider(
            "Durasi simulasi (menit)",
            min_value=30,
            max_value=240,
            value=120,
            step=10,
        )
        num_nozzles = st.slider(
            "Jumlah nozzle aktif",
            min_value=1,
            max_value=4,
            value=1,
            step=1,
        )
        seed = st.number_input(
            "Seed random",
            min_value=0,
            max_value=9999,
            value=42,
            step=1,
        )
        run_button = st.button("Jalankan Simulasi", type="primary")

    return arrival_rate, simulation_time, num_nozzles, seed, run_button