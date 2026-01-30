import streamlit as st
import pandas as pd
import os
from difflib import get_close_matches

# 1. Page Config
st.set_page_config(page_title="RRKLT Estate Collection", layout="wide")

# 2. State Initialization
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = 'Grid'
if 'limit' not in st.session_state: 
    st.session_state.limit = 48

# 3. Comprehensive Theme Engine
if st.session_state.dark_mode:
    bg_color = "#0f172a"
    sidebar_bg = "#1e293b"
    card_border = "#334155"
    title_color = "#cbd5e1"
    muted_color = "#94a3b8"
    price_color = "#52b788" 
    text_color = "#e2e8f0"
else:
    bg_color = "#ffffff"
    sidebar_bg = "#f8fafc"
    card_border = "#e2e8f0"
    title_color = "#64748b"  
    muted_color = "#94a3b8"  
    price_color = "#52b788"  
    text_color = "#1e293b"

st.markdown(f"""
    <style>
    /* Global App Background */
    .stApp {{
        background-color: {bg_color} !important;
        color: {text_color} !important;
    }}
    
    /* Sidebar Background and Widget Labels */
    [data-testid="stSidebar"] {{
        background-color: {sidebar_bg} !important;
    }}
    
    /* Centered Sidebar Title */
    .centered-sidebar-title {{
        text-align: center !important;
        color: {title_color} !important;
        font-weight: bold;
        font-size: 24px;
        margin-bottom: 20px;
    }}

    /* Sidebar Buttons - Light Mode Operation Fix */
    [data-testid="stSidebar"] button {{
        background-color: {bg_color} !important;
        color: {title_color} !important;
        border: 1px solid {card_border} !important;
    }}
    [data-testid="stSidebar"] button:hover {{
        border-color: {price_color} !important;
        color: {price_color} !important;
    }}

    /* LIST / EXPANDER FIX: Prevent dark background on un-hover */
    .stExpander {{
        background-color: transparent !important;
        border: none !important;
        border-top: 1px solid {card_border} !important;
    }}
    
    .stExpander > div:first-child:hover, 
    .stExpander > div:first-child:active,
    .stExpander > div:first-child {{
        background-color: transparent !important;
        color: {title_color} !important;
    }}

    /* List Item Summary Text Operation */
    .list-summary-container {{
        display: flex;
        justify-content: space-between;
        width: 100%;
        color: {title_color} !important;
        font-weight: 700;
        font-size: 14px;
    }}
    .list-summary-price {{
        color: {price_color} !important;
        font-weight: 800;
    }}

    /* Unified Typography */
    .grid-stamp-title, .row-title, .list-title {{
        font-size: 14px !important;
        font-weight: 700 !important;
        color: {title_color} !important;
    }}
    
    .price-text {{
        font-size: 16px !important;
        font-weight: 800 !important;
        color: {price_color} !important;
    }}
    
    .muted-label {{
        color: {muted_color} !important;
        font-size: 12px !important;
    }}

    /* Return to Top Button */
    .top-button {{
        background-color: #cbd5e1 !important;
        color: #1e293b !important;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        margin-bottom: 15px;
        text-decoration: none;
        display: block;
        border: 1px solid #94a3b8;
    }}
    </style>
    """, unsafe_allow_html=True)

# 4. Data Loading
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
st.sidebar.markdown(f"<div class='centered-sidebar-title'>Gallery Controls</div>", unsafe_allow_html=True)
st.sidebar.markdown("<a href='#top' class='top-button'>⬆️ Return to Top</a>", unsafe_allow_html=True)

col_v1, col_v2, col_v3 = st.sidebar.columns(3)
if col_v1.button("Grid ⣿"): st.session_state.view_mode = 'Grid'
if col_v2.button("Row ☰"): st.session_state.view_mode = 'Rows'
if col_v3.button("List ☷"): st.session_state.view_mode = 'Details'

st.sidebar.markdown("---")
sort_option = st.sidebar.selectbox("Sort Price:", ["Original", "Low to High", "High to Low"])
st.sidebar.markdown("---")

if st.sidebar.button("❌ Reset All Filters"):
    st.session_state.limit = 48
    st.rerun()

def get_opts(col):
    vals = df_raw[col].unique()
    return sorted([str(x) for x in vals if str(x).strip() != ''])

