import streamlit as st

def footer_buttons():
    st.markdown("<br>", unsafe_allow_html=True)
    # Replicating the Dashboard bottom buttons for all pages
    btn_col1, btn_col2, btn_col3, btn_col4 = st.columns([1, 1, 1, 1])
    with btn_col1:
        st.button("📄 Export Report", key=f"export_{st.session_state.get('page_id', 'gen')}")
    with btn_col2:
        st.button("🔔 Notify Mandi", key=f"notify_{st.session_state.get('page_id', 'gen')}")
    with btn_col3:
        st.button("📧 Share AI Result", key=f"share_{st.session_state.get('page_id', 'gen')}")
    with btn_col4:
        st.button("💾 Save to History", key=f"save_{st.session_state.get('page_id', 'gen')}")
