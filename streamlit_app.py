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
        # Initialize session
        session = requests.Session()
        
        # Headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        # Search form data
        search_data = {
            'ms_user': 'ctb09',
            'passwd': '',
            'district': '0906',
            'adv': '1',
            'out_type': '0',
            'srch_type': '1',
            'items_page': '50',
            'county': 'HUDSON',
            'location': address.upper()
        }

        with st.spinner("Searching property records..."):
            # Make the initial search request
            search_url = "https://taxrecords-nj.com/pub/cgi/prc6.cgi"
            response = session.post(search_url, data=search_data, headers=headers)
            response.raise_for_status()
            
            # Debug information
            st.write("Debug: Response Status Code:", response.status_code)
            
            # Parse the response
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for all links in the page
            all_links = soup.find_all('a')
            st.write(f"Debug: Found {len(all_links)} links")
            
            # Look specifically for the table with the results
            tables = soup.find_all('table')
            st.write(f"Debug: Found {len(tables)} tables")
            
            # Print table contents for debugging
            if tables:
                for i, table in enumerate(tables):
                    st.write(f"Debug: Table {i+1} contents:")
                    st.code(table.get_text()[:200])  # Show first 200 chars of each table
            
            # Look for the More Info link
            more_info = soup.find('a', string=lambda x: x and 'More Info' in x)
            
            if more_info and 'href' in more_info.attrs:
                detail_url = more_info['href']
                if not detail_url.startswith('http'):
                    detail_url = 'https://taxrecords-nj.com/pub/cgi/' + detail_url
                return detail_url
            else:
                st.write("Debug: HTML Content Preview:")
                st.code(response.text[:1000])  # Show first 1000 chars
                return None
                
    except requests.exceptions.RequestException as e:
        st.error(f"Network error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
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
    div[data-testid="stExpander"] {
        border: 1px solid #ddd;
        border-radius: 4px;
        margin-top: 1rem;
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