st.sidebar.multiselect("Stamp Type", get_opts('item_specifics_03_stamp_type'))
st.sidebar.multiselect("Condition", get_opts('item_specifics_04_condition'))
st.sidebar.multiselect("Centering", get_opts('item_specifics_08_centering'))
st.sidebar.multiselect("Stamp Format", get_opts('item_specifics_05_stamp_format'))
st.sidebar.selectbox("Has a Certificate?", ["All", "Yes", "No"])

st.sidebar.markdown(f'<p style="font-size:11px; color:{muted_color}; text-align:center; margin-top:10px;">💡 Hold <b>Ctrl</b> (Win) or <b>Cmd</b> (Mac) to select multiple options.</p>', unsafe_allow_html=True)

st.sidebar.markdown("---")
if st.sidebar.button("🌓 Toggle Dark/Light Mode"):
    st.session_state.dark_mode = not st.session_state.dark_mode
    st.rerun()

# --- MAIN CONTENT ---
st.markdown("<div id='top'></div>", unsafe_allow_html=True)

if os.path.exists("racingstamp.png"):
    _, cent_co, _ = st.columns([1, 1, 1])
    cent_co.image("racingstamp.png", width=200)

st.markdown(f"<h1 style='text-align: center; color: {title_color};'>RRKLT Estate Collection</h1>", unsafe_allow_html=True)
st.markdown(f'<p style="text-align:center; font-style:italic; color:{muted_color}; margin-bottom: 25px;">This collection of stamps was acquired by Richard Kucia from 1940 through 2024, and passed to the Richard Kucia Trust at his death in 2025.</p>', unsafe_allow_html=True)

search = st.text_input("🔍 Search", placeholder="Fuzzy search active...")

df = df_raw.copy()
# (Filtering Logic here...)

st.info(f"Showing {len(df)} items match your selection.")
df_show = df.head(st.session_state.limit)

# --- DISPLAY ---
if st.session_state.view_mode == 'Grid':
    grid_cols = st.columns(4)
    for i, (_, row) in enumerate(df_show.iterrows()):
        with grid_cols[i % 4]:
            st.markdown(f'<div style="border-top: 1px solid {card_border}; padding-top:10px; margin-bottom:20px;">', unsafe_allow_html=True)
            imgs = str(row['image']).split('||')
            if imgs[0].startswith('http'):
                st.image(imgs[0], use_container_width=True)
            st.markdown(f'<p class="grid-stamp-title">{row["name"]}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="price-text">${row["formatted_price"]}</p>', unsafe_allow_html=True)
            with st.expander("Details"):
                st.markdown(f'<p class="muted-label"><b>Cat #:</b> {row["item_specifics_02_catalog_number"]}</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.view_mode == 'Rows':
    for _, row in df_show.iterrows():
        c1, c2 = st.columns([0.6, 3.4])
        with c1:
            imgs = str(row['image']).split('||')
            if imgs[0].startswith('http'): st.image(imgs[0], width=110)
        with c2:
            st.markdown(f'<div style="display:flex; justify-content:space-between;"><p class="row-title">{row["name"]}</p><p class="price-text">${row["formatted_price"]}</p></div>', unsafe_allow_html=True)
        st.markdown(f'<div style="border-top:1px solid {card_border}; margin: 10px 0;"></div>', unsafe_allow_html=True)

else: # LIST VIEW
    for i, row in df_show.iterrows():
        # Summary string matches Grid/Row fonts: Slate Name | Green Price
        label_html = f'<div class="list-summary-container"><span>{row["name"][:45]}...</span><span class="list-summary-price">${row["formatted_price"]}</span></div>'
        with st.expander(label_html):
            st.markdown(f"<p class='list-title' style='font-size:18px !important;'>{row['name']}</p>", unsafe_allow_html=True)
            st.markdown(f'<p class="price-text">${row["formatted_price"]}</p>', unsafe_allow_html=True)
            st.write(row['description'])
        st.markdown(f'<div style="border-top:1px solid {card_border}; margin: 2px 0;"></div>', unsafe_allow_html=True)

if len(df) > st.session_state.limit:
    if st.button(f"🔽 Load more items"):
        st.session_state.limit += 48
        st.rerun()

st.write("---")
st.caption("RRKLT Estate Collection, formerly of Cranberry Township, PA.")
