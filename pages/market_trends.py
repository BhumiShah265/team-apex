import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

def show():
    st.markdown('<h1 class="header-text">Market Trends & Analytics</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subheader-text">Historical price trends and volume analysis across major Gujarat Mandis.</p>', unsafe_allow_html=True)

    # Market Overview Stats
    st.markdown("### 📈 Market Pulse", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="agri-card"><div class="stat-label">Groundnut HPS</div><div class="stat-value">₹7,210</div><div class="stat-trend trend-up">▲ 2.4%</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="agri-card"><div class="stat-label">Cotton (Shankar-6)</div><div class="stat-value">₹6,840</div><div class="stat-trend trend-down">▼ 1.1%</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="agri-card"><div class="stat-label">Cumin (Unjha Mix)</div><div class="stat-value">₹28,500</div><div class="stat-trend trend-up">▲ 5.2%</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="agri-card"><div class="stat-label">Wheat (Lok-1)</div><div class="stat-value">₹2,450</div><div class="stat-trend trend-up">▲ 0.8%</div></div>', unsafe_allow_html=True)

    # Price Trend Chart
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📊 Historical Price Movement (30 Days)", unsafe_allow_html=True)
    
    # Mock data for line chart
    dates = pd.date_range(end=pd.Timestamp.now(), periods=30)
    data = pd.DataFrame({
        'Date': dates,
        'Groundnut': np.random.normal(7000, 100, 30).cumsum() / 5 + 6800,
        'Cotton': np.random.normal(6500, 80, 30).cumsum() / 5 + 6400,
        'Cumin': np.random.normal(27000, 500, 30).cumsum() / 5 + 26000
    })
    
    df_melted = data.melt(id_vars=['Date'], var_name='Crop', value_name='Price (₹/Q)')
    
    fig = px.line(df_melted, x='Date', y='Price (₹/Q)', color='Crop',
                 color_discrete_map={'Groundnut': '#2ecc71', 'Cotton': '#3498db', 'Cumin': '#f1c40f'})
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='var(--text-secondary)',
        height=450,
        margin=dict(l=20, r=20, t=20, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor='rgba(255,255,255,0.05)')
    )
    
    st.markdown('<div class="agri-card">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

    # Market Volume Table
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🏪 Top Mandis by Volume", unsafe_allow_html=True)
    
    mandi_data = {
        "Mandi": ["Gondal", "Rajkot", "Surat", "Amreli", "Jasdan", "Unjha"],
        "Volume (MT)": [1250, 980, 850, 720, 640, 580],
        "Avg Price": ["₹7,110", "₹7,050", "₹7,240", "₹6,980", "₹6,850", "₹27,800"],
        "Trend": ["Stable", "Rising", "Falling", "Rising", "Stable", "Rising"]
    }
    df_mandi = pd.DataFrame(mandi_data)
    st.table(df_mandi)
    
    from utils.components import footer_buttons
    footer_buttons()

if __name__ == "__main__":
    show()
