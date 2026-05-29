import streamlit as st
import pandas as pd
import plotly.express as px

def render_queue_chart(queue_timeline):
    """
    Render a step line chart of Queue Length (Lq) vs Time.
    """
    if not queue_timeline:
        st.warning("Data timeline kosong.")
        return
        
    df = pd.DataFrame(queue_timeline)
    
    # Convert time from seconds to minutes for better readability on x-axis
    df['time_min'] = df['time'] / 60.0
    
    fig = px.line(
        df, 
        x='time_min', 
        y='queue_length', 
        title='Perkembangan Antrian (Lq) seiring Waktu',
        labels={'time_min': 'Waktu (Menit)', 'queue_length': 'Jumlah Kendaraan Antri'},
        line_shape='hv' # Step line format
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridcolor='rgba(200,200,200,0.2)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(200,200,200,0.2)'),
        hovermode="x unified"
    )
    fig.update_traces(line_color='#FF4B4B', line_width=2)
    
    st.plotly_chart(fig, use_container_width=True)

def render_results_table(wq, lq, rho, total_served):
    """
    Render the main KPI metrics and a descriptive table.
    """
    st.subheader("📊 Hasil Simulasi")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="Rata-rata Waktu Antri (Wq)", value=f"{wq:.2f} dtk")
    with col2:
        st.metric(label="Rata-rata Panjang Antrian (Lq)", value=f"{lq:.2f} mtr")
    with col3:
        st.metric(label="Utilisasi Nozzle (ρ)", value=f"{rho*100:.1f}%")
    with col4:
        st.metric(label="Total Dilayani", value=f"{total_served} kndr")
    
    # Optional: You can also show it as a dataframe if needed, 
    # but st.metric is usually cleaner for KPIs.
    st.markdown("---")
