import streamlit as st
import re
import requests
from bs4 import BeautifulSoup
import urllib.parse

def validate_address(address):
    """Validate address format and return cleaned version"""
    address = address.lower().strip()
    pattern = r'^\d+\s+[a-zA-Z]+\s+(?:ave|st|rd|dr|ln|ct|pl|blvd|cir)$'
    if not re.match(pattern, address):
        return None
    return address

def search_property(address):
    """Search property and return results"""
    try:
        session = requests.Session()
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://taxrecords-nj.com',
            'Referer': 'https://taxrecords-nj.com/pub/cgi/prc6.cgi'
        }

        with st.spinner("Searching property records..."):
            # Build the search URL with proper parameters
            base_url = "https://taxrecords-nj.com/pub/cgi/prc6.cgi"
            
            # Initial form data
            initial_params = {
                'ms_user': 'ctb09',
                'district': '0906',
                'adv': '1'
            }
            
            # Get the initial page to establish session
            initial_response = session.get(f"{base_url}?{urllib.parse.urlencode(initial_params)}")
            initial_response.raise_for_status()
            
            # Now prepare the search form data
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
                'location': address.upper()
            }
            
            # Get the search form page first
            form_response = session.post(base_url, data=search_data, headers=headers)
            form_response.raise_for_status()
            
            # Now extract the form and its hidden fields
            soup = BeautifulSoup(form_response.text, 'html.parser')
            form = soup.find('form')
            
            if form:
                # Get all form inputs
                inputs = form.find_all('input')
                final_search_data = {}
                
                # Build the complete form data including hidden fields
                for input_field in inputs:
                    if 'name' in input_field.attrs:
                        name = input_field['name']
                        value = input_field.get('value', '')
                        final_search_data[name] = value
                
                # Update with our search parameters
                final_search_data.update({
                    'location': address.upper(),
                    'database': '0',
                    'county': '09',
                    'district': '0906',
                    'items_page': '50',
                    'srch_type': '1',
                    'out_type': '0',
                    'Submit': 'Submit Search'
                })
                
                st.write("Debug: Final search data:", final_search_data)
                
                # Submit the final search
                search_response = session.post(base_url, data=final_search_data, headers=headers)
                search_response.raise_for_status()
                
                # Parse the response
                results_soup = BeautifulSoup(search_response.text, 'html.parser')
                
                # Look for any table containing property data
                tables = results_soup.find_all('table')
                for table in tables:
                    table_text = table.get_text()
                    if any(keyword in table_text for keyword in ['Block', 'Lot', 'Location']):
                        st.write("Debug: Found property results table")
                        more_info = table.find('a', string='More Info')
                        if more_info and 'href' in more_info.attrs:
                            detail_url = more_info['href']
                            if not detail_url.startswith('http'):
                                detail_url = 'https://taxrecords-nj.com/pub/cgi/' + detail_url
                            return detail_url
                
                st.write("Debug: Response content preview:")
                st.code(search_response.text[:500])
            
            return None
                
    except requests.exceptions.RequestException as e:
        st.error(f"Network error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return None

# UI Code remains the same
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
