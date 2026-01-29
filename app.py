import streamlit as st
import pandas as pd

st.set_page_config(page_title="RRKLT Stamp Inventory", layout="wide")

st.markdown("""
    <style>
    .stamp-card { border: 1px solid #ddd; padding: 15px; border-radius: 8px; margin-bottom: 25px; background-color: #f9f9f9; }
    .stImage { border-radius: 4px; border: 1px solid #eee; }
    </style>
    """, unsafe_allow_html=True)

st.title("✉️ RRKLT Full Inventory Mirror")
st.write("Browse your collection. All available images for each item are displayed below.")

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

    # --- MAIN GRID ---
    for i, (idx, row) in enumerate(df.iterrows()):
        # Create a container/card for each stamp
        with st.container():
            col_img, col_info = st.columns([1, 1]) # Splits the row into Image side and Info side
            
            with col_img:
                # --- MULTI-IMAGE LOGIC ---
                raw_images = str(row['image']).split('||')
                # Filter out any empty strings or 'nan'
                clean_images = [img.strip() for img in raw_images if img.strip().lower() != 'nan' and img.strip()]
                
                if clean_images:
                    # Show the first (main) image large
                    st.image(clean_images[0], use_container_width=True, caption="Main Image")
                    
                    # If there are more images, show them in a smaller row below
                    if len(clean_images) > 1:
                        st.write("Additional Views:")
                        sub_cols = st.columns(min(len(clean_images)-1, 4)) # Up to 4 small images wide
                        for sub_idx, extra_img in enumerate(clean_images[1:]):
                            with sub_cols[sub_idx % 4]:
                                st.image(extra_img, use_container_width=True)
                else:
                    st.warning("🖼️ No Images Available")
            
            with col_info:
                st.subheader(row['name'])
                st.write(f"💰 **Price:** {row['currency']} ${row['buyout_price']}")
                
                # Create a tidy table for the specs
                details = {
                    "Catalog #": row['item_specifics_02_catalog_number'],
                    "Condition": row['item_specifics_04_condition'],
                    "Country": row['item_specifics_01_country'],
                    "Type": row['item_specifics_03_stamp_type']
                }
                st.table(pd.DataFrame([details]).T.rename(columns={0: 'Details'}))
                
                with st.expander("📄 View Full Description"):
                    st.write(row['description'])
            
            st.divider()

except Exception as e:
    st.error(f"Error loading inventory: {e}")
