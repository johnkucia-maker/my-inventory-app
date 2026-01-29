import streamlit as st
import pandas as pd

st.set_page_config(page_title="RRKLT Inventory Mirror", layout="wide")

# Custom CSS for a professional look
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    [data-testid="stMetricValue"] { font-size: 1.2rem; }
    .stButton button { width: 100%; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv("inventory.csv")
    # Convert prices to numeric so they sort correctly
    df['buyout_price'] = pd.to_numeric(df['buyout_price'], errors='coerce')
    return df

try:
    df_raw = load_data()
    
    # --- SIDEBAR FILTERS ---
    st.sidebar.title("🔍 Filters & Sorting")
    
    if st.sidebar.button("🔄 Reset All (Clear Search)"):
        st.rerun()

    # Sorting
    sort_option = st.sidebar.selectbox("Sort by Price:", ["Original", "Price: Low to High", "Price: High to Low"])
    
    # Filter Categories (cleaning out empty values)
    def get_options(col):
        return sorted([str(x) for x in df_raw[col].unique() if pd.notna(x)])

    f_country = st.sidebar.multiselect("Country", get_options('item_specifics_01_country'))
    f_type = st.sidebar.multiselect("Stamp Type", get_options('item_specifics_03_stamp_type'))
    f_cond = st.sidebar.multiselect("Condition", get_options('item_specifics_04_condition'))
    f_center = st.sidebar.multiselect("Centering", get_options('item_specifics_08_centering'))
    f_format = st.sidebar.multiselect("Stamp Format", get_options('item_specifics_05_stamp_format'))
    f_cert = st.sidebar.selectbox("Has Certificate?", ["All", "Yes", "No"])
    
    st.sidebar.markdown("---")
    if st.sidebar.button("⬆️ Scroll to Top"):
        st.rerun()

    # --- FILTERING LOGIC ---
    df = df_raw.copy()
    
    # Text Search
    search = st.text_input("Search Name or Catalog #", key="search_bar")
    if search:
        df = df[df['name'].astype(str).str.contains(search, case=False, na=False) | 
                df['item_specifics_02_catalog_number'].astype(str).str.contains(search, case=False, na=False)]

    # Apply Multiselect Filters
    if f_country: df = df[df['item_specifics_01_country'].isin(f_country)]
    if f_type: df = df[df['item_specifics_03_stamp_type'].isin(f_type)]
    if f_cond: df = df[df['item_specifics_04_condition'].isin(f_cond)]
    if f_center: df = df[df['item_specifics_08_centering'].isin(f_center)]
    if f_format: df = df[df['item_specifics_05_stamp_format'].isin(f_format)]
    
    if f_cert == "Yes": df = df[df['item_specifics_09_has_a_certificate'].str.contains("Yes", case=False, na=False)]
    elif f_cert == "No": df = df[~df['item_specifics_09_has_a_certificate'].str.contains("Yes", case=False, na=False)]

    # Apply Sorting
    if sort_option == "Price: Low to High":
        df = df.sort_values("buyout_price", ascending=True)
    elif sort_option == "Price: High to Low":
        df = df.sort_values("buyout_price", ascending=False)

    # --- DISPLAY ---
    st.title("✉️ RRKLT Private Catalog")
    st.metric("Total Items Found", len(df))

    for i, (idx, row) in enumerate(df.iterrows()):
        with st.container():
            col_img, col_info = st.columns([1, 1.5])
            
            with col_img:
                raw_images = str(row['image']).split('||')
                clean_images = [img.strip() for img in raw_images if img.strip().lower() != 'nan' and img.strip()]
                if clean_images:
                    st.image(clean_images[0], use_container_width=True)
                    if len(clean_images) > 1:
                        with st.expander("📷 View More Images"):
                            cols = st.columns(3)
                            for sub_idx, img in enumerate(clean_images[1:]):
                                cols[sub_idx % 3].image(img, use_container_width=True)
                else:
                    st.info("No Image Available")
            
            with col_info:
                st.subheader(row['name'])
                st.write(f"### ${row['buyout_price']} {row['currency']}")
                
                # Metadata Grid
                m1, m2 = st.columns(2)
                m1.write(f"**Country:** {row['item_specifics_01_country']}")
                m1.write(f"**Cat #:** {row['item_specifics_02_catalog_number']}")
                m2.write(f"**Condition:** {row['item_specifics_04_condition']}")
                m2.write(f"**Centering:** {row['item_specifics_08_centering']}")
                
                with st.expander("📄 Full Description & Certificate Details"):
                    st.write(f"**Certificate Grade:** {row.get('item_specifics_10_certificate_grade', 'N/A')}")
                    st.write("---")
                    st.write(row['description'])
            
            st.divider()

except Exception as e:
    st.error(f"Error: {e}")
