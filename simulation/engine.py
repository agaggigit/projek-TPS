import simpy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def generate_interarrival(lam, dist_type="exponential", **kwargs):
    """
    Generate interarrival time based on a specific distribution.
    lam: Arrival rate (e.g., customers per minute)
    """
    if dist_type == "exponential":
        return np.random.exponential(1 / lam)
    elif dist_type == "lognormal":
        # Requires 'mean' and 'sigma' in kwargs for underlying normal dist
        mean = kwargs.get('mean', 0)
        sigma = kwargs.get('sigma', 1)
        return np.random.lognormal(mean, sigma)
    else:
        # Default fallback
        return np.random.exponential(1 / lam)

def generate_service(mu, dist_type="exponential", **kwargs):
    """
    Generate service time based on a specific distribution.
    mu: Service rate (e.g., customers per minute)
    """
    if dist_type == "exponential":
        return np.random.exponential(1 / mu)
    elif dist_type == "normal":
        # Requires 'std' in kwargs
        std = kwargs.get('std', 1)
        # Ensure positive service time
        return max(0.01, np.random.normal(1 / mu, std))
    else:
        return np.random.exponential(1 / mu)

def monitor_queue(env, gas_station, timeline, interval=1.0):
    """
    Periodically record the queue length to generate a timeline.
    """
    while True:
        timeline.append({'time': env.now, 'queue_length': len(gas_station.put_queue)})
        yield env.timeout(interval)

def customer(env, name, gas_station, mu, service_dist, metrics):
    """
    Process for a single customer.
    """
    arrival_time = env.now
    
    with gas_station.request() as request:
        # Wait in queue until a nozzle is available
        yield request
        
        wait_time = env.now - arrival_time
        metrics['wait_times'].append(wait_time)
        metrics['queue_lengths'].append(len(gas_station.put_queue))
        
        # Determine service time
        service_time = generate_service(mu, service_dist)
        
        # Record busy time (to calculate utilization later)
        metrics['server_busy_time'] += service_time
        
        # Being served
        yield env.timeout(service_time)

def arrival_generator(env, gas_station, lam, mu, interarrival_dist, service_dist, metrics):
    """ 
    Spawns customers based on the interarrival distribution.
    """
    customer_id = 0
    while True:
        interarrival_time = generate_interarrival(lam, interarrival_dist)
        yield env.timeout(interarrival_time)
        customer_id += 1
        env.process(customer(env, f'Customer_{customer_id}', gas_station, mu, service_dist, metrics))

def run_simulation(lam, mu, c, duration, interarrival_dist="exponential", service_dist="exponential"):
    """
    Run a single simulation and return the metrics.
    """
    env = simpy.Environment()
    gas_station = simpy.Resource(env, capacity=c)
    
    # Store metrics for this run
    metrics = {
        'wait_times': [],
        'queue_lengths': [],
        'server_busy_time': 0.0
    }
    timeline = []
    
    # Start processes
    env.process(arrival_generator(env, gas_station, lam, mu, interarrival_dist, service_dist, metrics))
    env.process(monitor_queue(env, gas_station, timeline, interval=1.0))
    
    # Run simulation
    env.run(until=duration)
    
    # Calculate Results
    num_customers = len(metrics['wait_times'])
    avg_wq = np.mean(metrics['wait_times']) if num_customers > 0 else 0
    
    # Timeline-based average queue length is more accurate
    if timeline:
        timeline_df = pd.DataFrame(timeline)
        avg_lq = timeline_df['queue_length'].mean()
    else:
        avg_lq = 0
        
    # Utilization rho
    rho = metrics['server_busy_time'] / (c * duration)
    # Ensure rho doesn't exceed 1 mathematically in edge cases
    rho = min(rho, 1.0)
    
    return {
        'Wq': avg_wq,
        'Lq': avg_lq,
        'rho': rho,
        'total_customers_served': num_customers,
        'timeline': timeline
    }

