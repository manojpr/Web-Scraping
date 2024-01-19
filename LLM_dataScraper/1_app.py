import streamlit as st
import pandas as pd 
import helper
st.sidebar.title("Python google data harvester")
upload_file=st.sidebar.file_uploader("Choose a File")
api_key=st.sidebar.text_input('Enter Gemini API KEY')
driver_path=st.sidebar.text_input('Enter your chrome driver path')
selected_option = st.selectbox("prefix word to search", ['buy','oreillyauto' , 'carparts.com' , 'harbour frieght','Autozone','Rockauto','NAPA','Rock auto','Summit','Onyx','amazon','ebay'])
if upload_file is not None and api_key !='':
    
    try:
        st.sidebar.success("Done")
        df=pd.read_excel(upload_file)
        st.write(''' -> Make sure you change the pincode to '56002' when the program enters into amazon.com for the first time ( usually happens in the first minute) ''')
        st.write(''' -> Make sure you are available to solve amazon captchas, or the program waits forever for you to complete it ''')
        if st.button("Aware of the above and start scraping"):
            a=helper.scraper(api_key)
            df=a.start_scraping(df,driver_path,selected_option)
    except:
        st.header(''' Harvesting stopped because of unnexpected issues, Try again ''')
    st.dataframe(df)