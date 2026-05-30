import numpy as np
import pandas as pd
import streamlit as st

def metric_value(summary, key, suffix="", decimals=2):
    value = summary.get(key)
    if value is None:
        return "-"
    if isinstance(value, (int, np.integer)):
        return f"{value}{suffix}"
    return f"{value:.{decimals}f}{suffix}"


def show_summary(summary):
    cols = st.columns(4)
    cols[0].metric("Motor dilayani", metric_value(summary, "jumlah_motor_dilayani", decimals=0))
    cols[1].metric("Rata-rata waktu tunggu", metric_value(summary, "rata_rata_waktu_tunggu", " menit"))
    cols[2].metric("Rata-rata waktu dalam sistem", metric_value(summary, "rata_rata_waktu_dalam_sistem", " menit"))
    cols[3].metric("Motor ditolak", metric_value(summary, "jumlah_motor_ditolak", decimals=0))

    cols = st.columns(3)
    cols[0].metric("Rata-rata waktu pelayanan", metric_value(summary, "rata_rata_waktu_pelayanan", " menit"))
    cols[1].metric("Rata-rata panjang antrian", metric_value(summary, "rata_rata_panjang_antrian", " motor"))
    utilization = summary.get("utilisasi_server")
    cols[2].metric("Utilisasi server", "-" if utilization is None else f"{utilization * 100:.2f}%")


def show_charts(results, queue_log):
    left, right = st.columns(2)

    with left:
        st.subheader("Panjang Antrian terhadap Waktu")
        if queue_log.empty:
            st.info("Queue log kosong.")
        else:
            queue_chart = queue_log[["time", "queue_length"]].set_index("time")
            st.line_chart(queue_chart)

    with right:
        st.subheader("Waiting Time per Customer")
        if results.empty:
            st.info("Belum ada customer yang selesai dilayani.")
        else:
            waiting_chart = results[["customer_id", "waiting_time"]].set_index("customer_id")
            st.line_chart(waiting_chart)


def show_sensitivity_analysis(run_simulation_fn, base_arrival_rate, service_times, simulation_time, seed, num_nozzles):
    st.subheader("Analisis Sensitivitas")

    scenarios = [
        ("Sepi", base_arrival_rate * 0.7),
        ("Normal", base_arrival_rate),
        ("Ramai", base_arrival_rate * 1.3),
    ]

    rows = []
    for offset, (name, scenario_arrival_rate) in enumerate(scenarios):
        output = run_simulation_fn(
            arrival_rate=scenario_arrival_rate,
            service_times=service_times,
            simulation_time=simulation_time,
            seed=seed + offset,
            num_nozzles=num_nozzles,
        )
        summary = output["summary"]
        rows.append(
            {
                "skenario": name,
                "arrival_rate": scenario_arrival_rate,
                "rata_rata_waktu_tunggu": summary.get("rata_rata_waktu_tunggu", 0),
                "rata_rata_panjang_antrian": summary.get("rata_rata_panjang_antrian", 0),
                "utilisasi_server": summary.get("utilisasi_server", 0),
            }
        )

    sensitivity_df = pd.DataFrame(rows)
    st.dataframe(
        sensitivity_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "skenario": "Skenario",
            "arrival_rate": st.column_config.NumberColumn("Arrival rate", format="%.3f motor/menit"),
            "rata_rata_waktu_tunggu": st.column_config.NumberColumn("Rata-rata waktu tunggu", format="%.2f menit"),
            "rata_rata_panjang_antrian": st.column_config.NumberColumn("Rata-rata panjang antrian", format="%.2f motor"),
            "utilisasi_server": st.column_config.NumberColumn("Utilisasi server", format="%.2f"),
        },
    )
