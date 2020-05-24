# Import packages
import os
import requests
import time
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Assign instagram url and retrieve account names
URL = "https://instagram.com/"
account_list = input("Enter account names (comma separated):")
account_list = account_list.replace(" ", "").split(",")

# Retrieve username and password for instagram if allowed
log_in = input("Log-in to download from private accounts? (Y/N):")
if log_in == "Y":
    username = input("Username:")
    password = input("Password:")

# Specify folder path and automatically create folder if non existent
FOLDER_LOCATION = 'FOLDER_PATH'
if not os.path.exists(FOLDER_LOCATION): os.mkdir(FOLDER_LOCATION)

# Assign selenium parameters
CHROME_PATH = 'CHROMEDRIVER_PATH'
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument('log-level=3')

# Download pictures for all entered accounts
for account_name in account_list:
    # Assign driver
    driver = webdriver.Chrome(CHROME_PATH, options=chrome_options)

    # Open account site and get html
    driver.get(URL + account_name)
    html = driver.page_source

    # Retrieve account status
    unavailable = html.find("The link you followed may be broken, or the page may have been removed.") != -1
    private = html.find("This Account is Private") != -1

    # Skip non-existent accounts
    if unavailable:
        print("Account name incorrect")
        continue

    # Skip private account if no log-in permission
    if private and log_in != "Y":
        print("Account is private and no permission to log-in!")
        continue

    # Log in to instagram if permission and account private
    if private and log_in == "Y":
        driver.get(URL)
        time.sleep(2)
        driver.find_element_by_name('username').send_keys(username)
        driver.find_element_by_name('password').send_keys(password)
        driver.find_element_by_xpath("//button[@type='submit']").click()
        time.sleep(2)

    # Create new folder for every account
    if not os.path.exists(FOLDER_LOCATION + "\\" + account_name): os.mkdir(FOLDER_LOCATION + "\\" + account_name)
    if not os.path.exists(FOLDER_LOCATION + "\\" + account_name + "\\" + "Pictures"): os.mkdir(
        FOLDER_LOCATION + "\\" + account_name + "\\" + "Pictures")
    if not os.path.exists(FOLDER_LOCATION + "\\" + account_name + "\\" + "Videos"): os.mkdir(
        FOLDER_LOCATION + "\\" + account_name + "\\" + "Videos")

    # Open account site
    driver.get(URL + account_name)

    # Fully scroll down to load all pictures and retrieve html data
    html = driver.page_source
    for i in range(0, 450):
        time.sleep(0.1)
        driver.execute_script("window.scrollTo(0, window.scrollY + 400)")
        driver.execute_script("window.scrollTo(0, window.scrollY - 10)")
        html = html + driver.page_source

    # Extract links from html
    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all('a', href=True)

    # Retrieve link and check if picture specific
    links = [link.get('href') for link in links if link.get('href')[0:3] == "/p/"]
    links = list(set(links))

    # Open all href links and retrieve full size image and video link
    im_url_list = []
    vid_url_list = []

    for link in links:
        # Open post and retrieve image url
        driver.get(urljoin(URL, link))

        # Retrieve html and repeat if error
        post_html = driver.page_source
        while str(post_html).find('"status": "fail"') != -1:
            time.sleep(0.5)
            driver.refresh()
            post_html = driver.page_source

        post_soup = BeautifulSoup(post_html, "html.parser")
        video_url = post_soup.find_all(type=re.compile('video/mp4'))

        # Check if media is video
        if len(video_url) == 0:

            # Catch error as sometimes src is missing
            try:
                image_url = post_soup.find_all(content=re.compile('^https://scontent'))

                if len(image_url) > 0:
                    image_url = image_url[0].get("content")
                else:
                    image_url = post_soup.find_all("img")[1].get("src")

                # Fix bad "Bad URL timestamp" problem by deleting "amp;"
                image_url = str(image_url).replace("amp;", "")

                # Append image url list
                im_url_list.append(image_url)
            except:
                pass
        else:
            video_url = post_soup.find_all(type=re.compile('video/mp4'))[0]

            # Fix bad "Bad URL timestamp" problem by deleting "amp;"
            video_url = str(video_url.get("src")).replace("amp;", "")

            # Append vid url list
            vid_url_list.append(video_url)

    # Download pictures
    counter = 1
    for image_url in im_url_list:
        filename = FOLDER_LOCATION + "\\" + account_name + "\\" + "Pictures" + "\\" + account_name + "_" + str(
            counter) + ".jpg"
        try:
            if str(image_url).find("jpg") != -1:
                with open(filename, 'wb') as f:
                    f.write(requests.get(image_url).content)
                counter = counter + 1
        except:
            print("Error")

    # Download videos
    counter = 1
    for video_url in vid_url_list:
        filename = FOLDER_LOCATION + "\\" + account_name + "\\" + "Videos" + "\\" + account_name + "_" + str(
            counter) + ".mp4"
        try:
            if str(video_url).find("mp4") != -1:
                with open(filename, 'wb') as f:
                    f.write(requests.get(video_url).content)
                counter = counter + 1
        except:
            print("Error")

    print(account_name + " done: " + str(len(im_url_list)) + " pictures & " + str(len(vid_url_list)) + " videos")
    driver.close()
