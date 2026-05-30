import streamlit as st
from app.scenarios import SCENARIOS

def render_sidebar() -> dict:
    st.sidebar.header("⚙️ Konfigurasi Simulasi")
    
    # Dropdown Preset Skenario
    preset_options = ["Custom"] + [s["name"] for s in SCENARIOS.values()]
    
    # Initialize session state for preset if not exists
    if 'selected_preset' not in st.session_state:
        st.session_state.selected_preset = preset_options[1] # Default to Skenario 1
        
    # Callback when preset changes
    def on_preset_change():
        preset = st.session_state.preset_dropdown
        if preset != "Custom":
            # Find scenario dict by name
            for key, s in SCENARIOS.items():
                if s["name"] == preset:
                    st.session_state.lam_slider = float(s["lam"])
                    st.session_state.mu_slider = float(s["mu"])
                    st.session_state.c_selectbox = int(s["c"])
                    st.session_state.duration_input = int(s["duration"])
                    break
                    
    # Initialize session states for inputs if not exist (using Skenario 1 default)
    if 'lam_slider' not in st.session_state:
        st.session_state.lam_slider = SCENARIOS["S1"]["lam"]
    if 'mu_slider' not in st.session_state:
        st.session_state.mu_slider = SCENARIOS["S1"]["mu"]
    if 'c_selectbox' not in st.session_state:
        st.session_state.c_selectbox = SCENARIOS["S1"]["c"]
    if 'duration_input' not in st.session_state:
        st.session_state.duration_input = SCENARIOS["S1"]["duration"]

    # The actual selectbox
    selected_preset = st.sidebar.selectbox(
        "Pilih Skenario Preset", 
        options=preset_options,
        index=preset_options.index(st.session_state.selected_preset) if st.session_state.selected_preset in preset_options else 0,
        key="preset_dropdown",
        on_change=on_preset_change
    )
    
    st.sidebar.markdown("---")
    
    # Callback when manual inputs change
    def on_manual_change():
        st.session_state.preset_dropdown = "Custom"
        st.session_state.selected_preset = "Custom"
    
    # Parameters
    lam = st.sidebar.slider(
        "λ (Arrival Rate - Kendaraan/detik)", 
        min_value=0.0, max_value=1.0, step=0.0001, format="%.4f",
        key="lam_slider",
        on_change=on_manual_change
    )
    
    mu = st.sidebar.slider(
        "μ (Service Rate - Kendaraan/detik)", 
        min_value=0.0, max_value=1.0, step=0.0001, format="%.4f",
        key="mu_slider",
        on_change=on_manual_change
    )
    
    c = st.sidebar.selectbox(
        "Jumlah Nozzle Aktif (c)", 
        options=[1, 2, 3],
        key="c_selectbox",
        on_change=on_manual_change
    )
    
    duration = st.sidebar.number_input(
        "Durasi Simulasi (detik)", 
        min_value=60, max_value=86400, step=60,
        key="duration_input",
        on_change=on_manual_change
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info(
        "💡 **Tip:** Geser slider secara manual untuk mengubah mode menjadi 'Custom'."
    )
    
    return {
        "lam": lam, 
        "mu": mu, 
        "c": c, 
        "duration": duration, 
        "dist": "exponential" # Hardcoded for now based on engine defaults
    }