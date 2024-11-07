import re
import csv
import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup

# Initialize the WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run headless if you don't want to see the browser
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-javascript")  # Disable JavaScript
chrome_options.add_argument("--disable-gpu") 
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
# no proxy
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--proxy-server='direct://'")
driver = webdriver.Chrome(service=Service('./chromedriver-mac-arm64/chromedriver'), options=chrome_options)

# Prepare the CSV file
csv_file = open('results.csv', 'a', newline='', encoding='utf-8')
csv_writer = csv.writer(csv_file)

# Write headers only if the file is empty
if csv_file.tell() == 0:
    csv_writer.writerow(['Image Name', 'Description', 'Pulls', 'Stars Count', 'Tags', 'By', 'Last Updated', 'Official Status'])

# Start pagination
page = 1
while True:
    try:
        start_time = datetime.datetime.now()
        print(f"Loading page {page}...")
        
        # Load the Docker Hub HTML page
        driver.get(f"https://hub.docker.com/search?q=&type=image&page={page}")
        time.sleep(60)  # Wait for page contents to load
        print("Page load complete. Time over")
        
        load_end_time = datetime.datetime.now()
        print(f"Page {page} load took: {load_end_time - start_time}")
        
        if page > 9:
            # Scroll to the bottom to trigger dynamic content loading
            scroll_start_time = datetime.datetime.now()
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Wait for content to load
            scroll_end_time = datetime.datetime.now()
            print(f"Scrolling page {page} took: {scroll_end_time - scroll_start_time}")
            
            # After the page loads
            with open(f"page_{page}.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)

        # Parse the page with BeautifulSoup
        parse_start_time = datetime.datetime.now()
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        parse_end_time = datetime.datetime.now()
        print(f"Parsing page {page} took: {parse_end_time - parse_start_time}")

        # Find all image cards
        images_list = soup.find_all('a', attrs={'data-testid': 'imageSearchResult'})
        if not images_list:
            print(f"No more images found on page {page}. Stopping.")
            break  # No more images to process

        # Process each image
        for image in images_list:
            try:
                image_start_time = datetime.datetime.now()
                
                # Extract image name
                image_name_element = image.find('strong', attrs={'data-testid': 'product-title'})
                image_name = image_name_element.text.strip() if image_name_element else 'N/A'

                # Extract description
                description_element = image.find('div', class_=re.compile(r'^MuiTypography-root.*css-mysnhd$'))
                description = description_element.text.strip() if description_element else 'N/A'

                # Extract pulls count
                pulls_element = image.find('div', attrs={'data-testid': 'product-badges-and-data-count'})
                if pulls_element:
                    pulls_div = pulls_element.find('p', class_=re.compile(r'^MuiTypography-root.*css-1xp8ea0$'))
                    pulls = pulls_div.text.strip() if pulls_div else '0'
                else:
                    pulls = '0'

                # Extract stars count
                stars_count_element = image.find('div', class_=re.compile(r'^MuiStack-root css-tehqbb$'))
                stars_count_strong = stars_count_element.find('strong') if stars_count_element else None
                stars_count = stars_count_strong.text.strip() if stars_count_strong else '0'

                # Extract 'By' field
                by_element = image.find('a', attrs={'data-testid': 'org-link'})
                by = by_element.text.strip() if by_element else 'N/A'

                # Extract last updated
                last_updated_element = image.find('span', class_=re.compile(r'^MuiTypography-root.*css-m5mzoi$'))
                last_updated = last_updated_element.text.strip() if last_updated_element and 'Updated' in last_updated_element.text else 'N/A'

                # Extract tags
                tags_elements = image.find_all('div', attrs={'data-testid': 'productChip'})
                tags = [tag.find('span').text.strip() for tag in tags_elements] if tags_elements else []

                # Check for official status
                official_status = 'Official' if image.find('svg', attrs={'data-testid': 'official-icon'}) else 'Not Official'

                image_end_time = datetime.datetime.now()
                print(f"Processing image took: {image_end_time - image_start_time}")

                # Write the extracted data to the CSV file
                # csv_writer.writerow([image_name, description, pulls, stars_count, ', '.join(tags), by, last_updated, official_status])

                # Print the extracted data (optional)
                print(f"Image Name: {image_name}")
                print(f"Description: {description}")
                print(f"Pulls: {pulls}")
                print(f"Stars Count: {stars_count}")
                print(f"Tags: {', '.join(tags) if tags else 'N/A'}")
                print(f"By: {by}")
                print(f"Last Updated: {last_updated}")
                print(f"Official Status: {official_status}")
                print("-" * 40)
            except Exception as e:
                print(f"Error processing image: {e}")

        # Increment the page number

    except Exception as e:
        print(f"Error loading page {page}: {e}")
        break
    page += 1

# Close the CSV file
csv_file.close()

# Quit the WebDriver
driver.quit()