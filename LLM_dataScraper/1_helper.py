from selenium import webdriver
from selenium.webdriver. common.keys import Keys
from selenium.webdriver. common.by import By
from urllib.request import urlopen
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import pandas as pd
from selenium.webdriver.chrome.options import Options
import streamlit as st
import google.generativeai as genai
import google.generativeai as palm
import PIL.Image
from PIL import Image
import textwrap
from IPython.display import Markdown
from io import BytesIO
import ast


class scraper:
    def __init__(self, key):
        self.GOOGLE_API_KEY=key
        genai.configure(api_key=self.GOOGLE_API_KEY)
        self.I_model = genai.GenerativeModel('gemini-pro-vision')

        #For LLM
        palm.configure(api_key=self.GOOGLE_API_KEY)
        models = [m for m in palm.list_models() if 'generateText' in m.supported_generation_methods]
        self.model = models[0].name


    def to_markdown(self,text):
        text = text.replace('•', '  *')
        return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

    def image_processor_stable(self,driver):
        img=driver.get_screenshot_as_png()
        screenshot_image = Image.open(BytesIO(img))
        temp_file_path = "screenshot.png"
        screenshot_image.save(temp_file_path)
        img = PIL.Image.open('screenshot.png')
        prompt ='''give a python dictionary of the product \
                    information in the image. dont include any other text other than the python distionary in the output. \
                    Make sure the dictionary is a single line piece of code. \
                    Make sure it is in the proper format of python dictionary with no additional information and spaces.\
                    Use dictionary keys as follows \
                    ['product_name','website','price','currency','sold_out','seller_name','product_type','other_seller_name','other_seller_price'].\
                    consider values that are missing to be empty also if the product is currently unnavailable or the price of it is missing, leave it empty corresponding to it's key value.\
                    Always include currency with the price.'''
        response = self.I_model.generate_content([prompt,img], stream=True)
        response.resolve()
        return response.text


    def walmart_image_processor_stable(self,driver):
        img=driver.get_screenshot_as_png()
        screenshot_image = Image.open(BytesIO(img))
        temp_file_path = "screenshot.png"
        screenshot_image.save(temp_file_path)
        img = PIL.Image.open('screenshot.png')
        prompt ='''give a python dictionary of the walmart product \
                    information in the google search image. dont include any other text other than the python distionary in the output. \
                    Make sure the dictionary is a single line piece of code. \
                    Make sure it is in the proper format of python dictionary with no additional information and spaces.\
                    Use dictionary keys as follows \
                    ['product_name','website','price','currency','sold_out','seller_name','product_type','other_seller_name','other_seller_price'].\
                    consider values that are missing to be empty also if the product is currently unnavailable or the price of it is missing, leave it empty corresponding to it's key value.\
                    Always include currency with the price. Consider only the walmart search result'''
        response = self.I_model.generate_content([prompt,img], stream=True)
        response.resolve()
        return response.text
    
    def cleanit(self,x):
            try: 
                x= x.replace('\n','') 
                x= x.replace('`','') 
                x=x.replace('python','')
                x=ast.literal_eval(x)
                return x
            except: 
                return x
    def normalize_dict(self,row,a):
        try:
            return row[a]
        except:
            return row
    
    def start_scraping(self,df,driver_path,prefix):
        # "C:/Users/Manoj.Prapagar/Downloads/chromedriver.exe"
        chrome_driver_path = driver_path
        chrome_options = Options()
        chrome_options.add_argument(f"executable_path={chrome_driver_path}")
        driver = webdriver.Chrome(options=chrome_options)
        data=pd.DataFrame()
        raw_data=[]
        amazon_flag=0
        # prefix=['buy','oreillyauto' , 'carparts.com' , 'harbour frieght','Autozone','Rockauto','NAPA','Rock auto','Summit','Onyx','amazon','ebay']
        # for aa in prefix:
        for index,values in df.iterrows():
            time.sleep(1)
            y=values['Part Number']+' '+values['Description (keywords)']+' '+values['Brand Name']
            print("Inside the main loop for ",y)
            driver.get("https://www.google.com")

            # Find the search input element and enter the query
            search_box = driver.find_element("name", "q")
            search_box.send_keys(prefix+'  '+  y)
            search_box.send_keys(Keys.RETURN)
            time.sleep(2)
            search_url=driver.current_url



            for i in range(0,16):
                    try:
                        # if i > 16:
                        #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        #     time.sleep(1)
                            # for aa in range(5):
                            #     driver.find_element("tag name", "body").send_keys(Keys.PAGE_UP)
                            #     time.sleep(1)
                        time.sleep(1)
                        results = driver.find_elements(By.CSS_SELECTOR,"h3")[:]
                        result=results[i]
                        # print('Now selecting this element : ',result.text)
                        if len(result.text)>13:
                            print(f"Clicking on result {i}: {result.text}")
                            time.sleep(1)
                            result.click()
                            time.sleep(1)
                            after_click_url=driver.current_url

                            if amazon_flag==0 and 'amazon.com' in after_click_url:
                                amazon_flag==1
                                time.sleep(20)

                            if 'google' not in after_click_url:
                                ####################################
                                time.sleep(3)
                                html=driver.page_source
                                flag=0
                                while 'Type the characters you see in' in html :
                                    html=driver.page_source
                                    flag=1
                                if flag==1:
                                    time.sleep(1)

                                # if 'amazon' in driver.current_url and amazon_flag==0:
                                #     print('inside if of amazon check')
                                #     # time.sleep(2)
                                #     # location = driver.find_element(By.ID, 'nav-global-location-popover-link')

                                #     # location.click()
                                #     # time.sleep(3)
                                #     # pin = driver.find_element(By.ID, 'GLUXZipUpdateInput')
                                #     # pinnumber='94203'
                                #     # pin.send_keys(pinnumber)

                                #     # apply=driver.find_element(By.CSS_SELECTOR, 'span.a-button-inner[data-action="GLUXPostalUpdateAction"]')
                                #     # apply.click()
                                #     while 'India' in driver.page_source:
                                #          if '''You're now shopping for delivery to''' in driver.page_source:
                                #             time.sleep(3)
                                #             break
                                #          pass
                                #     print('outside')
                                #     amazon_flag==1

                                html=driver.page_source     
                                soup = BeautifulSoup(html, 'html.parser')

                                # Extract all text from the parsed HTML
                                all_text = soup.get_text(separator='\n', strip=True)
                                prompt =''' Forget the previous converstation.\
                                            From the below gived data extracted from html of a page, return a python disctionary which has the following as key values\
                                            ['product_name','website','price','currency','sold_out','seller_name','product_type','other_seller_name','other_seller_price'] . Under the key value of product_type always fill either 'motor_spare' or 'others'.\
                                            Sold_out key should have the value of 'true' or 'false'.\
                                            if you are not able to find a value for any of the the above mentioned dictionary key , have the corresponding key value as empty.\
                                            make sure you arent hallucinating. Return only the dictionary and nothing other than that. Output should be just the dictionary.\
                                            Here's the data extracted from the HTML : \n 
                                            ''' + str(all_text)  +'''\n make sure to return only the required dictionary as mentioned at first '''
                                completion = palm.generate_text(
                                    model=self.model,
                                    prompt=prompt,
                                    temperature=0,
                                    # The maximum length of the response
                                    max_output_tokens=800,
                                )
                                if str(completion.result)!='None' and 'price' in completion.result and 'Motor Oil' not in completion.result:
                                    dummy={'search':y,'result':completion.result ,'url':driver.current_url}
                                    raw_data.append(dummy)
                                    print(completion.result)
                                    # st.write(completion.result)
                                    print("~~~"*40)
                                    if 'google' not in driver.current_url:
                                        while 'google' not in driver.current_url:
                                            driver.back()
                                            time.sleep(1)
                                        
                                    
                                else:
                                    
                                    print('inside if-else image processor')
                                    for i in range(0,2):
                                            webdriver.ActionChains(driver).send_keys(Keys.DOWN).perform()
                                    if 'ebay' in driver.current_url:
                                        #  driver.find_element("tag name", "body").send_keys(Keys.PAGE_DOWN)
                                        for i in range(0,7):
                                            webdriver.ActionChains(driver).send_keys(Keys.DOWN).perform()
                                    a=self.image_processor_stable(driver)
                                    print(a)
                                    # st.write(a)
                                    dummy={'search':y,'result':a ,'url':driver.current_url}
                                    raw_data.append(dummy)
                                    print("~~~"*40)
                                    if 'google' not in driver.current_url:
                                        while 'google' not in driver.current_url:
                                            driver.back()
                                            time.sleep(1)
                        else:
                            pass
                            
                    except:
                        try:
                            # cuurent_url=driver.current_url
                            if 'google' not in after_click_url:
                                print('inside except image processor')
                                for i in range(0,2):
                                    webdriver.ActionChains(driver).send_keys(Keys.DOWN).perform()
                                if 'ebay' in driver.current_url:
                                    #  driver.find_element("tag name", "body").send_keys(Keys.PAGE_DOWN)
                                    for i in range(0,7):
                                        webdriver.ActionChains(driver).send_keys(Keys.DOWN).perform()
                                a=self.image_processor_stable(driver)
                                print(a)
                                # st.write(a)
                                dummy={'search':y,'result':a ,'url':driver.current_url}
                                raw_data.append(dummy)
                                print("~~~"*40)
                                print('image processing inside except is completed')
                                if 'google' not in driver.current_url:
                                        while 'google' not in driver.current_url:
                                            driver.back()
                                            time.sleep(1)
                            else:
                                pass
                        except:
                            if 'google' not in driver.current_url:
                                        while 'google' not in driver.current_url:
                                            driver.back()
                                            time.sleep
                            print('error : ',i)

        output=pd.DataFrame(raw_data)
        
        output['result']=output['result'].apply(self.cleanit)
        lst=['product_name','website','price','currency','sold_out','seller_name','product_type','other_seller_name','other_seller_price']
        for a in lst:
            output[a]=output['result'].apply(self.normalize_dict,args=(a,))
        output.drop('result',axis=1,inplace=True)
        return output