def run_all_scenarios() -> pd.DataFrame:
    """
    Run the 5 defined scenarios and return a DataFrame with results.
    """
    # Data disesuaikan dari 01_statistik_deskriptif.ipynb
    # Asumsi satuan waktu adalah detik. Durasi simulasi = 3600 detik (1 jam)
    # CATATAN: Nilai mu di data Anda (50.42, 55.05) adalah Waktu Pelayanan (detik).
    # Sedangkan engine ini membutuhkan Service Rate (kendaraan/detik), sehingga mu = 1 / Waktu_Pelayanan.
    scenarios = [
        {'id': 'S1', 'desc': 'Sesi 2 (Sore peak)', 'lam': 0.019231, 'mu': 0.019833, 'c': 1, 'duration': 3600},
        {'id': 'S2', 'desc': 'Sesi 3 (Malam peak)', 'lam': 0.019558, 'mu': 0.018165, 'c': 1, 'duration': 3600},
        {'id': 'S3', 'desc': 'Sesi 4 (Malam)', 'lam': 0.022660, 'mu': 0.021372, 'c': 1, 'duration': 3600},
        {'id': 'S4', 'desc': 'Hipotetis: Sesi 3 + 1 Nozzle', 'lam': 0.019558, 'mu': 0.018165, 'c': 2, 'duration': 3600},
        {'id': 'S5', 'desc': 'Hipotetis: Sesi 3 (Event Sudirman, lambda +50%)', 'lam': 0.019558 * 1.5, 'mu': 0.018165, 'c': 1, 'duration': 3600}
    ]
    
    results = []
    
    for s in scenarios:
        # Running 10 replications per scenario to get a stable average
        n_replications = 10
        wq_list, lq_list, rho_list = [], [], []
        
        for _ in range(n_replications):
            res = run_simulation(s['lam'], s['mu'], s['c'], s['duration'])
            wq_list.append(res['Wq'])
            lq_list.append(res['Lq'])
            rho_list.append(res['rho'])
            
        results.append({
            'Scenario': s['id'],
            'Description': s['desc'],
            'lambda': s['lam'],
            'mu': s['mu'],
            'c': s['c'],
            'Wq (Sim)': np.mean(wq_list),
            'Lq (Sim)': np.mean(lq_list),
            'rho (Sim)': np.mean(rho_list)
        })
        
    return pd.DataFrame(results)

def compare_with_empirical(sim_results_df: pd.DataFrame, empirical_data: dict = None) -> pd.DataFrame:
    """
    Compare simulation results with empirical data.
    """
    if empirical_data is None:
        # Data empiris dari notebook analisis
        empirical_data = {  
            'S1': {'Wq (Emp)': 264.50, 'Lq (Emp)': 6.0},
            'S2': {'Wq (Emp)': 515.24, 'Lq (Emp)': 11.92},
            'S3': {'Wq (Emp)': 299.39, 'Lq (Emp)': 6.33},
        }
    
    # Map empirical data to simulation results
    sim_results_df['Wq (Emp)'] = sim_results_df['Scenario'].apply(lambda x: empirical_data.get(x, {}).get('Wq (Emp)', None))
    sim_results_df['Lq (Emp)'] = sim_results_df['Scenario'].apply(lambda x: empirical_data.get(x, {}).get('Lq (Emp)', None))
    
    # Calculate Error (Absolute Difference)
    sim_results_df['Diff_Wq'] = abs(sim_results_df['Wq (Sim)'] - sim_results_df['Wq (Emp)'])
    sim_results_df['Diff_Lq'] = abs(sim_results_df['Lq (Sim)'] - sim_results_df['Lq (Emp)'])
    
    return sim_results_df

def plot_timeline(timeline_data, title="Antrian vs Waktu"):
    """
    Plot the queue length over time.
    """
    df = pd.DataFrame(timeline_data)
    plt.figure(figsize=(10, 5))
    plt.plot(df['time'], df['queue_length'], drawstyle='steps-post', label='Panjang Antrian')
    plt.title(title)
    plt.xlabel("Waktu (Menit)")
    plt.ylabel("Jumlah Kendaraan dalam Antrian (Lq)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.show()

if __name__ == "__main__":
    print("Menjalankan seluruh skenario simulasi...")
    df_results = run_all_scenarios()
    
    print("\nHasil Simulasi:")
    print(df_results.to_string(index=False))
    
    print("\nMembandingkan dengan Data Empiris...")
    df_comparison = compare_with_empirical(df_results)
    print(df_comparison[['Scenario', 'Wq (Sim)', 'Wq (Emp)', 'Diff_Wq', 'Lq (Sim)', 'Lq (Emp)', 'Diff_Lq']].to_string(index=False))
    
    print("\nMembuat plot timeline untuk contoh Skenario 2 (Malam Peak)...")
    # Menggunakan parameter asli S2
    res_s2 = run_simulation(lam=0.019558, mu=0.018165, c=1, duration=3600)
    plot_timeline(res_s2['timeline'], title="Skenario 2 - Malam Peak")
    print("Selesai! Tutup jendela grafik untuk mengakhiri program.")
