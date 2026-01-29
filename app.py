import streamlit as st
import pandas as pd

# 1. Performance: Set page config and enable wide mode early
st.set_page_config(page_title="RRKLT High-Speed Mirror", layout="wide")

# 2. Performance: Cache the data so it stays in RAM
@st.cache_data
def load_and_clean_data():
    # Reading CSV once and storing it
    df = pd.read_csv("inventory.csv")
    df['buyout_price'] = pd.to_numeric(df['buyout_price'], errors='coerce')
    # Pre-filling empty strings to avoid errors during search
    df = df.fillna('') 
    return df

try:
    df_raw = load_and_clean_data()
    
    # --- SIDEBAR (FAST FILTERS) ---
    st.sidebar.title("🔍 Quick Filters")
    
    if st.sidebar.button("🔄 Reset / Clear All"):
        st.rerun()

    sort_option = st.sidebar.selectbox("Sort by:", ["Original", "Price: Low to High", "Price: High to Low"])

    # Pre-calculating filter options for speed
    def get_options(col):
        return sorted([str(x) for x in df_raw[col].unique() if x != ''])

    f_country = st.sidebar.multiselect("Country", get_options('item_specifics_01_country'))
    f_cond = st.sidebar.multiselect("Condition", get_options('item_specifics_04_condition'))
    f_cert = st.sidebar.selectbox("Certificate?", ["All", "Yes", "No"])

    # --- HIGH-SPEED FILTERING ---
    df = df_raw.copy()

    # Search (Optimized)
    search = st.text_input("Search Name or Catalog #")
    if search:
        # We only search the columns we care about to save processing power
        search = search.lower()
        df = df[
            df['name'].str.lower().str.contains(search) | 
            df['item_specifics_02_catalog_number'].str.lower().str.contains(search)
        ]

    # Apply Sidebar Filters
    if f_country: df = df[df['item_specifics_01_country'].isin(f_country)]
    if f_cond: df = df[df['item_specifics_04_condition'].isin(f_cond)]
    if f_cert == "Yes": df = df[df['item_specifics_09_has_a_certificate'].str.contains("Yes", case=False)]
    elif f_cert == "No": df = df[~df['item_specifics_09_has_a_certificate'].str.contains("Yes", case=False)]

    if sort_option == "Price: Low to High":
        df = df.sort_values("buyout_price")
    elif sort_option == "Price: High to Low":
        df = df.sort_values("buyout_price", ascending=False)

    # --- DISPLAY (PAGINATION) ---
    # To prevent the browser from crashing with 1000 images, 
    # we show the first 20 and let the user click "Load More"
    items_per_page = 20
    if 'page_size' not in st.session_state:
        st.session_state.page_size = items_per_page

    st.title(f"✉️ RRKLT Catalog ({len(df)} items)")

    # Only show the slice of data for the current page size
    df_visible = df.head(st.session_state.page_size)

    for idx, row in df_visible.iterrows():
        with st.container():
            c1, c2 = st.columns([1, 2])
            with c1:
                # Optimized image loading
                img_list = str(row['image']).split('||')
                if img_list[0].startswith('http'):
                    st.image(img_list[0], use_container_width=True)
            with c2:
                st.subheader(row['name'])
                st.write(f"**Price:** ${row['buyout_price']} | **Cat #:** {row['item_specifics_02_catalog_number']}")
                with st.expander("Details"):
                    st.write(row['description'])
            st.divider()

    # "Load More" button at the bottom
    if len(df) > st.session_state.page_size:
        if st.button("🔽 Load More Items"):
            st.session_state.page_size += 20
            st.rerun()

except Exception as e:
    st.error(f"Error: {e}")
