import streamlit as st
import pandas as pd

# Load your inventory
st.set_page_config(page_title="RRKLT Inventory Mirror", layout="wide")
st.title("📦 RRKLT Private Inventory")

try:
    # This reads the file you uploaded
    df = pd.read_csv("inventory.csv")
    
    # Search bar
    search = st.text_input("Search by Title or SKU", "")
    if search:
        df = df[df['Title'].str.contains(search, case=False, na=False)]

    # Show the items in a clean list
    st.dataframe(df[['Title', 'Price', 'Condition', 'Image URL']])
    
    # Visual Gallery
    st.write("### Gallery View")
    cols = st.columns(3)
    for i, row in df.iterrows():
        with cols[i % 3]:
            if 'Image URL' in df.columns:
                st.image(row['Image URL'], use_container_width=True)
            st.subheader(row['Title'])
            st.write(f"Price: {row['Price']}")

except Exception as e:
    st.error("Wait! We need to upload your inventory.csv file to GitHub first.")