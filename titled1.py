import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin

def scrape_typography(url):
    # Fetch the webpage
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all text elements
    text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'a', 'li', 'div'])

    typography_data = []

    for element in text_elements:
        # Get the element's text and tag name
        text = element.get_text(strip=True)
        tag = element.name

        # Get inline styles
        style = element.get('style', '')

        # Get classes
        classes = ' '.join(element.get('class', []))

        # Extract typography information
        font_family = extract_style_property(style, 'font-family')
        font_size = extract_style_property(style, 'font-size')
        font_weight = extract_style_property(style, 'font-weight')
        line_height = extract_style_property(style, 'line-height')
        color = extract_style_property(style, 'color')
        text_transform = extract_style_property(style, 'text-transform')

        typography_data.append({
            'text': text[:50],  # Truncate long text
            'tag': tag,
            'classes': classes,
            'font_family': font_family,
            'font_size': font_size,
            'font_weight': font_weight,
            'line_height': line_height,
            'color': color,
            'text_transform': text_transform
        })

    return typography_data

def extract_style_property(style, property_name):
    if property_name in style:
        return style.split(property_name + ':')[1].split(';')[0].strip()
    return ''

def save_to_csv(data, filename):
    keys = data[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)

        dict_writer.writeheader()
        dict_writer.writerows(data)

# Usage
url = 'https://ridge.com/'  # Replace with the URL you want to scrape
typography_data = scrape_typography(url)
save_to_csv(typography_data, 'typography_data.csv')

print(f"Typography data from {url} has been scraped and saved to typography_data.csv")