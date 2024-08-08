from bs4 import BeautifulSoup
import requests
import time
import re
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
import logging
import json
import cssutils
import argparse

parser = argparse.ArgumentParser(description='extract website style')
parser.add_argument('url', help='url of the website')
parser.add_argument('-O', '--output', default='website_styles.json', help='output of the json file')
args = parser.parse_args()

# selenium with headless chrome
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
# create a session
sessions = requests.Session()
stylesheet_cache = {}

def scrape(url):
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'body')))
        page_source = driver.page_source
        content = BeautifulSoup(page_source, 'html.parser')
        return content
    except Exception as e:
        logging.error(f'Error fetching url: {e}')
        return None

def style(soup):
    styles = {}
    try:
        for element in soup.find_all(style=True):
            styles[str(element)] = element['style']
        for style in soup.find_all('style'):
            if style.string:
                sheet = cssutils.parseString(style.string)
                for rule in sheet:
                    if rule.type == rule.STYLE_RULE:
                        selector = rule.selectorText
                        property = rule.style.cssText
                        for element in soup.select(selector):
                            t = str(element)
                            if t not in styles:
                                styles[t] = property
                            else:
                                styles[t] += ';' + property
    except Exception as e:
        logging.warning(f'Error in style extraction: {e}')
    return styles

def external_css(soup, url):
    styles = {}
    try:
        for link in soup.find_all('link', rel='stylesheet'):
            css_url = link.get('href')
            if not css_url.startswith('http'):
                css_url = f"{url.rstrip('/')}/{css_url.lstrip('/')}"
            
            if css_url not in stylesheet_cache:
                response = sessions.get(css_url)
                if response.status_code == 200:
                    stylesheet_cache[css_url] = response.text
                else:
                    logging.warning(f"Failed to fetch CSS from {css_url}")
                    continue
            
            sheet = cssutils.parseString(stylesheet_cache[css_url])
            for rule in sheet:
                if rule.type == rule.STYLE_RULE:
                    selector = rule.selectorText
                    property = rule.style.cssText
                    for element in soup.select(selector):
                        t = str(element)
                        if t not in styles:
                            styles[t] = property
                        else:
                            styles[t] += ';' + property
    except Exception as e:
        logging.warning(f'Error in external CSS extraction: {e}')
    return styles

def main():
    url = args.url
    output_file = args.output

    soup = scrape(url)
    if soup is None:
        print("Failed to scrape the website.")
        return

    inline_embedded_styles = style(soup)
    external_styles = external_css(soup, url)

    # Combine all styles
    all_styles = {**inline_embedded_styles, **external_styles}

    # Save to JSON file
    with open(output_file, 'w') as f:
        json.dump(all_styles, f, indent=2)

    print(f"Styles have been extracted and saved to {output_file}")

    # Close the webdriver
    driver.quit()

if __name__ == "__main__":
    main()