import streamlit as st
import pandas as pd

# 1. Page Config
st.set_page_config(page_title="RRKLT Master Catalog", layout="wide")

# 2. Cached Data Loading (Speeds up the app significantly)
@st.cache_data
def load_data():
    df = pd.read_csv("inventory.csv")
    df['buyout_price'] = pd.to_numeric(df['buyout_price'], errors='coerce')
    df = df.fillna('')
    return df

df_raw = load_data()

# --- SIDEBAR (FILTERS & NAVIGATION) ---
st.sidebar.title("🔍 Filters & Sorting")

# Action Buttons at the top of Sidebar
if st.sidebar.button("❌ Reset All Filters"):
    st.rerun()

st.sidebar.markdown("---")

# 1. Sort Option
sort_option = st.sidebar.selectbox("Sort Price:", ["Original", "Low to High", "High to Low"])

# Helper function to get clean filter lists
def get_opts(col):
    return sorted([str(x) for x in df_raw[col].unique() if str(x).strip() != ''])

# 2-8. The 7 Required Filter Categories
f_cat = st.sidebar.multiselect("Categories", get_opts('category_id'))
f_type = st.sidebar.multiselect("Stamp Type", get_opts('item_specifics_03_stamp_type'))
f_cond = st.sidebar.multiselect("Condition", get_opts('item_specifics_04_condition'))
f_cent = st.sidebar.multiselect("Centering", get_opts('item_specifics_08_centering'))
f_form = st.sidebar.multiselect("Stamp Format", get_opts('item_specifics_05_stamp_format'))
f_has_cert = st.sidebar.selectbox("Has a Certificate?", ["All", "Yes", "No"])
f_grade = st.sidebar.multiselect("Certificate Grade", get_opts('item_specifics_10_certificate_grade'))

st.sidebar.markdown("---")

# The requested "Return to Top" button in the menu
if st.sidebar.button("⬆️ Return to Top"):
    st.rerun()

# --- FILTERING LOGIC ---
df = df_raw.copy()

# Text Search (Top of Page)
search = st.text_input("🔍 Search Name, Catalog #, or Country", "")
if search:
    s = search.lower()
    df = df[df['name'].str.lower().str.contains(s) | 
            df['item_specifics_02_catalog_number'].str.lower().str.contains(s) |
            df['item_specifics_01_country'].str.lower().str.contains(s)]

# Applying the Multiselect Filters
if f_cat: df = df[df['category_id'].astype(str).isin(f_cat)]
if f_type: df = df[df['item_specifics_03_stamp_type'].isin(f_type)]
if f_cond: df = df[df['item_specifics_04_condition'].isin(f_cond)]
if f_cent: df = df[df['item_specifics_08_centering'].isin(f_cent)]
if f_form: df = df[df['item_specifics_05_stamp_format'].isin(f_form)]
if f_grade: df = df[df['item_specifics_10_certificate_grade'].isin(f_grade)]

# Certificate Toggle
if f_has_cert == "Yes": 
    df = df[df['item_specifics_09_has_a_certificate'].str.contains("Yes", case=False)]
elif f_has_cert == "No": 
    df = df[~df['item_specifics_09_has_a_certificate'].str.contains("Yes", case=False)]

# Sorting
if sort_option == "Low to High": 
    df = df.sort_values("buyout_price")
elif sort_option == "High to Low": 
    df = df.sort_values("buyout_price", ascending=False)

# --- DISPLAY ---
st.title("✉️ RRKLT Private Catalog")
st.info(f"Showing {len(df)} items match your criteria.")

# Pagination (Prevents browser lag)
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
            
            # Key Details Grid
            d1, d2 = st.columns(2)
            d1.write(f"**Country:** {row['item_specifics_01_country']}")
            d1.write(f"**Cat #:** {row['item_specifics_02_catalog_number']}")
            d2.write(f"**Condition:** {row['item_specifics_04_condition']}")
            d2.write(f"**Grade:** {row['item_specifics_10_certificate_grade']}")
            
            with st.expander("📄 View Full Description"):
                st.write(row['description'])
        st.divider()

# Load More Button
if len(df) > st.session_state.limit:
    if st.button("🔽 Load More Items"):
        st.session_state.limit += 20
        st.rerun()
