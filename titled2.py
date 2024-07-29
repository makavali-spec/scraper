import requests
from bs4 import BeautifulSoup
import re
import csv

def scrape_typography(url):
    # Fetch the webpage
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all elements with inline styles
    elements = soup.find_all(style=True)

    typography_data = []

    for element in elements:
        style = element.get('style')
        
        # Extract font-family
        font_family = re.search(r'font-family:\s*([^;]+)', style)
        
        # Extract font-size
        font_size = re.search(r'font-size:\s*([^;]+)', style)
        
        # Extract color
        color = re.search(r'color:\s*([^;]+)', style)

        if font_family or font_size or color:
            typography_data.append({
                'element': element.name,
                'font_family': font_family.group(1) if font_family else None,
                'font_size': font_size.group(1) if font_size else None,
                'color': color.group(1) if color else None
            })

    return typography_data

def save_to_csv(data, filename):
    keys = data[0].keys()
    with open(filename, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)

# Usage
url = 'https://ridge.com/'  # Replace with the URL you want to scrape

typography_info = scrape_typography(url)

# Print results
for item in typography_info:
    print(item)

# Save to CSV
save_to_csv(typography_info, 'typography_data.csv')