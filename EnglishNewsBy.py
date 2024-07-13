import random
import requests
from moviepy.editor import VideoFileClip, AudioFileClip
from bs4 import BeautifulSoup
from gtts import gTTS
from selenium.webdriver.common.by import By
import uuid
import os
from selenium.webdriver import ActionChains
import time
from selenium import webdriver

import cv2
import numpy as np
import random
from moviepy.editor import AudioFileClip, ImageClip

unique_filename = str(uuid.uuid4())
def get_news_from_toi(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print('Failed to fetch the page:', e)
        return []

    soup = BeautifulSoup(response.content, 'html.parser')

    articles = []

    # Find the <ul> with the specific class
    ul = soup.find('ul', {'class': 'article-list'})  # Replace 'your_ul_class' with the actual class name
    if ul:
        # Find all <li> tags within this <ul>
        lis = ul.find_all('li')
        for li in lis:
            # Within each <li>, find the <figure> tag
            h3= li.find('h3')
            if h3:
                a=h3.find('a')
                if a and 'href' in a.attrs:
                    title = a.text.strip()
                    link = a['href']
                    articles.append({
                        'title': title,
                        'link': link
                    })

    return articles

def extract_article_text(url,alttext):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print('Failed to fetch the page:', e)
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract article text
    article_text = ''
    div= soup.find('div', {'class' : 'story_details'})#.find_all('p')  # Update class based on the actual structure
    if div:
        pall = div.find_all('p')
        if pall:
            for p in pall[0:2]:
                text = p.text.strip()
                article_text+=text
                text =''
        else :
            print("div1 article not found")
    else :
        print("div not found")

    # for paragraph in div1:
    #     article_text += paragraph.get_text() + '\n'

    return article_text

def get_audio(text):
    tts = gTTS(text=text, lang='en')
    # fileprefix = random.randint(1, 1000)
    file_path = f"{unique_filename}.mp3"
    tts.save(file_path)
    # os.system(f'start {file_path}')
    return file_path

def get_image_from_url(title,numberOfImages):
    #List of paths of image where saved
    imgPaths=[]
    # Set up the Chrome WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    driver = webdriver.Chrome(options=options)
    # Navigate to the web page
    driver.get(f"https://www.google.com/search?q={title}&tbm=isch")
    # Hovering over the elements so we can get the href link in a tag , as have dynamic loading
    elements = driver.find_elements(By.CSS_SELECTOR, 'div.H8Rx8c')  # Adjust the CSS selector as needed
    # Initialize ActionChains
    actions = ActionChains(driver)
    for element in elements[0:numberOfImages]:
        actions.move_to_element(element).perform()
    # Define the number of times to scroll
    scroll_count = 0 # if we need more values we can use this
    # Create an ActionChains object to perform the hover action
    actions = ActionChains(driver)
    # Simulate continuous scrolling using JavaScript
    for _ in range(scroll_count):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Wait for the new results to load (adjust as needed)
    # Get the page source after scrolling
    page_source = driver.page_source
    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(page_source, "html.parser")
    # Extract and print search results
    search_results = soup.find_all("h3", class_="ob5Hkd")
    driver.quit()
    for result in search_results[0:numberOfImages]:
        a=result.find('a')
        if a:
            # print(a)
            href =a.get('href')
            if href:
                hrefimg = 'https://www.google.com'+href
                print(hrefimg)

                options = webdriver.ChromeOptions()
                options.add_argument('headless')
                options.add_argument('window-size=1920x1080')
                driver = webdriver.Chrome(options=options)

                driver.get(hrefimg)
                elements = driver.find_elements(By.CSS_SELECTOR, 'div.p7sI2 PUxBg')  # Adjust the CSS selector as needed
                # Initialize ActionChains
                actions = ActionChains(driver)
                for element in elements:
                    actions.move_to_element(element).perform()
                page_source = driver.page_source
                # Parse the page source with BeautifulSoup
                soup = BeautifulSoup(page_source, "html.parser")
                imgdiv=soup.find('div',{'class':'p7sI2 PUxBg'})
                if imgdiv:
                    imgtag=imgdiv.find_all('img')
                    if imgtag:
                        for imgs in imgtag[0:1]:
                            link=imgs.get('src')
                            # calling image download function to dowbload image and to save
                            path=download_image(link, save_directory)
                            imgPaths.append(path)
                            print(link)
                    else:
                        print("no img tag found in p7sI2 PUxBg")
                else:
                    print("no such div found p7sI2 PUxBg")
                driver.quit()
            else:
                print("no href link found in a(for img)")
        else:
            print("a does not exist")
    return imgPaths

def download_image(image_url, save_directory):
    # Generate a unique filename using uuid
    r =str(random.randint(1,100))
    filename =unique_filename + r +".jpg"
    # Create the full path to save the image
    save_path = os.path.join(save_directory,filename)
    # Make a request to fetch the image content
    response = requests.get(image_url)
    if response.status_code == 200:
        # Write the content to a file
        with open(filename, 'wb') as file:
            file.write(response.content)
        print(f"Image successfully downloaded and saved as {filename}")
        return filename
    else:
        print(f"Failed to retrieve image. Status code: {response.status_code}")

'''def add_static_image_to_audio(image_path, audio_path, output_path):
    """Create and save a video file to `output_path` after
    combining a static image that is located in `image_path`
    with an audio file in `audio_path`"""
    # create the audio clip object
    audio_clip = AudioFileClip(audio_path)
    # create the image clip object
    image_clip = ImageClip(image_path)
    # use set_audio method from image clip to combine the audio with the image
    video_clip = image_clip.set_audio(audio_clip)
    # specify the duration of the new clip to be the duration of the audio clip
    video_clip.duration = audio_clip.duration
    # set the FPS to 1
    video_clip.fps = 1
    # write the resuling video clip
    video_clip.write_videofile(output_path)'''

def add_static_image_to_audio(image_paths, audio_path, output_path):
    width, height = 1280, 720
    FPS = 24
    # Create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    video = cv2.VideoWriter('./output.avi', fourcc, float(FPS), (width, height))

    audio_clip = AudioFileClip(f"{audio_path}")
    video_clip= audio_clip.duration

    # Loop through each picture and add it to the video
    for picture in image_paths:
        img = cv2.imread(picture)
        img = cv2.resize(img, (width, height))  # Resize the image to fit the video dimensions
        for _ in range(FPS * int(video_clip) // len(image_paths)):
            video.write(img)
    # Release the video writer
    video.release()
    ####
    # Load the video with animation and transition
    video_clip = VideoFileClip("./output.avi")

    # Add the audio to the video
    final_clip = video_clip.set_audio(audio_clip)

    # Save the final video
    final_clip.write_videofile(f"{output_path}")

url = 'https://indianexpress.com/section/technology/'
news_articles = get_news_from_toi(url)

save_directory ="C:\\Users\\hp\\Documents\\INSTAautoREEl"

if news_articles:
    for i, article in enumerate(news_articles, start=1):
        print(f"{i}. {article['title']}")
        print(f"URL: {article['link']}\n")
    sel=int(input("Enter one of the number"))
    print("article title")
    title=news_articles[sel-1]['title']
    print(title)
    url2 =news_articles[sel-1]['link']
    print(url2)
    textfound=extract_article_text(url2,title)
    if textfound:
        print("Article Text:")
        print(textfound)

        # calling get audio function to convert text which is textfound to audio
        audiopath = get_audio(textfound)

        # Get images related to text from google by sctraping
        imgpath = get_image_from_url(title,4)

        vediopath= unique_filename+'.mp4'
        vedio_path = os.path.join(save_directory, vediopath)


        add_static_image_to_audio(imgpath ,audiopath ,vediopath)

    else:
        print("Failed to extract article text.")
else:
    print("No news articles found.")