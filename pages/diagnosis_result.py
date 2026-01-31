import streamlit as st

def show():
    # Header Section
    st.markdown('<h1 class="header-text">AI Diagnosis Result</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subheader-text">Anand, Gujarat • Last updated OCT 24, 10:45 PM</p>', unsafe_allow_html=True)

    # Main Analysis Row
    col_img, col_diag = st.columns([1, 1])

    with col_img:
        st.markdown("### 🖼️ AI Analysis Preview", unsafe_allow_html=True)
        st.markdown("""
            <div class="agri-card" style="height: 480px; position: relative; background: #000; overflow: hidden; display: flex; align-items: center; justify-content: center;">
                <div style="width: 100%; height: 100%; position: absolute; opacity: 0.3;">
                    <!-- Simple SVG Leaf Placeholder -->
                    <svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg" style="width: 100%; height: 100%;">
                        <path fill="#2ecc71" d="M100 20C60 20 20 80 20 120C20 160 100 180 180 120C180 80 140 20 100 20Z" />
                        <path fill="#27ae60" d="M100 20L100 180M100 60L140 80M100 100L160 120M100 140L140 160M100 60L60 80M100 100L40 120M100 140L60 160" stroke="#fff" stroke-width="2"/>
                    </svg>
                </div>
                <!-- Bounding Box -->
                <div style="position: absolute; border: 3px solid #f39c12; border-radius: 4px; width: 60%; height: 40%; top: 30%; left: 20%; box-shadow: 0 0 10px #f39c12;">
                    <div style="background: #f39c12; color: black; font-size: 0.7rem; font-weight: bold; position: absolute; top: -20px; left: -3px; padding: 2px 8px; border-radius: 2px;">
                        HEAT STRESS DETECTED (94.2%)
                    </div>
                </div>
            </div>
            <p style="color: var(--text-secondary); font-size: 0.8rem; margin-top: 1rem; text-align: center;">Uploaded Crop Image - Detected Leaf Stress Area</p>
        """, unsafe_allow_html=True)
        
        # Bottom Stats in Diagnosis
        st.markdown('<br>', unsafe_allow_html=True)
        s_col1, s_col2, s_col3 = st.columns(3)
        with s_col1:
            st.markdown('<div class="agri-card"><div class="stat-label">Confidence</div><div class="stat-value" style="font-size: 1.2rem;">94.2%</div></div>', unsafe_allow_html=True)
        with s_col2:
            st.markdown('<div class="agri-card"><div class="stat-label">Temp</div><div class="stat-value" style="font-size: 1.2rem;">42°C</div></div>', unsafe_allow_html=True)
        with s_col3:
            st.markdown('<div class="agri-card"><div class="stat-label">Moisture</div><div class="stat-value" style="font-size: 1.2rem;">12%</div></div>', unsafe_allow_html=True)

    with col_diag:
        st.markdown("### ️⚠️ Severity: High", unsafe_allow_html=True)
        # Alert Box
        st.markdown("""
            <div class="agri-card" style="border-left: 5px solid #f39c12; background: rgba(243, 156, 18, 0.05);">
                <div style="color: #f39c12; font-weight: 700; font-size: 1.1rem; margin-bottom: 0.5rem;">🚨 Diagnosis: Heat Stress Detected</div>
                <p style="color: var(--text-secondary); margin: 0;">The crop is showing significant signs of thermal stress due to prolonged exposure to high temperatures and low soil moisture.</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # How it reached conclusion
        with st.expander("🔍 How it reached this conclusion?", expanded=True):
            st.markdown("""
            <div style="color: var(--text-secondary); font-size: 0.9rem;">
                    Our Multimodal Transformer combined image data from your upload with real-time hyperlocal weather measurements.
                    <br><br>
                    <b>Key Factors:</b>
                    - Leaves: Curled edges and yellowing.
                    - Soil: Surface level moisture deficit.
                    - Hyperlocal Weather: 14% deviation from regional avg.
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### ✅ Recommended Actions", unsafe_allow_html=True)
        st.markdown("""
            <div class="agri-card">
                <ul style="list-style: none; padding: 0; margin: 0; color: var(--text-secondary); font-size: 0.9rem;">
                    <li style="margin-bottom: 0.8rem; display: flex; align-items: start; gap: 10px;">
                        <span style="color: #2ecc71;">✔</span> Use organic mulch (crop residue) to the soil surface to retain moisture and lower soil temperatures.
                    </li>
                    <li style="margin-bottom: 0.8rem; display: flex; align-items: start; gap: 10px;">
                        <span style="color: #2ecc71;">✔</span> Increase irrigation frequency to once every 2 days during peak hours.
                    </li>
                    <li style="margin-bottom: 0.8rem; display: flex; align-items: start; gap: 10px;">
                        <span style="color: #2ecc71;">✔</span> Apply bio-stimulants to help the plant recover from oxidative stress.
                    </li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("Connect with Agri-Expert", key="expert_btn"):
            st.session_state.current_page = "ai chat"
            st.rerun()
        
    from utils.components import footer_buttons
    footer_buttons()

if __name__ == "__main__":
    show()
