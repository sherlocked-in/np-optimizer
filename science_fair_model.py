import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="🧠 NP Optimizer", layout="wide")
st.title("🧠🧬 NP BBB Optimizer")

@st.cache_data
def generate_data():
    np.random.seed(42)
    n = 1000  # ✅ FIXED: Reduced from 5000
    # ... [your exact data generation code] ...
    return df

data = generate_data()

# Sidebar (unchanged)
st.sidebar.header("🔧 Filters")
size = st.sidebar.slider("Size", 10, 300, (50, 150))

# Filter
filtered = data[data['Size_nm'].between(*size)]

# Metrics (unchanged)

# FIXED TABLE
st.subheader("🏆 Top 10")
top10 = filtered.nlargest(10, 'BBB_Efficiency').reset_index(drop=True)
st.dataframe(top10.style.background_gradient(subset=['BBB_Efficiency'], cmap='RdYlGn'), 
             width="100%", hide_index=True)

# FIXED PLOTS
@st.cache_data
def safe_plot(df, max_points=500):
    if len(df) > max_points:
        return px.scatter(df.sample(max_points), x='Size_nm', y='BBB_Efficiency')
    return px.scatter(df, x='Size_nm', y='BBB_Efficiency')

st.plotly_chart(safe_plot(filtered), width="100%")
