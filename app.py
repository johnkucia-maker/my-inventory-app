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

# 3. Dynamic Theme CSS
if st.session_state.dark_mode:
    # DARK MODE COLORS
    bg_color = "#0f172a"
    sidebar_bg = "#1e293b"
    card_border = "#334155"
    title_color = "#cbd5e1"
    muted_color = "#94a3b8"
    price_color = "#52b788"  # Brighter mint for dark bg
    text_color = "#e2e8f0"
else:
    # LIGHT MODE COLORS
    bg_color = "#ffffff"
    sidebar_bg = "#f8fafc"
    card_border = "#e2e8f0"
    title_color = "#64748b"
    muted_color = "#94a3b8"
    price_color = "#2d6a4f"  # Deeper forest for light bg
    text_color = "#1e293b"

st.markdown(f"""
    <style>
    /* Global Background */
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}
    
    /* Centered Sidebar Title */
    .sidebar-title {{
        text-align: center !important;
        width: 100%;
        color: {title_color};
    }}
    
    /* Typography Hierarchy */
    .grid-stamp-title, .row-title, .list-title {{
        font-size: 14px !important;
        font-weight: 700;
        color: {title_color};
        line-height: 1.3;
    }}
    .row-title {{ font-size: 17px !important; }}
    
    .price-text {{
        font-size: 16px;
        font-weight: 800;
        color: {price_color};
        margin-bottom: 8px;
    }}
    
    .row-metadata, .muted-text, .stCaption {{
        font-size: 12px;
        color: {muted_color} !important;
        font-weight: 400;
    }}
    
    /* Card/Divider Styles */
    .stamp-card, .stExpander {{
        border-top: 1px solid {card_border} !important;
        background-color: transparent;
    }}
    
    /* Sidebar Specifics */
    [data-testid="stSidebar"] {{
        background-color: {sidebar_bg};
    }}

    .top-button {{
        background-color: {muted_color};
        color: white;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        margin-bottom: 10px;
        text-decoration: none;
        display: block;
    }}
    
    .filter-tip {{
        font-size: 11px;
        color: {muted_color};
        margin-top: 10px;
        text-align: center;
    }}

    div.stButton > button {{
        width: 100%;
        padding: 8px 1px;
        font-size: 11px;
        white-space: nowrap;
        border-radius: 6px;
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
st.sidebar.markdown("<h2 class='sidebar-title'>Gallery Controls</h2>", unsafe_allow_html=True)
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

f_type = st.sidebar.multiselect("Stamp Type", get_opts('item_specifics_03_stamp_type'))
f_cond = st.sidebar.multiselect("Condition", get_opts('item_specifics_04_condition'))
f_cent = st.sidebar.multiselect("Centering", get_opts('item_specifics_08_centering'))
f_form = st.sidebar.multiselect("Stamp Format", get_opts('item_specifics_05_stamp_format'))
f_has_cert = st.sidebar.selectbox("Has a Certificate?", ["All", "Yes", "No"])

st.sidebar.markdown('<p class="filter-tip">💡 Hold <b>Ctrl</b> (Win) or <b>Cmd</b> (Mac) to select multiple options.</p>', unsafe_allow_html=True)

st.sidebar.markdown("---")
# Dark Mode Toggle at bottom of sidebar
if st.sidebar.button("🌓 Toggle Dark/Light Mode"):
    st.session_state.dark_mode = not st.session_state.dark_mode
    st.rerun()

# --- TOP SECTION ---
st.markdown("<div id='top'></div>", unsafe_allow_html=True)

if os.path.exists("racingstamp.png"):
    _, cent_co, _ = st.columns([1, 1, 1])
    cent_co.image("racingstamp.png", width=200)

st.markdown(f"<h1 style='text-align: center; color: {title_color};'>RRKLT Estate Collection</h1>", unsafe_allow_html=True)
st.markdown(f'<p class="estate-intro" style="text-align:center; font-style:italic; color:{muted_color};">This collection of stamps was acquired by Richard Kucia from 1940 through 2024, and passed to the Richard Kucia Trust at his death in 2025.</p>', unsafe_allow_html=True)

search = st.text_input("🔍 Search", placeholder="Fuzzy search active...")

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
                        for j, url in enumerate(imgs[1:]):
                            sub[j % 3].image(url, use_container_width=True)
            st.markdown(f'<p class="grid-stamp-title">{row["name"]}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="price-text">${row["formatted_price"]}</p>', unsafe_allow_html=True)
            with st.expander("Details"):
                st.markdown(f'<p class="muted-text"><b>Cat #:</b> {row["item_specifics_02_catalog_number"]}<br><b>Cond:</b> {row["item_specifics_04_condition"]}</p>', unsafe_allow_html=True)
                st.caption(row['description'][:100] + "...")
            st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.view_mode == 'Rows':
    for _, row in df_show.iterrows():
        with st.container():
            c1, c2 = st.columns([0.6, 3.4])
            with c1:
                imgs = str(row['image']).split('||')
                if imgs[0].startswith('http'):
                    st.image(imgs[0], width=110)
            with c2:
                st.markdown(f'<div style="display:flex; justify-content:space-between; align-items:center;"><p class="row-title">{row["name"]}</p><p class="price-text">${row["formatted_price"]}</p></div>', unsafe_allow_html=True)
                st.markdown(f'<p class="row-metadata"><b>Country:</b> {row["item_specifics_01_country"]} | <b>Cat #:</b> {row["item_specifics_02_catalog_number"]} | <b>Condition:</b> {row["item_specifics_04_condition"]}</p>', unsafe_allow_html=True)
                with st.expander("📄 Details & Photos"):
                    st.write(row['description'])
                    if len(imgs) > 1:
                        sub = st.columns(6)
                        for j, url in enumerate(imgs[1:]):
                            sub[j % 6].image(url, use_container_width=True)
            st.markdown(f'<div style="border-top:1px solid {card_border}; margin: 10px 0;"></div>', unsafe_allow_html=True)

else: # List View
    for i, row in df_show.iterrows():
        line_text = f"**{row['name'][:40]}...** | ${row['formatted_price']}"
        with st.expander(line_text):
            imgs = str(row['image']).split('||')
            if imgs[0].startswith('http'):
                st.image(imgs[0], width=300)
            st.markdown(f"<h3 style='color: {title_color};'>{row['name']}</h3>", unsafe_allow_html=True)
            st.markdown(f'<p class="price-text">${row["formatted_price"]}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="muted-text"><b>Country:</b> {row["item_specifics_01_country"]} | <b>Cat #:</b> {row["item_specifics_02_catalog_number"]} | <b>Condition:</b> {row["item_specifics_04_condition"]}</p>', unsafe_allow_html=True)
            st.write(row['description'])
            if len(imgs) > 1:
                st.markdown("---")
                sub_d = st.columns(4)
                for j, url in enumerate(imgs[1:]):
                    sub_d[j % 4].image(url, use_container_width=True)
        st.markdown(f'<div style="border-top:1px solid {card_border}; margin: 2px 0;"></div>', unsafe_allow_html=True)

# Infinite Scroll
if len(df) > st.session_state.limit:
    remaining = len(df) - st.session_state.limit
    if st.button(f"🔽 Load more items ({remaining} left)"):
        st.session_state.limit += 48
        st.rerun()

st.write("---")
st.caption("RRKLT Estate Collection, formerly of Cranberry Township, PA.")
