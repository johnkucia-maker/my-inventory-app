import streamlit as st
import pandas as pd
import os
from difflib import get_close_matches

# 1. Page Config
st.set_page_config(page_title="RRKLT Estate Collection", layout="wide")

# 2. Custom CSS for High-Density View
st.markdown("""
    <style>
    .grid-stamp-title {
        font-size: 13px !important;
        font-weight: 600;
        line-height: 1.2;
        margin-bottom: 5px;
        height: 3.2em;
        overflow: hidden;
    }
    .row-title {
        font-size: 16px !important;
        font-weight: bold;
        margin: 0;
    }
    .row-metadata {
        font-size: 13px;
        color: #555;
        margin-top: 2px;
    }
    .stamp-card {
        border-top: 1px solid #dee2e6;
        padding: 10px 5px;
        margin-bottom: 5px;
    }
    .estate-intro {
        color: #666;
        font-style: italic;
        text-align: center;
        margin-bottom: 15px;
        font-size: 14px;
    }
    .filter-tip {
        font-size: 11px;
        color: #666;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Data Loading
@st.cache_data
def load_data():
    df = pd.read_csv("inventory.csv")
    df['buyout_price'] = pd.to_numeric(df['buyout_price'], errors='coerce')
    df = df.fillna('')
    df['formatted_price'] = df['buyout_price'].apply(lambda x: f"{x:,.2f}" if pd.notnull(x) else "0.00")
    # Pre-process for fuzzy search
    df['search_blob'] = (df['name'] + " " + df['item_specifics_02_catalog_number'] + " " + df['item_specifics_01_country']).str.lower()
    return df

df_raw = load_data()

# --- SIDEBAR ---
st.sidebar.title("🔍 Gallery Controls")
st.sidebar.markdown("<a href='#top' style='text-decoration:none;'><div style='background-color:#f0f2f6;padding:10px;border-radius:5px;text-align:center;border:1px solid #dcdfe4;font-weight:bold;margin-bottom:10px;'>⬆️ Return to Top</div></a>", unsafe_allow_html=True)

if 'view_mode' not in st.session_state:
    st.session_state.view_mode = 'Grid'

col_v1, col_v2 = st.sidebar.columns(2)
if col_v1.button("⣿ Grid"):
    st.session_state.view_mode = 'Grid'
if col_v2.button("☰ Rows"):
    st.session_state.view_mode = 'Rows'

st.sidebar.markdown("---")
sort_option = st.sidebar.selectbox("Sort Price:", ["Original", "Low to High", "High to Low"])
st.sidebar.markdown("---")

if st.sidebar.button("❌ Reset All Filters"):
    st.session_state.limit = 24
    st.rerun()

def get_opts(col):
