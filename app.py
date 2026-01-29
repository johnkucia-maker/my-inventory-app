import streamlit as st
import pandas as pd

# 1. Page Config
st.set_page_config(page_title="RRKLT Master Catalog", layout="wide")

# 2. Styling: Floating Arrow & Card UI
st.markdown("""
    <style>
    .stamp-card { border: 1px solid #ddd; padding: 15px; border-radius: 8px; background-color: white; margin-bottom: 20px; }
    #scrollBtn {
        display: none; position: fixed; bottom: 30px; left: 50%; transform: translateX(-50%);
        z-index: 99; border: none; outline: none; background-color: #333; color: white;
        cursor: pointer; padding: 15px; border-radius: 50%; font-size: 20px; opacity: 0.7; transition: 0.3s;
    }
    #scrollBtn:hover { opacity: 1; background-color: #000; }
    </style>
    <button onclick="topFunction()" id="scrollBtn" title="Go to top">▲</button>
    <script>
    const mybutton = window.parent.document.getElementById("scrollBtn");
    const scrollContainer = window.parent.document.querySelector(".main");
    scrollContainer.onscroll = function() {
        if (scrollContainer.scrollTop > 300) { mybutton.style.display = "block"; } 
        else { mybutton.style.display = "none"; }
    };
    function topFunction() { scrollContainer.scrollTo({top: 0, behavior: 'smooth'}); }
    </script>
    """, unsafe_allow_html=True)

# 3. Cached Data Loading
@st.cache_data
def load_data():
    df = pd.read_csv("inventory.csv")
    df['buyout_price'] = pd.to_numeric(df['buyout_price'], errors='coerce')
    df = df.fillna('')
    return df

try:
    df_raw = load_data()
    
    # --- SIDEBAR (ALL 7 CATEGORIES) ---
    st.sidebar.title("🔍 Filters & Sorting")
    
    if st.sidebar.button("❌ Clear All & Reset"):
        st.rerun()

    st.sidebar.markdown("---")
    sort_option = st.sidebar.selectbox("Sort Price:", ["Original", "Low to High", "High to Low"])

    def get_opts(col):
        return sorted([str(x) for x in df_raw[col].unique() if str(x).strip() != ''])

    # The 7 requested categories
    f_cat = st.sidebar.multiselect("Categories", get_opts('category_id'))
    f_type = st.sidebar.multiselect("Stamp Type", get_opts('item_specifics_03_stamp_type'))
    f_cond = st.sidebar.multiselect("Condition", get_opts('item_specifics_04_condition'))
    f_cent = st.sidebar.multiselect("Centering", get_opts('item_specifics_08_centering'))
    f_form = st.sidebar.multiselect("Stamp Format", get_opts('item_specifics_05_stamp_format'))
    f_has_cert = st.sidebar.selectbox("Has a Certificate?", ["All", "Yes", "No"])
    f_grade = st.sidebar.multiselect("Certificate Grade", get_opts('item_specifics_10_certificate_grade'))

    # --- FILTER LOGIC ---
    df = df_raw.copy()
    
    search = st.text_input("🔍 Search Name, Catalog #, or Country", "")
    if search:
        s = search.lower()
        df = df[df['name'].str.lower().str.contains(s) | 
                df['item_specifics_02_catalog_number'].str.lower().str.contains(s) |
                df['item_specifics_01_country'].str.lower().str.contains(s)]

    # Applying the 7 filters (Fixed the syntax
