import streamlit as st
import sys
import os

# Ensure the parent directory is in the Python path so we can import simulation.engine
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulation.engine import run_simulation
from app.components.sidebar import render_sidebar
from app.components.charts import render_queue_chart, render_results_table
from app.components.animation import render_animation

st.set_page_config(
    page_title="Simulasi Antrian SPBU",
    page_icon="⛽",
    layout="wide"
)

def main():
    st.title("⛽ Simulasi Antrian SPBU")
    st.markdown("""
    Aplikasi ini mensimulasikan antrian pada SPBU berdasarkan **Model Antrian M/M/c**.
    Pilih preset skenario di sidebar atau atur parameter secara manual untuk melihat hasilnya.
    """)
    
    # 1. Render Sidebar & Get Parameters
    params = render_sidebar()
    
    # 2. Main Area: Run Simulation Button
    if st.button("🚀 Jalankan Simulasi", type="primary"):
        with st.spinner("Menjalankan simulasi..."):
            # Call engine.py
            results = run_simulation(
                lam=params["lam"],
                mu=params["mu"],
                c=params["c"],
                duration=params["duration"],
                interarrival_dist=params["dist"],
                service_dist=params["dist"]
            )
            
            # Save results to session state so they persist when interacting with animation speed
            st.session_state.sim_results = results
            st.session_state.sim_params = params

    # 3. Display Results if available
    if 'sim_results' in st.session_state:
        res = st.session_state.sim_results
        c_nozzles = st.session_state.sim_params["c"]
        
        st.markdown("---")
        
        # Display KPI and Chart
        render_results_table(res['Wq'], res['Lq'], res['rho'], res['total_customers_served'])
        
        # Debug: Show data availability
        customer_log = res.get('customer_log', [])
        st.caption(f"🔍 Debug: customer_log memiliki {len(customer_log)} entri | Keys di results: {list(res.keys())}")
        
        # Animation (full-width for the wide SPBU canvas)
        st.markdown("---")
        render_animation(customer_log, c_nozzles)
        
        # Queue chart below
        st.markdown("---")
        render_queue_chart(res['timeline'])

if __name__ == "__main__":
    main()
