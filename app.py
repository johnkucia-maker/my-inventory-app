import streamlit as st
import pandas as pd
import os
from difflib import get_close_matches

# 1. Page Config
st.set_page_config(page_title="RRKLT Estate Collection", layout="wide")

# 2. Refined CSS
st.markdown("""
    <style>
    .sidebar-title {
        text-align: center !important;
        width: 100%;
        color: #64748b;
    }
    .grid-stamp-title {
        font-size: 14px !important;
        font-weight: 700;
        color: #64748b; 
        line-height: 1.3;
        margin-bottom: 4px;
        height: 2.8em;
        overflow: hidden;
    }
    .row-title, .list-header-title {
        font-size: 17px !important;
        font-weight: 700;
        color: #64748b; 
        margin: 0;
    }
    .price-text {
        font-size: 16px;
        font-weight: 800;
        color: #52b788; 
        margin-bottom: 8px;
    }
    .row-metadata, .muted-text {
        font-size: 12px;
        color: #94a3b8; 
        font-weight: 400;
        letter-spacing: 0.2px;
    }
    .stamp-card {
        border-top: 1px solid #e2e8f0;
        padding: 12px 5px;
        margin-bottom: 10px;
    }
    .estate-intro {
        color: #64748b;
        font-style: italic;
        text-align: center;
        margin-bottom: 25px;
        font-size: 15px;
        max-width: 800px;
        margin: 0 auto;
    }
    .top-button {
        background-color: #cbd5e1;
        color: #1e293b;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        border: 1px solid #94a3b8;
        font-weight: bold;
        margin-bottom: 10px;
        text-decoration: none;
        display: block;
    }
    .filter-tip {
        font-size: 11px;
        color: #94a3b8;
        margin-top: 10px;
        text-align: center;
    }
    div.stButton > button {
        width: 100%;
        padding: 8px 1px;
        font-size: 11px;
        white-space: nowrap;
        border-radius: 6px;
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
st.sidebar.markdown("<h2 class='sidebar-title'>Gallery Controls</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<a href='#top' class='top-button'>⬆️ Return to Top</a>", unsafe_allow_html=True)

if 'view_mode' not in st.session_state:
    st.session_state.view_mode = 'Grid'
if 'limit' not in st.session_state: 
    st.session_state.limit = 48

col_v1, col_v2, col_v3 = st.sidebar.columns(3)
if col_v1.button("Grid ⣿"): st.session_state.view_mode = 'Grid'
if col_v2.button("Row ☰"): st.session_state.view_mode = 'Rows'
if col_v3.button("List ☷"): st.session_state.view_mode = 'Details'

st.sidebar.markdown("---")
sort_option = st.sidebar.selectbox("Sort Price:", ["Original", "Low to High", "High to Low"])
st.sidebar.markdown("---")

def get_opts(col):
    vals = df_raw[col].unique()
    return sorted([str(x) for x in vals if str(x).strip() != ''])

# New Checkbox Stack at Top
st.sidebar.write("**Condition**")
f_cond = []
for opt in get_opts('item_specifics_04_condition'):
    if st.sidebar.checkbox(opt, key=f"cond_{opt}"):
        f_cond.append(opt)

st.sidebar.write("**Centering**")
f_cent = []
for opt in get_opts('item_specifics_08_centering'):
    if st.sidebar.checkbox(opt, key=f"cent_{opt}"):
        f_cent.append(opt)

st.sidebar.markdown("---")

# New Country Dropdown and original filters
f_country = st.sidebar.multiselect("Country", get_opts('item_specifics_01_country'))
f_type = st.sidebar.multiselect("Stamp Type", get_opts('item_specifics_03_stamp_type'))
f_form = st.sidebar.multiselect("Stamp Format", get_opts('item_specifics_05_stamp_format'))
f_has_cert = st.sidebar.selectbox("Has a Certificate?", ["All", "Yes", "No"])

if st.sidebar.button("❌ Reset All Filters"):
    st.session_state.limit = 48
    st.rerun()

st.sidebar.markdown('<p class="filter-tip">💡 Hold <b>Ctrl</b> (Win) or <b>Cmd</b> (Mac) to select multiple options in dropdowns.</p>', unsafe_allow_html=True)

# --- TOP SECTION ---
st.markdown("<div id='top'></div>", unsafe_allow_html=True)
if os.path.exists("racingstamp.png"):
    _, cent_co, _ = st.columns([1, 1, 1])
    cent_co.image("racingstamp.png", width=200)

st.markdown("<h1 style='text-align: center; color: #64748b;'>RRKLT Estate Collection</h1>", unsafe_allow_html=True)
st.markdown('<p class="estate-intro">This collection of stamps was acquired by Richard Kucia from 1940 through 2024, and passed to the Richard Kucia Trust at his death in 2025.</p>', unsafe_allow_html=True)

search = st.text_input("🔍 Search", placeholder="Fuzzy search active...")

# --- FILTERING ---
df = df_raw.copy()
if search:
    s_term = search.lower()
    df = df[df['search_blob'].apply(lambda x: s_term in x or len(get_close_matches(s_term, x.split(), n=1, cutoff=0.7)) > 0)]

if f_country: df = df[df['item_specifics_01_country'].isin(f_country)]
if f_cond: df = df[df['item_specifics_04_condition'].isin(f_cond)]
if f_cent: df = df[df['item_specifics_08_centering'].isin(f_cent)]
if f_type: df = df[df['item_specifics_03_stamp_type'].isin(f_type)]
if f_form: df = df[df['item_specifics_05_stamp_format'].isin(f_form)]

if f_has_cert == "Yes": df = df[df['item_specifics_09_has_a_certificate'].str.contains("Yes", case=False)]
elif f_has_cert == "No": df = df[~df['item_specifics_09_has_a_certificate'].str.contains("Yes", case=False)]

if sort_option == "Low to High": df = df.sort_values("buyout_price")
elif sort_option == "High to Low": df = df.sort_values("buyout_price", ascending=False)

st.info(f"Showing {len(df)} items match your selection.")
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
                        sub = st.columns(3)
                        for j, url in enumerate(imgs[1:]): sub[j % 3].image(url, use_container_width=True)
            st.markdown(f'<p class="grid-stamp-title">{row["name"]}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="price-text">${row["formatted_price"]}</p>', unsafe_allow_html=True)
            with st.expander("Details"):
                st.markdown(f'<p class="muted-text"><b>Cat #:</b> {row["item_specifics_02_catalog_number"]}<br><b>Cond:</b> {row["item_specifics_04_condition"]}</p>', unsafe_allow_html=True)
                st.caption(row['description'])
            st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.view_mode == 'Rows':
    for _, row in df_show.iterrows():
        c1, c2 = st.columns([0.6, 3.4])
        imgs = str(row['image']).split('||')
        with c1:
            if imgs[0].startswith('http'): st.image(imgs[0], width=110)
        with c2:
            st.markdown(f'<div style="display:flex; justify-content:space-between; align-items:center;"><p class="row-title">{row["name"]}</p><p class="price-text">${row["formatted_price"]}</p></div>', unsafe_allow_html=True)
            st.markdown(f'<p class="row-metadata"><b>Cat #:</b> {row["item_specifics_02_catalog_number"]} | <b>Cond:</b> {row["item_specifics_04_condition"]}</p>', unsafe_allow_html=True)
            with st.expander("📄 Details & Photos"):
                st.write(row['description'])
                if len(imgs) > 1:
                    sub = st.columns(6)
                    for j, url in enumerate(imgs[1:]): sub[j % 6].image(url, use_container_width=True)
        st.markdown('<div style="border-top:1px solid #f1f5f9; margin: 10px 0;"></div>', unsafe_allow_html=True)

else: # List View
    for i, row in df_show.iterrows():
        summary = f"{row['name'][:45]}... | ${row['formatted_price']}"
        with st.expander(summary):
            imgs = str(row['image']).split('||')
            if imgs[0].startswith('http'):
                st.image(imgs[0], width=300)
                if len(imgs) > 1:
                    sub = st.columns(4)
                    for j, url in enumerate(imgs[1:]): sub[j % 4].image(url, use_container_width=True)
            st.markdown(f"<p class='list-header-title'>{row['name']}</p>", unsafe_allow_html=True)
            st.markdown(f'<p class="price-text">${row["formatted_price"]}</p>', unsafe_allow_html=True)
            st.write(row['description'])
        st.markdown('<div style="border-top:1px solid #f1f5f9; margin: 2px 0;"></div>', unsafe_allow_html=True)

# 5. Load More Button with dynamic count
if len(df) > st.session_state.limit:
    if st.button(f"🔽 Load more items ({st.session_state.limit} of {len(df)} Items)"):
        st.session_state.limit += 48
        st.rerun()

st.write("---")
st.caption("RRKLT Estate Collection, formerly of Cranberry Township, PA.")
