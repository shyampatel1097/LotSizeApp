import streamlit as st
import re
import requests
from bs4 import BeautifulSoup
import urllib.parse
import json

def validate_address(address):
    """Validate address format and return cleaned version"""
    address = address.lower().strip()
    pattern = r'^\d+\s+[a-zA-Z]+\s+(?:ave|st|rd|dr|ln|ct|pl|blvd|cir)$'
    if not re.match(pattern, address):
        return None
    return address

def search_property(address):
    """Search property using requests"""
    try:
        session = requests.Session()
        
        # Set up headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://taxrecords-nj.com',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache'
        }

        with st.spinner("Searching property records..."):
            # Step 1: Get initial page and cookies
            base_url = "https://taxrecords-nj.com/pub/cgi/prc6.cgi"
            initial_params = {
                'ms_user': 'ctb09',
                'district': '0906',
                'adv': '1'
            }
            
            response = session.get(f"{base_url}?{urllib.parse.urlencode(initial_params)}", headers=headers)
            st.write("Debug: Initial response status:", response.status_code)
            
            # Step 2: Prepare search data
            search_data = {
                'ms_user': 'ctb09',
                'passwd': '',
                'p_loc': '',
                'owner': '',
                'block': '',
                'lot': '',
                'qual': '',
                'location': address.upper(),
                'database': '0',
                'county': '09',
                'district': '0906',
                'items_page': '50',
                'srch_type': '1',
                'out_type': '0',
                'Submit Search': 'Submit Search'
            }
            
            # Step 3: Submit search
            st.write("Debug: Submitting search with data:", json.dumps(search_data, indent=2))
            search_response = session.post(base_url, data=search_data, headers=headers)
            
            st.write("Debug: Search response status:", search_response.status_code)
            st.write("Debug: Search response URL:", search_response.url)
            
            # Parse response
            soup = BeautifulSoup(search_response.text, 'html.parser')
            
            # Look for results table
            tables = soup.find_all('table')
            for table in tables:
                if table.find('td', text=lambda t: t and address.upper() in t):
                    st.write("Debug: Found matching address in table")
                    more_info = table.find('a', string='More Info')
                    if more_info and 'href' in more_info.attrs:
                        detail_url = more_info['href']
                        if not detail_url.startswith('http'):
                            detail_url = 'https://taxrecords-nj.com/pub/cgi/' + detail_url
                        return detail_url
            
            # If we got here, no results were found
            st.write("Debug: Response preview:")
            st.code(search_response.text[:500])
            return None
            
    except requests.RequestException as e:
        st.error(f"Network error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return None

# UI Code
st.set_page_config(page_title="Jersey City Property Lookup", page_icon="🏠", layout="centered")

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
