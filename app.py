import streamlit as st
import pandas as pd
import os
from difflib import get_close_matches

# 1. Page Config
st.set_page_config(page_title="RRKLT Estate Collection", layout="wide")

# 2. Custom CSS for High-Density View and Typography
st.markdown("""
    <style>
    /* Grid Title Font Scaling */
    .grid-stamp-title {
        font-size: 13px !important;
        font-weight: 600;
        line-height: 1.2;
        margin-bottom: 5px;
        height: 3.2em;
        overflow: hidden;
    }
    /* Row View Compression */
    .row-title {
        font-size: 16px !important;
        font-weight: bold;
        margin-bottom: 2px;
    }
    .row-metadata {
        font-size: 13px;
        color: #555;
    }
    /* Standardized Hairline */
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
    /* Fixed Image Size for Row View */
    .row-image-container img {
        max-height: 120px;
        width: auto;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Data Loading with Currency Formatting
@st.cache_data
def load_data():
    df = pd.read_csv("inventory.csv")
    df['buyout_price'] = pd.to_numeric(df['buyout_price'], errors='coerce')
    df = df.fillna('')
    df['formatted_price'] = df['buyout_price'].apply(lambda x: f"{x:,.2f}" if pd.notnull(x) else "0.00")
    # Pre-process search string for fuzzy matching
    df['search_blob'] = (df['name'] + " " + df['item_specifics_02_catalog_number'] + " " + df['item_specifics_01_country']).str.lower()
    return df

df_raw = load_data()

# --- SIDEBAR CONTROLS ---
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
    return sorted([str(x) for x in df_raw[col].unique() if str(x).strip() != ''])

f_type = st.sidebar.multiselect("Stamp Type", get_opts('item_specifics_03_stamp_type'))
f_cond = st.sidebar.multiselect("Condition", get_opts('item_specifics_04_condition'))
f_cent = st.sidebar.multiselect("Centering", get_opts('item_specifics_08_centering'))
f_form = st.sidebar.multiselect("Stamp Format", get_opts('item_specifics_05_stamp_format'))
f_has_cert = st.sidebar.selectbox("Has a Certificate?", ["All", "Yes", "No"])

st.sidebar.markdown('<p class="filter-tip">💡 Hold <b>Ctrl</b> (Win) or <b>Cmd</b> (Mac) to select multiple options.</p>', unsafe_allow_html=True)

# --- TOP SECTION ---
st.markdown("<div id='top'></div>", unsafe_allow_html=True)

if os.path.exists("racingstamp.png"):
    _, cent_co, _ = st.columns([1, 1, 1])
    cent_co.image("racingstamp.png", width=200)

st.markdown("<h1 style='text-align: center;'>RRKLT Estate Collection</h1>", unsafe_allow_html=True)
st.markdown('<p class="estate-intro">This collection of stamps was acquired by Richard Kucia from 1940 through 2024, and passed to the Richard Kucia Trust at his death in 2025.</p>', unsafe_allow_html=True)

search = st.text_input("🔍 Search Name, Catalog #, or Country", placeholder="Search with fuzzy matching (spelling doesn't have to be perfect)...")

# --- FILTERING LOGIC (FUZZY SEARCH) ---
df = df_raw.copy()

if search:
    search_term = search.lower()
    # Fuzzy matching logic: checks contains OR close matches
    df = df[df['search_blob'].apply(lambda x: search_term in x or len(get_close_matches(search_term, x.split(), n=1, cutoff=0.7)) > 0)]

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

st.info(f"Showing {len(df)} items match your selection.")

# --- INFINITE SCROLL LOGIC ---
if 'limit' not in st.session_state: 
    st.session_state.limit = 24

df_show = df.head(st.session_state.limit)

# --- DISPLAY ---
if st.session_state.view_mode == 'Grid':
    grid_cols = st.columns(4)
    for i, (_, row) in enumerate(df_show.iterrows()):
        with grid_cols[i % 4]:
            st.markdown('<div class="stamp-card">', unsafe_allow_html=True)
            imgs = str(row['image']).split('||')
            if imgs[0].startswith('http'):
                st.image(imgs[0], use_container_width=True)
                if len(imgs) > 1:
                    with st.expander("📷 Photos"):
                        sub_cols = st.columns(3)
                        for j, url in enumerate(imgs[1:]):
                            sub_cols[j % 3].image(url, use_container_width=True)
            
            st.markdown(f'<p class="grid-stamp-title">{row["name"]}</p>', unsafe_allow_html=True)
            st.write(f"**${row['formatted_price']}**")
            
            with st.expander("Details"):
                st.write(f"**Cat #:** {row['item_specifics_02_catalog_number']}")
                st.write(f"**Cond:** {row['item_specifics_04_condition']}")
                st.caption(row['description'][:100] + "...")
            st.markdown('</div>', unsafe_allow_html=True)
else:
    # Tightened Row View
    for _, row in df_show.iterrows():
        with st.container():
            c1, c2 = st.columns([0.5, 3.5]) # Smaller image column
            with c1:
                imgs = str(row['image']).split('||')
                if imgs[0].startswith('http'):
                    st.image(imgs[0], width=110)
            with c2:
                st.markdown(f'<p class="row-title">{row["name"]} <span style="float:right;">${row["formatted_price"]}</span></p>', unsafe_allow_html=True)
                st.markdown(f'<p class="row-
