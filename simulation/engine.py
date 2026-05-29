import simpy
import random
import numpy as np
import pandas as pd
from scipy import stats


def run_mg1_simulation(
    arrival_rate,
    service_times,
    simulation_time=120,
    seed=42,
    num_servers=1,
    max_queue=15,
    service_distribution="empirical"
):
    """
    Simulasi antrian M/G/1 untuk SPBU Pertamax motor.

    arrival_rate:
        lambda, rata-rata jumlah motor datang per menit

    service_times:
        list/array durasi pengisian bensin dari data asli, dalam menit

    simulation_time:
        durasi simulasi dalam menit

    num_servers:
        jumlah nozzle/server aktif. Default 1 agar tetap menjadi M/G/1.

    max_queue:
        jumlah maksimum motor yang boleh menunggu di antrean.
        Motor baru akan ditolak jika antrean sudah penuh.

    service_distribution:
        "empirical" mengambil sampel langsung dari data.
        "gamma" mengambil sampel dari distribusi Gamma hasil fitting data.
    """

    random.seed(seed)
    np.random.seed(seed)

    service_times = np.asarray(service_times, dtype=float)
    service_times = service_times[service_times > 0]
    if service_times.size == 0:
        raise ValueError("service_times harus berisi minimal satu durasi positif.")

    gamma_params = None
    if service_distribution == "gamma":
        gamma_params = stats.gamma.fit(service_times, floc=-1e-5)
    elif service_distribution != "empirical":
        raise ValueError("service_distribution harus 'empirical' atau 'gamma'.")

    env = simpy.Environment()
    server = simpy.Resource(env, capacity=num_servers)

    results = []
    queue_log = []
    rejected_customers = []

    def customer(env, customer_id):
        arrival_time = env.now

        with server.request() as request:
            yield request

            service_start = env.now
            waiting_time = service_start - arrival_time

            if service_distribution == "gamma":
                shape, loc, scale = gamma_params
                service_time = max(float(np.random.gamma(shape, scale) + loc), 1e-6)
            else:
                service_time = random.choice(service_times)
            yield env.timeout(service_time)

            departure_time = env.now

            results.append({
                "customer_id": customer_id,
                "arrival_time": arrival_time,
                "service_start": service_start,
                "departure_time": departure_time,
                "waiting_time": waiting_time,
                "service_time": service_time,
                "system_time": departure_time - arrival_time
            })

    def arrival_process(env):
        customer_id = 0

        while env.now < simulation_time:
            interarrival_time = np.random.exponential(1 / arrival_rate)
            yield env.timeout(interarrival_time)

            customer_id += 1
            if server.count >= num_servers and len(server.queue) >= max_queue:
                rejected_customers.append({
                    "customer_id": customer_id,
                    "arrival_time": env.now,
                    "reason": "queue_full",
                })
                continue
            env.process(customer(env, customer_id))

    def monitor_queue(env):
        while env.now < simulation_time:
            queue_log.append({
                "time": env.now,
                "queue_length": len(server.queue),
                "server_busy": server.count,
                "rejected_count": len(rejected_customers),
            })
            yield env.timeout(1)

    env.process(arrival_process(env))
    env.process(monitor_queue(env))
    env.run(until=simulation_time)

    results_df = pd.DataFrame(results)
    queue_df = pd.DataFrame(queue_log)

    if results_df.empty:
        return {
            "summary": {
                "jumlah_motor_dilayani": 0,
                "jumlah_motor_ditolak": len(rejected_customers),
                "rata_rata_panjang_antrian": queue_df["queue_length"].mean() if not queue_df.empty else 0,
                "utilisasi_server": queue_df["server_busy"].mean() / num_servers if not queue_df.empty else 0,
            },
            "results": results_df,
            "queue_log": queue_df
        }

    avg_waiting_time = results_df["waiting_time"].mean()
    avg_system_time = results_df["system_time"].mean()
    avg_service_time = results_df["service_time"].mean()
    avg_queue_length = queue_df["queue_length"].mean()
    utilization = queue_df["server_busy"].mean() / num_servers

    summary = {
        "jumlah_motor_dilayani": len(results_df),
        "jumlah_motor_ditolak": len(rejected_customers),
        "rata_rata_waktu_tunggu": avg_waiting_time,
        "rata_rata_waktu_dalam_sistem": avg_system_time,
        "rata_rata_waktu_pelayanan": avg_service_time,
        "rata_rata_panjang_antrian": avg_queue_length,
        "utilisasi_server": utilization
    }

    return {
        "summary": summary,
        "results": results_df,
        "queue_log": queue_df
    }
