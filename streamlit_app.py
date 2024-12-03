import streamlit as st
import re
import requests
from bs4 import BeautifulSoup
import time
import urllib.parse

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
        # Initialize session
        session = requests.Session()
        
        # Headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        with st.spinner("Searching property records..."):
            # First, construct the URL with query parameters
            base_url = "https://taxrecords-nj.com/pub/cgi/prc6.cgi"
            params = {
                'ms_user': 'ctb09',
                'passwd': '',
                'district': '0906',
                'adv': '1',
                'out_type': '0',
                'srch_type': '1'
            }
            
            # Get initial page with session cookie
            initial_url = f"{base_url}?{urllib.parse.urlencode(params)}"
            session.get(initial_url)
            
            # Prepare search form data
            search_data = {
                'ms_user': 'ctb09',
                'passwd': '',
                'district': '0906',
                'adv': '1',
                'out_type': '0',
                'srch_type': '1',
                'database': '0',
                'county': '09',
                'items_page': '50',
                'location': address.upper(),
                'submit_button': 'Submit Search'
            }
            
            # Submit the search
            st.write("Debug: Submitting search with data:", search_data)
            response = session.post(base_url, data=search_data, headers=headers, allow_redirects=True)
            response.raise_for_status()
            
            # Debug information
            st.write("Debug: Search Response Status Code:", response.status_code)
            st.write("Debug: Response URL:", response.url)
            
            # Parse the response
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for table with class 'datatable' or any table containing property data
            tables = soup.find_all('table')
            
            for table in tables:
                # Check table contents
                table_text = table.get_text()
                if 'Block' in table_text and 'Lot' in table_text:
                    st.write("Debug: Found property data table")
                    st.write("Debug: Table contents preview:")
                    st.code(table_text[:200])
                    
                    # Look for More Info link
                    more_info = table.find('a', string='More Info')
                    if more_info and 'href' in more_info.attrs:
                        detail_url = more_info['href']
                        if not detail_url.startswith('http'):
                            detail_url = 'https://taxrecords-nj.com/pub/cgi/' + detail_url
                        return detail_url
            
            st.write("Debug: HTML Response Preview:")
            st.code(response.text[:500])
            return None
                
    except requests.exceptions.RequestException as e:
        st.error(f"Network error: {str(e)}")
        st.write("Debug: Full error details:", str(e))
        return None
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        st.write("Debug: Full error details:", str(e))
        return None

# Set page config and UI components remain the same
st.set_page_config(
    page_title="Jersey City Property Lookup",
    page_icon="🏠",
    layout="centered"
)

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

st.title("Jersey City Property Lookup 🏠")

st.markdown("""
    ### Enter Property Address
    Format: number + street name + abbreviated type  
    Example: "192 olean ave" or "413 summit ave"
""")

address = st.text_input("Property Address:", key="address_input")

if st.button("Find Property Details"):
    if not address:
        st.error("Please enter an address")
    else:
        clean_address = validate_address(address)
        if not clean_address:
            st.error("Please enter address in correct format: number + street name + abbreviated type (ave, st, rd, etc.)")
        else:
            result_url = search_property(clean_address)
            
            if result_url:
                st.success("Property found! Click below to view details:")
                st.markdown(f"[View Property Details]({result_url})", unsafe_allow_html=True)
            else:
                st.error("Property not found or an error occurred. Please check the address and try again.")

st.markdown("---")
st.markdown("Made with Streamlit ❤️")
