import streamlit as st
import pandas as pd

st.set_page_config(page_title="RRKLT Inventory Mirror", layout="wide")
st.title("📦 RRKLT Private Inventory")

try:
    # Load the file
    df = pd.read_csv("inventory.csv")
    
    # --- STEP 1: SHOW THE COLUMNS ---
    # This helps us see what HipStamp named your headers
    with st.expander("🛠️ Debug: See Column Names"):
        st.write("Your CSV has these columns:", df.columns.tolist())
        st.write("First 3 rows of data:", df.head(3))

    # --- STEP 2: TRY TO FIND THE RIGHT COLUMNS ---
    # We check for common names like 'Title' or 'Item Title'
    title_col = next((c for c in df.columns if 'title' in c.lower()), None)
    price_col = next((c for c in df.columns if 'price' in c.lower()), None)
    img_col = next((c for c in df.columns if 'image' in c.lower() or 'url' in c.lower()), None)

    # --- STEP 3: DISPLAY ---
    if title_col:
        search = st.text_input("Search inventory...", "")
        if search:
            df = df[df[title_col].str.contains(search, case=False, na=False)]

        st.write(f"Showing **{len(df)}** items:")
        
        # Create a grid
        cols = st.columns(3)
        for i, (idx, row) in enumerate(df.iterrows()):
            with cols[i % 3]:
                # Show image if we found a URL column
                if img_col and pd.notna(row[img_col]):
                    st.image(row[img_col], use_container_width=True)
                
                st.subheader(row[title_col])
                
                if price_col:
                    st.write(f"**Price:** {row[price_col]}")
                
                st.divider()
    else:
        st.error("We found the file, but we couldn't find a 'Title' column. Look at the 'Debug' section above to see what the headers are named.")

except Exception as e:
    st.error(f"Something went wrong while reading the file: {e}")
