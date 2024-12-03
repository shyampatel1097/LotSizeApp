import streamlit as st
import re
from playwright.sync_api import sync_playwright
import time

def validate_address(address):
    """Validate address format and return cleaned version"""
    address = address.lower().strip()
    pattern = r'^\d+\s+[a-zA-Z]+\s+(?:ave|st|rd|dr|ln|ct|pl|blvd|cir)$'
    if not re.match(pattern, address):
        return None
    return address

def search_property(address):
    """Search property using Playwright"""
    try:
        with st.spinner("Searching property records..."):
            with sync_playwright() as p:
                # Launch browser
                browser = p.chromium.launch(headless=True)
                context = browser.new_context()
                page = context.new_page()
                
                # Navigate to search page
                url = "https://taxrecords-nj.com/pub/cgi/prc6.cgi?ms_user=ctb09&district=0906&adv=1"
                page.goto(url)
                
                # Wait for form to load
                page.wait_for_selector('input[name="location"]')
                
                # Fill form
                page.fill('input[name="location"]', address.upper())
                page.select_option('select[name="database"]', '0')  # Current Owners/Assmt List
                page.select_option('select[name="county"]', '09')   # HUDSON
                
                # Submit form
                page.click('input[value="Submit Search"]')
                
                # Wait for results
                page.wait_for_load_state('networkidle')
                
                st.write("Debug: Current URL:", page.url)
                
                # Look for More Info link
                more_info = page.query_selector('a:text("More Info")')
                if more_info:
                    # Get href attribute
                    href = more_info.get_attribute('href')
                    if href:
                        detail_url = href if href.startswith('http') else f"https://taxrecords-nj.com/pub/cgi/{href}"
                        
                        # Click the link
                        more_info.click()
                        page.wait_for_load_state('networkidle')
                        
                        # Get final URL
                        final_url = page.url
                        
                        browser.close()
                        return final_url
                
                # If no results found
                st.write("Debug: Page content preview:")
                st.code(page.content()[:500])
                browser.close()
                return None
                
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
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
