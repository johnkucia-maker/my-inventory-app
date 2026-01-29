import streamlit as st
import pandas as pd
import os

st.title("📦 RRKLT Inventory Mirror")

# --- DEBUG SECTION ---
# This part tells us what the app actually sees in the folder
st.write("### 📂 Files found in your folder:")
files = os.listdir('.')
st.write(files)

target_file = "inventory.csv"

if target_file in files:
    st.success(f"Found {target_file}! Loading now...")
    try:
        df = pd.read_csv(target_file)
        st.write("### Gallery View")
        cols = st.columns(3)
        for i, row in df.iterrows():
            with cols[i % 3]:
                # We use .get() to avoid errors if the column name is slightly different
                img = row.get('Image URL') or row.get('image_url')
                title = row.get('Title') or row.get('title')
                price = row.get('Price') or row.get('price')
                
                if img:
                    st.image(img, use_container_width=True)
                st.subheader(title)
                st.write(f"Price: {price}")
    except Exception as e:
        st.error(f"Error reading the file: {e}")
else:
    st.error(f"Looking for '{target_file}' but could not find it.")
    st.info("Check if your file is named exactly 'inventory.csv' (all lowercase).")
