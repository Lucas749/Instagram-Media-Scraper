# Import packages
import os
import requests
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Assign instagram url and retrieve account names
URL = "https://instagram.com/"
account_list = input("Enter account names (comma separated):")
account_list = account_list.replace(" ", "").split(",")

# Specify folder path and automatically create folder if non existent
FOLDER_LOCATION = "FOLDER_PATH"
if not os.path.exists(FOLDER_LOCATION): os.mkdir(FOLDER_LOCATION)

# Assign selenium parameters
CHROME_PATH = "CHROMEDRIVER_PATH"
chrome_options = Options()
chrome_options.add_argument("--headless")

# Download pictures for all entered accounts
for account_name in account_list:
    # Create new folder for every account
    if not os.path.exists(FOLDER_LOCATION + "\\" + account_name): os.mkdir(FOLDER_LOCATION + "\\" + account_name)

    # Open instagram user site in chrome
    driver = webdriver.Chrome(CHROME_PATH, options=chrome_options)
    driver.get(URL + account_name)

    # Fully scroll down to load all pictures and retrieve html data
    html = driver.page_source
    for i in range(0, 200):
        time.sleep(0.2)
        driver.execute_script("window.scrollTo(0, window.scrollY + 300)")
        html = html + driver.page_source
    html = html + driver.page_source

    # Check if account is private and continue if not
    if html.find("This Account is Private") == -1:
        soup = BeautifulSoup(html, "html.parser")
        links = soup.find_all('a', href=True)

        # Retrieve link and check if picture specific
        links = [link.get('href') for link in links if link.get('href')[0:3] == "/p/"]
        links = list(set(links))

        # Open all href links and retrieve full size image link
        im_url_list = []

        for link in links:
            # Open post and retrieve image url
            driver.get(urljoin(URL, link))
            post_html = driver.page_source
            post_soup = BeautifulSoup(post_html, "html.parser")
            image_url = post_soup.find_all('img')[1]

            # Fix bad "Bad URL timestamp" problem by deleting "amp;"
            image_url = str(image_url).replace("amp;", "").split("src=")[1].split('"')[1]

            # Append image url list
            im_url_list.append(image_url)

        # Download pictures
        counter = 1
        for image_url in im_url_list:
            filename = FOLDER_LOCATION + "\\" + account_name + "\\" + account_name + "_" + str(counter) + ".jpg"
            try:
                if str(image_url).find("jpg") != -1:
                    with open(filename, 'wb') as f:
                        f.write(requests.get(image_url).content)
                    counter = counter + 1
            except:
                print("Error")
    else:
        print("Account is private!")
    driver.close()
