import streamlit as st
import re
import requests

def validate_address(address):
    """Validate address format and return cleaned version"""
    # Convert to lowercase for consistency
    address = address.lower().strip()
    
    # Check if address matches pattern: number + street name + abbreviated type
    pattern = r'^\d+\s+[a-zA-Z]+\s+(?:ave|st|rd|dr|ln|ct|pl|blvd|cir)$'
    if not re.match(pattern, address):
        return None
    
    return address

# Set page config
st.set_page_config(
    page_title="Jersey City Property Lookup",
    page_icon="🏠",
    layout="centered"
)

# Add custom CSS
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
    }
    .stTextInput>div>div>input {
        font-size: 16px;
    }
    </style>
    """, unsafe_allow_html=True)

# Main app
st.title("Jersey City Property Lookup 🏠")

st.markdown("""
    ### Enter Property Address
    Format: number + street name + abbreviated type  
    Example: "192 olean ave" or "1278 clifton pl"
""")

# Create input for address
address = st.text_input("Property Address:", key="address_input")

# Add search button
if st.button("Find Property Details"):
    if not address:
        st.error("Please enter an address")
    else:
        # Validate address format
        clean_address = validate_address(address)
        if not clean_address:
            st.error("Please enter address in correct format: number + street name + abbreviated type (ave, st, rd, etc.)")
        else:
            # Show success message for now (we'll add actual functionality later)
            st.success(f"Valid address format: {clean_address}")
            
            # Create expandable section to show what would happen next
            with st.expander("Search Process (Demo)"):
                st.write("1. ✅ Address validated")
                st.write("2. 🔍 Would search on: https://taxrecords-nj.com/")
                st.write("3. 📋 Would fill form with:")
                st.code(f"""
                Database: Current Owners/Assmt List
                County: HUDSON
                District: JERSEY CITY
                Address: {clean_address.upper()}
                """)

# Add footer
st.markdown("---")
st.markdown("Made with Streamlit ❤️")
