import streamlit as st
from utils.pdf_gen import generate_all_reports_pdf

def show():
    # Header Section
    st.markdown('<h1 class="header-text">Saved Reports History</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subheader-text">Access your previous plant diagnostics and market price lookups.</p>', unsafe_allow_html=True)

    # Filter Bar
    st.markdown("### 🔍 Filter History", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search_query = st.text_input("Search reports...", placeholder="e.g. Cotton, Groundnut, Heat Stress")
    with col2:
        filter_type = st.selectbox("Filter by Type", ["All Reports", "Diagnosis", "Market Search"])
    with col3:
        sort_by = st.selectbox("Sort by", ["Newest First", "Oldest First"])

    st.markdown("<br>", unsafe_allow_html=True)

    # Report List
    reports = [
        {
            "date": "Oct 24, 2023",
            "location": "Gondal - Groundnut",
            "type": "Diagnosis Result",
            "result": "Aphids Infestation",
            "result_color": "#e74c3c",
            "summary": "Trees show high vulnerability of aphids on current crops. Recommended treatment: Immediate application of organic Neem Oil spray.",
            "confidence": "92%"
        },
        {
            "date": "Oct 22, 2023",
            "location": "Wheat - Rajkot",
            "type": "Diagnosis Result",
            "result": "Healthy",
            "result_color": "#2ecc71",
            "summary": "No major pathogens detected. Plant health is within optimal range for this growth stage.",
            "confidence": "98%"
        },
        {
            "date": "Oct 15, 2023",
            "location": "Groundnut - Jamnagar",
            "type": "Market Search",
            "result": "Market Opportunity Found",
            "result_color": "#2ecc71",
            "summary": "Best price identified at Gondal Mandi (₹7,110). Potential profit margin of +₹450/Q.",
            "confidence": ""
        }
    ]

    # Display individual report cards
    for report in reports:
        st.markdown(f"""
            <div class="agri-card" style="margin-bottom: 1.5rem;">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                    <div>
                        <div style="color: var(--text-secondary); font-size: 0.8rem; font-weight: 500;">{report['date']} • {report['location']}</div>
                        <div style="color: var(--text-primary); font-size: 1.1rem; font-weight: 700; margin-top: 0.25rem;">{report['type']}</div>
                    </div>
                    <div style="background: rgba(46, 204, 113, 0.1); border: 1px solid {report['result_color']}; color: {report['result_color']}; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 600;">
                        {report['result']} {report['confidence']}
                    </div>
                </div>
                <p style="color: var(--text-secondary); font-size: 0.9rem; line-height: 1.5; margin-bottom: 1.5rem;">{report['summary']}</p>
                <div style="display: flex; gap: 10px;">
                    <div style="background: var(--brand-primary); color: black; padding: 6px 15px; border-radius: 6px; font-size: 0.8rem; font-weight: 600; cursor: pointer;">View Full Report</div>
                    <div style="border: 1px solid var(--border-color); color: var(--text-primary); padding: 6px 15px; border-radius: 6px; font-size: 0.8rem; font-weight: 600; cursor: pointer;">Share</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Single PDF Download Section for all reports
    st.markdown("### 📄 Download All Reports", unsafe_allow_html=True)
    st.markdown('<div class="agri-card" style="text-align: center; padding: 2rem;">', unsafe_allow_html=True)
    
    col_left, col_right = st.columns([2, 1])
    with col_left:
        st.markdown(f"""
            <div style="text-align: left;">
                <h3 style="margin-bottom: 0.5rem;">Download Complete Report History</h3>
                <p style="color: var(--text-secondary); margin: 0;">Export all {len(reports)} reports to a single PDF document</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col_right:
        if st.button("📄 Download All as PDF", key="download_all_pdf", use_container_width=True):
            # Generate combined PDF for all reports
            pdf_bytes = generate_all_reports_pdf(reports)
            
            # Create download button
            st.download_button(
                label="📥 Click to Download",
                data=pdf_bytes,
                file_name="krishimitra_report_history.pdf",
                mime="application/pdf",
                key="download_all_btn"
            )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    from utils.components import footer_buttons
    footer_buttons()

if __name__ == "__main__":
    show()
