import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from streamlit.components.v1 import html

#import vues
from views import vente_views







# ========== CSS Style ===============
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

html("""
<style>
    @import url("https://fonts.googleapis.com/css2?family=Acme&family=Dancing+Script:wght@400..700&family=Dosis:wght@200..800&family=Merienda:wght@300..900&family=Quicksand:wght@300..700&family=Satisfy&display=swap");
    
  .box {
    color: #eee;
    padding: 20px;
    font-family: 'Dancing Script', cursive;
    border-radius: 10px;
    font-size: 74px;
  }
</style>
<div class="box">Vente</div>
""")


st.markdown(vente_views.custom_css, unsafe_allow_html=True)
st.markdown(vente_views.kpis_html, unsafe_allow_html=True)



# ========== LEFT SECTION (Visitors + Graph) ==========
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    <div class="card section-card">
        <div class="section-header">
            <h4>Online Store Sessions</h4>
            <button class="view-report-btn">View Report</button>
        </div>
        <p class="visitors-count">Visitors: <strong>68</strong></p>
        <p class="visitor-details">
            <span class="positive">↑ 15.6%</span> &nbsp;&nbsp;
            <span class="negative">↓ 1.6%</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Simulated data
    days = pd.date_range("2025-07-21", periods=7).strftime("%d").tolist()
    values = [6, 8, 10, 7, 9, 11, 15]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=days, y=values, mode="lines+markers", line=dict(color="#4A6CF7", width=3)))
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=250, xaxis_title=None, yaxis_title=None)
    st.plotly_chart(fig, use_container_width=True)

# ========== RIGHT SECTION ==========
with col2:
    st.markdown("""
    <div class="promo-card">
        <p class="promo-title">Need More Stats?</p>
        <p class="promo-subtext">Upgrade to pro for added benefits.</p>
        <button class="go-pro-btn">Go Pro Now</button>
    </div>
    """, unsafe_allow_html=True)

    # Gauge chart for conversion
    fig2 = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=58.19,
        delta={'reference': 50, 'increasing': {'color': "#28a745"}},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#4A6CF7"},
            'bgcolor': "white",
        },
        domain={'x': [0, 1], 'y': [0, 1]},
        number={'suffix': "%"}
    ))
    fig2.update_layout(height=250, margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("""
    <div class="conversion-footer">
        <span>💰 <strong>Income:</strong> $542,317</span><br>
        <span>💸 <strong>Expenses:</strong> $497,456</span>
    </div>
    """, unsafe_allow_html=True)
