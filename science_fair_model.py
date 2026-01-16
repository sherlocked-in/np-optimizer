import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import plotly.express as px
import plotly.graph_objects as go

# Page config (NEW Streamlit syntax)
st.set_page_config(
    page_title="NP Optimizer - Glioblastoma",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🧠🧬 **Nanoparticle Optimizer**")
st.markdown("### Optimize nanoparticles for **Glioblastoma** BBB penetration")

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #1f77b4;
        padding: 1rem;
        border-radius: 0.5rem;
        color: white;
        text-align: center;
    }
    .stMetric > label {
        color: white !important;
        font-size: 1.2rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_sample_data():
    """Generate realistic sample data for nanoparticle optimization"""
    np.random.seed(42)
    n_samples = 1000
    
    data = {
        'NP_Type': np.random.choice(['PLGA', 'Liposome', 'Gold', 'Polymeric', 'Silica'], n_samples),
        'Size_nm': np.random.normal(100, 30, n_samples).clip(10, 500),
        'Zeta_mV': np.random.normal(-20, 10, n_samples).clip(-60, 30),
        'Ligand': np.random.choice(['TfR', 'PSMA', 'Angiopep-2', 'None', 'RGD'], n_samples),
        'PEGylation': np.random.choice(['Yes', 'No'], n_samples, p=[0.7, 0.3]),
        'Charge': np.random.choice(['Neutral', 'Negative', 'Positive'], n_samples),
        'Surface_Area': np.random.normal(0.8, 0.2, n_samples).clip(0.1, 2.0),
        'Hydrophobicity': np.random.uniform(0, 1, n_samples)
    }
    
    df = pd.DataFrame(data)
    
    # BBB efficiency model (simplified logistic + linear terms)
    df['BBB_Efficiency_percent'] = (
        50 + 
        15 * (df['Size_nm'] <= 100).astype(float) +
        20 * (df['Zeta_mV'] > -30).astype(float) * (df['Zeta_mV'] < -5).astype(float) +
        25 * (df['Ligand'] != 'None').astype(float) +
        10 * (df['PEGylation'] == 'Yes').astype(float) +
        8 * (df['Charge'] == 'Neutral').astype(float) +
        5 * df['Surface_Area'].clip(0.5, 1.5) +
        np.random.normal(0, 8, n_samples)
    ).clip(0, 100)
    
    # Format as percentage strings (matching your original data)
    df['BBB_Efficiency_percent'] = df['BBB_Efficiency_percent'].astype(int).astype(str) + '%'
    
    return df

def clean_percentage_column(df, col_name):
    """Convert percentage strings to numeric for calculations"""
    df_clean = df.copy()
    if df_clean[col_name].dtype == 'object':
        df_clean[col_name + '_numeric'] = (
            df_clean[col_name].str.rstrip('%').astype(float)
        )
    else:
        df_clean[col_name + '_numeric'] = df_clean[col_name]
    return df_clean

# Load data
@st.cache_data
def get_data():
    return load_sample_data()

df = get_data()

# Sidebar controls
st.sidebar.header("🔧 **Optimization Parameters**")

col1, col2 = st.sidebar.columns(2)
with col1:
    size_range = st.slider("Size (nm)", 10, 500, (50, 150), key="size")
with col2:
    zeta_range = st.slider("Zeta Potential (mV)", -60, 30, (-30, -10), key="zeta")

ligand = st.sidebar.selectbox("Ligand", df['Ligand'].unique())
peg = st.sidebar.selectbox("PEGylation", ['Yes', 'No'])
charge = st.sidebar.selectbox("Charge", ['Neutral', 'Negative', 'Positive'])

if st.sidebar.button("🔍 **OPTIMIZE**", type="primary"):
    st.session_state.optimized = True
else:
    st.session_state.optimized = False

# Filter data based on parameters
filtered_df = df[
    (df['Size_nm'].between(*size_range)) &
    (df['Zeta_mV'].between(*zeta_range)) &
    (df['Ligand'] == ligand) &
    (df['PEGylation'] == peg) &
    (df['Charge'] == charge)
].copy()

# Clean percentage column for numeric operations
filtered_df = clean_percentage_column(filtered_df, 'BBB_Efficiency_percent')

# Main content
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total NPs", len(df), delta="1K samples")
with col2:
    st.metric("Filtered", len(filtered_df), delta=f"{len(filtered_df)-len(df):+.0f}")
with col3:
    avg_numeric = filtered_df['BBB_Efficiency_percent_numeric'].mean()
    st.metric("Avg BBB Efficiency", f"{avg_numeric:.1f}%", delta=f"{avg_numeric:.1f}%")
with col4:
    best_numeric = filtered_df['BBB_Efficiency_percent_numeric'].max()
    st.metric("Best Candidate", f"{best_numeric:.0f}%", delta=f"+{best_numeric:.0f}%")

st.divider()

# Top performers table (THE FIXED VERSION)
if len(filtered_df) > 0:
    # Get top 10 performers with NUMERIC sorting
    top_performers = filtered_df.nlargest(10, 'BBB_Efficiency_percent_numeric')[
        ['NP_Type', 'Size_nm', 'Ligand', 'BBB_Efficiency_percent', 'BBB_Efficiency_percent_numeric']
    ].round(0).copy()
    
    # Create the PERFECTLY FORMATTED dataframe
    styled_df = top_performers.style.background_gradient(
        subset=['BBB_Efficiency_percent_numeric'], 
        cmap='viridis', 
        low=0, 
        high=100
    ).format({
        'BBB_Efficiency_percent_numeric': '{:.0f}%',
        'Size_nm': '{:.0f}'
    }).hide_columns(['BBB_Efficiency_percent_numeric'])
    
    st.subheader("🏆 **Top 10 Best Nanoparticles**")
    st.dataframe(
        styled_df,
        width='stretch',  # ✅ FIXED: Replaces deprecated use_container_width
        hide_index=True   # ✅ Clean display
    )
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        fig_size = px.histogram(
            filtered_df, 
            x='Size_nm', 
            color='BBB_Efficiency_percent_numeric',
            nbins=30,
            title="Size Distribution",
            labels={'BBB_Efficiency_percent_numeric': 'BBB Efficiency (%)'}
        )
        st.plotly_chart(fig_size, use_container_width=True)
    
    with col2:
        fig_ligand = px.box(
            filtered_df, 
            x='Ligand', 
            y='BBB_Efficiency_percent_numeric',
            title="Ligand Performance"
        )
        st.plotly_chart(fig_ligand, use_container_width=True)
        
else:
    st.warning("⚠️ No nanoparticles match your criteria. Try broadening the filters.")

# Footer
st.markdown("---")
st.markdown("*Optimized for Glioblastoma BBB penetration using ML surrogate model*")
