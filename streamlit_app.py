import streamlit as st
import re
import requests
from bs4 import BeautifulSoup
import time

def validate_address(address):
    """Validate address format and return cleaned version"""
    # Convert to lowercase for consistency
    address = address.lower().strip()
    
    # Check if address matches pattern: number + street name + abbreviated type
    pattern = r'^\d+\s+[a-zA-Z]+\s+(?:ave|st|rd|dr|ln|ct|pl|blvd|cir)$'
    if not re.match(pattern, address):
        return None
    
    return address

def search_property(address):
    """Search property and return results"""
    # Initial search URL
    search_url = "https://taxrecords-nj.com/pub/cgi/prc6.cgi"
    
    # Form data for the search
    data = {
        'ms_user': 'ctb09',
        'passwd': '',
        'district': '0906',
        'adv': '1',
        'out_type': '0',
        'srch_type': '1',
        'database': 'Current Owners/Assmt List',
        'county': 'HUDSON',
        'district': 'JERSEY CITY',
        'location': address.upper(),
        'items_page': '50'
    }
    
    try:
        # Make the search request
        with st.spinner("Searching property records..."):
            response = requests.post(search_url, data=data)
            response.raise_for_status()
            
            # Parse the results page
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for the "More Info" link
            more_info_link = soup.find('a', text='More Info')
            if more_info_link:
                detail_url = more_info_link.get('href')
                if not detail_url.startswith('http'):
                    detail_url = 'https://taxrecords-nj.com/pub/cgi/' + detail_url
                    
                # Get the details page
                detail_response = requests.get(detail_url)
                detail_response.raise_for_status()
                return detail_url
            else:
                return None
                
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

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
    Example: "192 olean ave" or "413 summit ave"
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
            # Perform the actual search
            result_url = search_property(clean_address)
            
            if result_url:
                st.success("Property found! Click below to view details:")
                st.markdown(f"[View Property Details]({result_url})", unsafe_allow_html=True)
            else:
                st.error("Property not found or an error occurred. Please check the address and try again.")

# Add footer
st.markdown("---")
st.markdown("Made with Streamlit ❤️")
