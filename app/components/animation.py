import streamlit as st
import streamlit.components.v1 as components
import json
import os

def render_animation(customer_log, c_nozzles):
    """
    Membungkus file animation_2d.html dan menyisipkan data customer_log
    langsung ke dalam variabel JavaScript di HTML.
    """
    st.subheader("🎥 Animasi 2D SPBU")
    
    if not customer_log:
        st.info("Jalankan simulasi untuk melihat animasi.")
        return

    st.caption(f"📊 {len(customer_log)} kendaraan tercatat | ⛽ {c_nozzles} nozzle aktif")

    # Get absolute path to the HTML file
    dir_path = os.path.dirname(os.path.realpath(__file__))
    html_path = os.path.join(dir_path, "animation_2d.html")
    
    # Read the HTML content
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
        
    # Serialize customer log to JSON
    json_log = json.dumps(customer_log)
    
    # Directly replace placeholder variables in the HTML source
    # This is more reliable than appending a separate <script> injection
    html_with_data = html_content.replace(
        'var customerLog = [];',
        'var customerLog = ' + json_log + ';'
    ).replace(
        'var cNozzles = 1;',
        'var cNozzles = ' + str(int(c_nozzles)) + ';'
    )
    
    # Render the HTML component in Streamlit
    components.html(html_with_data, height=720)