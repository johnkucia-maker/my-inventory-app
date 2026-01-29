import streamlit as st
import pandas as pd
import os

# 1. Page Config
st.set_page_config(page_title="RRKLT Estate Collection", layout="wide")

# 2. Top Anchor for navigation
st.markdown("<div id='top'></div>", unsafe_allow_html=True)

# 3. Logo and Header Section
# This checks if the file exists before trying to load it to prevent errors
if os.path.exists("racingstamp.png"):
    # Using columns to center the logo
    left_co, cent_co, last_co = st.columns([1, 1, 1])
    with cent_co:
        st.image("racingstamp.png", width=300)

st.markdown("<h1 style='text-align: center;'>RRKLT Estate Collection</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: gray;'>This collection of stamps was acquired by Richard Kucia from 1940 through 2024, and passed to the Richard Kucia Trust at his death in 2025.</h4>", unsafe_allow_html=True)
st.write("---")

# 4. Cached Data Loading
@st.cache_data
def load_data():
    df = pd.read_csv("inventory.csv")
    df['buyout_price'] = pd.to_numeric(df['buyout_price'], errors='coerce')
    df = df.fillna('')
    return df

df_raw = load_data()

# --- SIDEBAR (FILTERS & NAVIGATION) ---
st.sidebar.title("🔍 Filters & Sorting")

# Return to Top Button
st.sidebar.markdown("""
    <a href='#top' style='text-decoration: none;'>
        <div style='background-color: #f0f2f6; color: #31333F; padding: 10px; border-radius: 5px; text-align: center; border: 1px solid #dcdfe4; font-weight: bold; margin-bottom: 10px;'>
            ⬆️ Return to Top
        </div>
    </a>
    """, unsafe_allow_html=True)

if st.sidebar.button("❌ Reset All Filters"):
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip:** Hold **Ctrl** (Win) or **Cmd** (Mac) to select multiple options.")

sort_option = st.sidebar.selectbox("Sort Price:", ["Original", "Low to High", "High to Low"])

def get_opts(col):
    return sorted([str(x) for x in df_raw[col].unique() if str(x).strip() != ''])

# The 5 Active Filter Categories
f_type = st.sidebar.multiselect("Stamp Type", get_opts('item_specifics_03_stamp_type'))
f_cond = st.sidebar.multiselect("Condition", get_opts('item_specifics_04_condition'))
f_cent = st.sidebar.multiselect("Centering", get_opts('item_specifics_08_centering'))
f_form = st.sidebar.multiselect("Stamp Format", get_opts('item_specifics_05_stamp_format'))
f_has_cert = st.sidebar.selectbox("Has a Certificate?", ["All", "Yes", "No"])

# --- FILTERING LOGIC ---
df = df_raw.copy()

search = st.text_input("🔍 Search Name, Catalog #, or Country", "")
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

if sort_option == "Low to High": 
    df = df.sort_values("buyout_price")
elif sort_option == "High to Low": 
    df = df.sort_values("buyout_price", ascending=False)

st.info(f"Showing {len(df)} items.")

# --- DISPLAY ---
if 'limit' not in st.session_state: 
    st.session_state.limit = 20
df_show = df.head(st.session_state.limit)

for _, row in df_show.iterrows():
    with st.container():
        c1, c2 = st.columns([1, 2])
        with c1:
            imgs = str(row['image']).split('||')
            if imgs[0].startswith('http'):
                st.image(imgs[0], use_container_width=True)
                if len(imgs) > 1:
                    with st.expander("📷 View All Images"):
                        sub_cols = st.columns(3)
                        for j, url in enumerate(imgs[1:]):
                            sub_cols[j % 3].image(url, use_container_width=True)
        with c2:
            st.subheader(row['name'])
            st.write(f"### ${row['buyout_price']} {row['currency']}")
            
            d1, d2 = st.columns(2)
            d1.write(f"**Country:** {row['item_specifics_01_country']}")
            d1.write(f"**Cat #:** {row['item_specifics_02_catalog_number']}")
            d2.write(f"**Condition:** {row['item_specifics_04_condition']}")
            d2.write(f"**Cert Grade:** {row['item_specifics_10_certificate_grade']}")
            
            with st.expander("📄 View Full Description"):
                st.write(row['description'])
        st.divider()

if len(df) > st.session_state.limit:
    if st.button("🔽 Load More Items"):
        st.session_state.limit += 20
        st.rerun()

# Bottom Blurb
st.write("---")
st.caption("RRKLT Estate Collection, formerly of Cranberry Township, PA.")
