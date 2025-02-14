import re
import json
import sys
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def auto_scroll(driver, url):
    driver.get(url)
    total_height = 0  
    distance = 300  
    scroll_pause_time = 0.5  
    click_count = 0  
    start_time = time.time()  
    html_pages = []  # List to store HTMLs of all pages visited

    while True:
        driver.execute_script(f"window.scrollBy(0, {distance});")
        total_height += distance
        time.sleep(scroll_pause_time)

        if time.time() - start_time > 25:
            sys.stderr.write("[INFO] Scrolling in progress...\n")  

        scroll_height = driver.execute_script("return document.body.scrollHeight;")
        if total_height >= scroll_height - driver.execute_script("return window.innerHeight;"):
            sys.stderr.write("[INFO] End of page reached. Stopping scroll.\n")
            break

        if time.time() - start_time > 90:
            sys.stderr.write("[ERROR] Timeout reached (90s). Exiting.\n")
            return {"status": "error", "message": "Timeout after 90 seconds", "action": "stop_script"}

        # Store the HTML of the current page
        html_pages.append(driver.page_source)

    return html_pages  # Return all collected HTMLs

def parse_products(all_htmls):
    all_products = []
    max_items = 250
    cont = 0

    # Loop through all the collected HTML pages
    for html_content in all_htmls:
        soup = BeautifulSoup(html_content, 'html.parser')
        promotions = soup.find_all('div', class_='relative w-full overflow-hidden')
        
        for product in promotions:
            if cont >= max_items:
                sys.stderr.write('[INFO] Reached maximum limit (250 products)\n')
                break
            
            percentage_tag = product.find('span', class_='font-normal leading-s tracking-[-0.01em]')
            if not percentage_tag:
                continue
            
            name_tag = product.find('p', class_='h-full w-full lowercase leading-[20px] line-clamp-1 text-s')
            name = name_tag.text.strip() if name_tag else "Name not found"
            
            percentage = percentage_tag.text.strip()
            percentage = int(re.sub(r'[^\d]', '', percentage).strip())

            price_tag = product.find('span', class_='font-bold text-primary-main')
            price = price_tag.text.strip() if price_tag else "Price not found"
            price = float(re.sub(r'[^\d,]', '', price).replace('.', '').replace(',', '.')) if price_tag else 0.0
            
            original_price_tag = product.find('span', class_='mr-m text-primary-light line-through block')
            original_price = original_price_tag.text.strip() if original_price_tag else 'Original price not found'
            original_price = float(re.sub(r'[^\d,]', '', original_price).replace(',', '.').strip()) if original_price_tag else 0.0
            
            link_tag = product.find('a', href=True)
            link = 'https://www.youcom.com.br' + link_tag['href'] if link_tag else "Link not found"

            img_tag = product.find('img', class_='bg-neutrals-2 object-cover')
            if img_tag:
                img_url = img_tag.get('src')
                if img_url:
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    elif not img_url.startswith('http'):
                        img_url = 'https://www.youcom.com.br' + img_url
                else:
                    img_url = "Img not found"
            else:
                img_url = "Img not found"

            product_data = {
                'name': name,
                'price': price,
                'link': link,
                'img': img_url,
                'brand': 23,
                'discount': {
                    'before_price': original_price,
                    'after_price': price,
                    'percentage': percentage
                }
            }
            
            if product_data not in all_products:
                cont += 1
                all_products.append(product_data)
        
    return all_products, cont

if __name__ == '__main__':
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-webgl")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--enable-unsafe-swiftshader")
    chrome_options.add_argument("--disable-notifications")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    urls = [
        'https://www.youcom.com.br/promocao?o=descDate&pg=1',
        'https://www.youcom.com.br/promocao?o=descDate&pg=2',
        'https://www.youcom.com.br/promocao?o=descDate&pg=3',
        'https://www.youcom.com.br/promocao?o=descDate&pg=4',
        'https://www.youcom.com.br/promocao?o=descDate&pg=5',
        'https://www.youcom.com.br/promocao?o=descDate&pg=6',
        'https://www.youcom.com.br/promocao?o=descDate&pg=7'
    ]
    
    all_products = []
    total_products = 0

    for url in urls:
        html_pages = auto_scroll(driver, url)  # Captures all HTMLs during navigation for each URL
        products, cont = parse_products(html_pages)  # Passes all HTMLs to the parsing function
        all_products.extend(products)
        total_products += cont
        if total_products >= 250:
            break

    driver.quit()

    status = "success" if total_products >= 250 else "partial"
    message = f"Collected {total_products} products" if total_products < 250 else "Products successfully collected"

    output_data = {
        "status": status,
        "message": message,
        "collected_products": total_products,
        "products": all_products
    }

    json_string = json.dumps(output_data, ensure_ascii=False, indent=4)
    sys.stdout.buffer.write(json_string.encode("utf-8"))    