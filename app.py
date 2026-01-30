import streamlit as st
import pandas as pd
import os
from difflib import get_close_matches

# 1. Page Config
st.set_page_config(page_title="RRKLT Estate Collection", layout="wide")

# 2. Premium CSS Overhaul
st.markdown("""
    <style>
    /* Main Background & Font */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Premium Card Styling */
    .stamp-card {
        background: white;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
        border: 1px solid #eaeaea;
    }
    .stamp-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 20px rgba(0,0,0,0.1);
        border-color: #d1d1d1;
    }
    
    /* Typography Hierarchy */
    .grid-stamp-title {
        font-size: 14px !important;
        font-weight: 700;
        color: #1a1a1a;
        line-height: 1.3;
        margin-top: 10px;
        height: 2.6em;
        overflow: hidden;
    }
    .price-tag {
        font-size: 16px;
        color: #2e7d32;
        font-weight: 800;
        margin-top: 5px;
    }
    .metadata-label {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #757575;
        font-weight: 600;
    }
    
    /* Sidebar Polish */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #eaeaea;
    }
    
    /* Custom Button Styling */
    div.stButton > button {
        border-radius: 8px;
        border: 1px solid #dcdfe4;
        background-color: white;
        color: #374151;
        font-weight: 600;
        transition: all 0.2s;
    }
    div.stButton > button:hover {
        border-color: #2563eb;
        color: #2563eb;
        background-color: #eff6ff;
    }

    /* Image Framing */
    .img-frame {
        background-color: #f3f4f6;
        border-radius: 8px;
        padding: 10px;
        display: flex;
        justify-content: center;
        align-items: center;
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
    df['search_blob'] = (df['name'].astype(str) + " " + 
                         df['item_specifics_02_catalog_number'].astype(str) + " " + 
                         df['item_specifics_01_country'].astype(str)).str.lower()
    return df

df_raw = load_data()

# --- SIDEBAR ---
st.sidebar.title("🔍 Controls")
st.sidebar.markdown("<a href='#top' style='text-decoration:none;'><div style='background-color:#2563eb;color:white;padding:10px;border-radius:8px;text-align:center;font-weight:bold;margin-bottom:20px;'>⬆️ Return to Top</div></a>", unsafe_allow_html=True)

if 'view_mode' not in st.session_state:
    st.session_state.view_mode = 'Grid'
if 'limit' not in st.session_state: 
    st.session_state.limit = 48

col_v1, col_v2, col_v3 = st.sidebar.columns(3)
if col_v1.button("Grid ⣿"):
    st.session_state.view_mode = 'Grid'
if col_v2.button("Rows ☰"):
    st.session_state.view_mode = 'Rows'
if col_v3.button("Details ☷"):
    st.session_state.view_mode = 'Details'

st.sidebar.markdown("---")
sort_option = st.sidebar.selectbox("Sort Price:", ["Original", "Low to High", "High to Low"])

st.sidebar.markdown("---")
if st.sidebar.button("❌ Reset Filters"):
    st.session_state.limit = 48
    st.rerun()

def get_opts(col):
    vals = df_raw[col].unique()
    return sorted([str(x) for x in vals if str(x).strip() != ''])

f_type = st.sidebar.multiselect("Stamp Type", get_opts('item_specifics_03_stamp_type'))
f_cond = st.sidebar.multiselect("Condition", get_opts('item_specifics_04_condition'))
f_cent = st.sidebar.multiselect("Centering", get_opts('item_specifics_08_centering'))
f_form = st.sidebar.multiselect("Stamp Format", get_opts('item_specifics_05_stamp_format'))
f_has_cert = st.sidebar.selectbox("Has Certificate?", ["All", "Yes", "No"])

# --- TOP SECTION ---
st.markdown("<div id='top'></div>", unsafe_allow_html=True)

if os.path.exists("racingstamp.png"):
    _, cent_co, _ = st.columns([1, 0.5, 1])
    cent_co.image("racingstamp.png", use_container_width=True)

st.markdown("<h1 style='text-align: center; color: #111827; font-size: 42px;'>RRKLT Estate Collection</h1>", unsafe_allow_html=True)
st.markdown('<p style="color: #6b7280; font-style: italic; text-align: center; max-width: 800px; margin: 0 auto 30px auto;">This collection of stamps was acquired by Richard Kucia from 1940 through 2024, and passed to the Richard Kucia Trust at his death in 2025.</p>', unsafe_allow_html=True)

search = st.text_input("", placeholder="🔍 Search catalog numbers, countries, or names...", label_visibility="collapsed")

# --- FILTERING ---
df = df_raw.copy()
if search:
    s_term = search.lower()
    df = df[df['search_blob'].apply(lambda x: s_term in x or len(get_close_matches(s_term, x.split(), n=1, cutoff=0.7)) > 0)]

if f_type: df = df[df['item_specifics_03_stamp_type'].isin(f_type)]
if f_cond: df = df[df['item_specifics_04_condition'].isin(f_cond)]
if f_cent: df = df[df['item_specifics_08_centering'].isin(f_cent)]
if f_form: df = df[df['item_specifics_05_stamp_format'].isin(f_form)]

if f_has_cert == "Yes": 
    df = df[df['item_specifics_09_has_a_certificate'].str.contains("Yes", case=False)]
elif f_has_cert == "No": 
    df = df[~df['item_specifics_09_has_a_certificate'].str.contains("Yes", case=False)]

if sort_option == "Low to High": df = df.sort_values("buyout_price")
elif sort_option == "High to Low": df = df.sort_values("buyout_price", ascending=False)

st.write(f"Showing **{len(df)}** stamps")

df_show = df.head(st.session_state.limit)

# --- DISPLAY LAYOUTS ---
if st.session_state.view_mode == 'Grid':
    grid_cols = st.columns(4)
    for i, (_, row) in enumerate(df_show.iterrows()):
        with grid_cols[i % 4]:
            st.markdown('<div class="stamp-card">', unsafe_allow_html=True)
            imgs = str(row['image']).split('||')
            if imgs[0].startswith('http'):
                st.markdown('<div class="img-frame">', unsafe_allow_html=True)
                st.image(imgs[0], use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown(f'<div class="grid-stamp-title">{row["name"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-tag">${row["formatted_price"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metadata-label">CAT # {row["item_specifics_02_catalog_number"]}</div>', unsafe_allow_html=True)
            
            with st.expander("Quick View"):
                st.caption(row['description'][:150] + "...")
                if len(imgs) > 1:
                    st.image(imgs[1], use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.view_mode == 'Rows':
    for _, row in df_show.iterrows():
        with st.container():
            st.markdown('<div class="stamp-card">', unsafe_allow_html=True)
            c1, c2 = st.columns([0.8, 3.2])
            with c1:
                imgs = str(row['image']).split('||')
                if imgs[0].startswith('http'):
                    st.image(imgs[0], width=140)
            with c2:
                st.markdown(f'<div style="display: flex; justify-content: space-between;"><h3>{row["name"]}</h3><h3 style="color:#2e7d32;">${row["formatted_price"]}</h3></div>', unsafe_allow_html=True)
                st.markdown(f"**Country:** {row['item_specifics_01_country']} | **Cat #:** {row['item_specifics_02_catalog_number']} | **Condition:** {row['item_specifics_04_condition']}")
                with st.expander("Full Details"):
                    st.write(row['description'])
                    if len(imgs) > 1:
                        sub = st.columns(4)
                        for j, url in enumerate(imgs[1:]):
                            sub[j % 4].image(url, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

else: # Details View
    for _, row in df_show.iterrows():
        line_text = f"{row['name'][:40]}... | {row['item_specifics_01_country']} | ${row['formatted_price']}"
        with st.expander(line_text):
            st.markdown(f"### {row['name']}")
            imgs = str(row['image']).split('||')
            e1, e2 = st.columns([1, 2])
            with e1:
                if imgs[0].startswith('http'): st.image(imgs[0], use_container_width=True)
            with e2:
                st.write(f"**Catalog Number:** {row['item_specifics_02_catalog_number']}")
                st.write(f"**Condition:** {row['item_specifics_04_condition']}")
                st.write(row['description'])
            if len(imgs) > 1:
                st.markdown("---")
                sub_d = st.columns(4)
                for j, url in enumerate(imgs[1:]):
                    sub_d[j % 4].image(url, use_container_width=True)

# Infinite Scroll
if len(df) > st.session_state.limit:
    if st.button(f"Show More Stamps ({len(df) - st.session_state.limit} remaining)"):
        st.session_state.limit += 48
        st.rerun()

st.write("---")
st.caption("RRKLT Estate Collection")
