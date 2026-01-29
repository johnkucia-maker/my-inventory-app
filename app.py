import streamlit as st
import pandas as pd

st.set_page_config(page_title="RRKLT Stamp Inventory", layout="wide")

st.markdown("""
    <style>
    .stamp-card { border: 1px solid #ddd; padding: 10px; border-radius: 5px; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("✉️ RRKLT Private Inventory Mirror")

try:
    df = pd.read_csv("inventory.csv")

    search = st.text_input("Search by Name, Catalog Number, or Country", "")
    
    if search:
        mask = (
            df['name'].astype(str).str.contains(search, case=False, na=False) | 
            df['item_specifics_02_catalog_number'].astype(str).str.contains(search, case=False, na=False) |
            df['item_specifics_01_country'].astype(str).str.contains(search, case=False, na=False)
        )
        df = df[mask]

    st.info(f"Showing {len(df)} items")

    cols = st.columns(3)
    for i, (idx, row) in enumerate(df.iterrows()):
        with cols[i % 3]:
            # --- UPDATED IMAGE LOGIC ---
            img_url = str(row['image']).strip()
            
            # 1. If the image exists and starts with http, show it
            if img_url and img_url.lower() != 'nan' and img_url.startswith('http'):
                st.image(img_url, use_container_width=True)
            # 2. If it exists but is a partial link, try to fix it
            elif img_url and img_url.lower() != 'nan' and img_url.startswith('/'):
                st.image(f"https://www.hipstamp.com{img_url}", use_container_width=True)
            # 3. Otherwise, show a placeholder
            else:
                st.warning("🖼️ No Image Provided in CSV")
            
            st.subheader(row['name'])
            st.write(f"**Price:** {row['currency']} ${row['buyout_price']}")
            st.write(f"**Catalog #:** {row['item_specifics_02_catalog_number']}")
            st.write(f"**Condition:** {row['item_specifics_04_condition']}")
            
            with st.expander("View Full Description"):
                st.write(row['description'])
            
            st.divider()

except Exception as e:
    st.error(f"Error loading inventory: {e}")
