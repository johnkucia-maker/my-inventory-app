import streamlit as st
import pandas as pd
import os

# 1. Page Config
st.set_page_config(page_title="RRKLT Estate Collection", layout="wide")

# 2. Advanced CSS: Sticky Header, Skeleton-style cards, and Grid Styling
st.markdown("""
    <style>
    /* Sticky Header Logic */
    .sticky-header {
        position: -webkit-sticky;
        position: sticky;
        top: 0;
        background-color: white;
        z-index: 1000;
        padding: 10px 0;
        border-bottom: 2px solid #f0f2f6;
    }
    /* Card Styling */
    .stamp-card {
        border: 1px solid #e6e9ef;
        border-radius: 10px;
        padding: 15px;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        height: 100%;
        transition: transform 0.2s;
    }
    .stamp-card:hover {
        transform: translateY(-5px);
        border-color: #d1d5db;
    }
    /* Hide Streamlit elements for cleaner look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 3. Cached Data Loading
@st.cache_data
def load_data():
    df = pd.read_csv("inventory.csv")
    df['buyout_price'] = pd.to_numeric(df['buyout_price'], errors='coerce')
    df = df.fillna('')
    return df

df_raw = load_data()

# --- SIDEBAR (FILTERS & VIEW TOGGLE) ---
st.sidebar.title("🔍 Gallery Controls")

# Return to Top Link
st.sidebar.markdown("<a href='#top' style='text-decoration:none;'><div style='background-color:#f0f2f6;padding:10px;border-radius:5px;text-align:center;border:1px solid #dcdfe4;font-weight:bold;margin-bottom:10px;'>⬆️ Return to Top</div></a>", unsafe_allow_html=True)

# VIEW TOGGLE (Buttons in Sidebar)
st.sidebar.subheader("🖼️ Display View")
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = 'Grid'

col_v1, col_v2 = st.sidebar.columns(2)
if col_v1.button("Grid"):
    st.session_state.view_mode = 'Grid'
if col_v2.button("Rows"):
    st.session_state.view_mode = 'Rows'

st.sidebar.markdown("---")

# Sort Option
sort_option = st.sidebar.selectbox("Sort Price:", ["Original", "Low to High", "High to Low"])

st.sidebar.markdown("---")
if st.sidebar.button("❌ Reset All Filters"):
    st.rerun()

# 5 Filters
def get_opts(col):
    return sorted([str(x) for x in df_raw[col].unique() if str(x).strip() != ''])

f_type = st.sidebar.multiselect("Stamp Type", get_opts('item_specifics_03_stamp_type'))
f_cond = st.sidebar.multiselect("Condition", get_opts('item_specifics_04_condition'))
f_cent = st.sidebar.multiselect("Centering", get_opts('item_specifics_08_centering'))
f_form = st.sidebar.multiselect("Stamp Format", get_opts('item_specifics_05_stamp_format'))
f_has_cert = st.sidebar.selectbox("Has a Certificate?", ["All", "Yes", "No"])

# --- HEADER SECTION (STICKY) ---
st.markdown("<div id='top'></div>", unsafe_allow_html=True)

# Sticky Container for Search and Stats
with st.container():
    st.markdown('<div class="sticky-header">', unsafe_allow_html=True)
    
    if os.path.exists("racingstamp.png"):
        st.image("racingstamp.png", width=150)
    
    st.title("RRKLT Estate Collection")
    
    # Global Search
    search = st.text_input("🔍 Search Name, Catalog #, or Country", key="main_search", placeholder="Type to filter...")
    st.markdown('</div>', unsafe_allow_html=True)

# Intro Text
st.markdown("#### *This collection of stamps was acquired by Richard Kucia from 1940 through 2024, and passed to the Richard Kucia Trust at his death in 2025.*")

# --- FILTERING LOGIC ---
df = df_raw.copy()

if search:
    s = search.lower()
    df = df[df['name'].str.lower().str.contains(s) | 
            df['item_specifics_02_catalog_number'].str.lower().str.contains(s) |
            df['item_specifics_01_country'].str.lower().str.contains(s)]

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

st.caption(f"Showing {len(df)} items in {st.session_state.view_mode} mode.")

# Pagination
if 'limit' not in st.session_state: st.session_state.limit = 24
df_show = df.head(st.session_state.limit)

# --- DISPLAY LOGIC (GRID VS ROW) ---

if st.session_state.view_mode == 'Grid':
    # Grid View: 3 columns
    cols = st.columns(3)
    for i, (_, row) in enumerate(df_show.iterrows()):
        with cols[i % 3]:
            st.markdown('<div class="stamp-card">', unsafe_allow_html=True)
            imgs = str(row['image']).split('||')
            if imgs[0].startswith('http'):
                st.image(imgs[0], use_container_width=True)
            
            st.subheader(row['name'][:50] + "..." if len(row['name']) > 50 else row['name'])
            st.write(f"**Price:** ${row['buyout_price']}")
            st.write(f"**Cat #:** {row['item_specifics_02_catalog_number']}")
            
            with st.expander("View Details"):
                st.write(f"**Cond:** {row['item_specifics_04_condition']}")
                st.write(f"**Centering:** {row['item_specifics_08_centering']}")
                st.write(row['description'])
            st.markdown('</div>', unsafe_allow_html=True)
            st.write("") # Spacer

else:
    # Row View (Original Style)
    for _, row in df_show.iterrows():
        with st.container():
            c1, c2 = st.columns([1, 2])
            with c1:
                imgs = str(row['image']).split('||')
                if imgs[0].startswith('http'):
                    st.image(imgs[0], use_container_width=True)
            with c2:
                st.subheader(row['name'])
                st.write(f"### ${row['buyout_price']}")
                st.write(f"**Country:** {row['item_specifics_01_country']} | **Cat #:** {row['item_specifics_02_catalog_number']}")
                with st.expander("📄 Full Description"):
                    st.write(row['description'])
            st.divider()

# Load More
if len(df) > st.session_state.limit:
    if st.button("🔽 Load More Items"):
        st.session_state.limit += 24
        st.rerun()

st.write("---")
st.caption("RRKLT Estate Collection, formerly of Cranberry Township, PA.")
