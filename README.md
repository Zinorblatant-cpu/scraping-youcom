# Web Scraper for Youcom Product Discounts

## 📌 Overview
This project is a Python-based web scraper designed to extract discounted product information from the Youcom website. It utilizes:

- **Selenium** for automated browsing
- **BeautifulSoup** for HTML parsing
- **JSON** for storing extracted data

## ✨ Features
- ✅ **Ensures complete page load** before extraction
- ✅ **Extracts key product details**:
  - Product Name
  - Current Price
  - Discount Percentage
  - Original Price (calculated)
  - Product Link
  - Image URL
- ✅ **Data validation and cleaning** for numerical accuracy
- ✅ **Headless browsing** for efficient execution
- ✅ **Exports results to a JSON file**

---
## ⚙️ Requirements
Ensure the following dependencies are installed:

- Python 3.x
- Google Chrome browser
- ChromeDriver

### 🔧 Install Dependencies
Run the following command to install the required packages:
```sh
pip install -r requirements.txt
```
**Contents of `requirements.txt`:**
```
beautifulsoup4
selenium
webdriver-manager
```

---
## 🚀 How It Works
### 1️⃣ Initialize WebDriver
The script configures **ChromeDriver** with headless options for optimized scraping.
```python
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--disable-gpu")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
```

### 2️⃣ Wait for Page Load
The function `wait_for_page_load(driver, url)` ensures the page is fully loaded before extraction:
```python
WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.TAG_NAME, "body"))
)
html_content = driver.page_source
```

### 3️⃣ Extract Product Information
The function `parse_products(all_htmls)`:
- Parses the loaded page with **BeautifulSoup**
- Filters only **discounted products**
- Cleans and formats price data:
```python
price = float(re.sub(r'[^\d,]', '', price).replace('.', '').replace(',', '.'))
original_price = float(re.sub(r'[^\d,]', '', original_price).replace(',', '.').strip())
```
- Stores product details in **JSON format**

### 4️⃣ Save Extracted Data
The extracted data is saved as a JSON string and printed to the console:
```python
json_string = json.dumps(output_data, ensure_ascii=False, indent=4)
sys.stdout.buffer.write(json_string.encode("utf-8"))
```

---
## ▶️ Running the Script
Execute the script with:
```sh
python scraper.py
```
The scraped data will be printed in **JSON format**.

---
## 🔍 Notes
- Ensure **ChromeDriver** is compatible with your browser version.
- You may need to **adjust waiting times** depending on website responsiveness.

---
## 📜 License
This project is open-source and available under the **MIT License**.

