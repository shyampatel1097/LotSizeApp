import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import re
import time

def validate_address(address):
    """Validate address format and return cleaned version"""
    address = address.lower().strip()
    pattern = r'^\d+\s+[a-zA-Z]+\s+(?:ave|st|rd|dr|ln|ct|pl|blvd|cir)$'
    if not re.match(pattern, address):
        return None
    return address

def search_property(address):
    """Search property using Selenium"""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    try:
        with st.spinner("Searching property records..."):
            driver = webdriver.Chrome(options=options)
            wait = WebDriverWait(driver, 10)
            
            # Navigate to the search page
            url = "https://taxrecords-nj.com/pub/cgi/prc6.cgi?ms_user=ctb09&district=0906&adv=1"
            driver.get(url)
            
            # Wait for and fill out the form
            location_input = wait.until(EC.presence_of_element_located((By.NAME, "location")))
            location_input.send_keys(address.upper())
            
            # Select the correct options
            database_select = driver.find_element(By.NAME, "database")
            database_select.send_keys("0")  # Current Owners/Assmt List
            
            county_select = driver.find_element(By.NAME, "county")
            county_select.send_keys("09")  # HUDSON
            
            # Submit the form
            submit_button = driver.find_element(By.CSS_SELECTOR, "input[value='Submit Search']")
            submit_button.click()
            
            # Wait for results and check for More Info link
            try:
                more_info_link = wait.until(EC.presence_of_element_located((By.LINK_TEXT, "More Info")))
                detail_url = more_info_link.get_attribute('href')
                
                # Click the More Info link to get to the details page
                more_info_link.click()
                
                # Wait for the page to load and get the final URL
                time.sleep(2)  # Give the page time to load
                final_url = driver.current_url
                
                driver.quit()
                return final_url
                
            except:
                st.write("Debug: No More Info link found")
                # Capture the page source for debugging
                st.code(driver.page_source[:500])
                driver.quit()
                return None
                
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        try:
            driver.quit()
        except:
            pass
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
