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
    try:
        # Initialize session to maintain cookies
        session = requests.Session()
        
        # Set headers to mimic browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://taxrecords-nj.com',
            'Referer': 'https://taxrecords-nj.com/'
        }

        # Initial form data
        form_data = {
            'ms_user': 'ctb09',
            'passwd': '',
            'district': '0906',
            'adv': '1',
            'out_type': '0',
            'srch_type': '1',
            'database': '0',
            'county': '09',
            'items_page': '50',
            'location': address.upper()
        }

        # Make the search request
        with st.spinner("Searching property records..."):
            # First, get the search page
            base_url = "https://taxrecords-nj.com/pub/cgi/prc6.cgi"
            response = session.post(base_url, data=form_data, headers=headers)
            response.raise_for_status()
            
            # Add debug information
            st.write("Debug: Response Status Code:", response.status_code)
            
            # Parse the results page
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for table rows
            table_rows = soup.find_all('tr')
            st.write(f"Debug: Found {len(table_rows)} table rows")
            
            # Look for the "More Info" link
            more_info_link = None
            for row in table_rows:
                link = row.find('a', string='More Info')
                if link:
                    more_info_link = link
                    break
            
            if more_info_link:
                # Get the relative URL and make it absolute
                detail_url = more_info_link['href']
                if not detail_url.startswith('http'):
                    detail_url = 'https://taxrecords-nj.com/pub/cgi/' + detail_url
                
                return detail_url
            else:
                # Additional debugging: Print part of the response
                st.write("Debug: Response preview:")
                st.code(response.text[:500])  # Show first 500 characters
                return None
                
    except requests.exceptions.RequestException as e:
        st.error(f"Network error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        st.write("Debug: Full error details:", str(e))
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
        padding: 12px 0;
        font-size: 16px;
    }
    .stTextInput>div>div>input {
        font-size: 16px;
        padding: 8px 12px;
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

# Create expander for debug info
debug_expander = st.expander("Debug Information", expanded=False)

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
