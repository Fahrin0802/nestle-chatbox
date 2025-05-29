# import requests
# from bs4 import BeautifulSoup
# from playwright.sync_api import sync_playwright


# def scrape_nestle_site(url="https://www.madewithnestle.ca/"):
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=False)
#         page = browser.new_page()
#         page.goto(url, timeout=60000)
#         page.wait_for_timeout(3000)  # wait for JS content to load

#         html = page.content()
#         browser.close()

#     soup = BeautifulSoup(html, "html.parser")

#     # ✅ Extract visible text from common tags
#     paragraphs = [
#         tag.get_text(strip=True)
#         for tag in soup.find_all(['p', 'span', 'div', 'h1', 'h2', 'li'])
#         if tag.get_text(strip=True)
#     ]

#     # ✅ Get all links
#     links = [a['href'] for a in soup.find_all('a', href=True)]

#     # ✅ Get all images
#     images = [img['src'] for img in soup.find_all('img') if 'src' in img.attrs]

#     # ✅ Get all tables
#     tables = [str(table) for table in soup.find_all('table')]

#     # ✅ Combine all text content
#     content = "\n".join(paragraphs + tables)

#     return {
#         "url": url,
#         "text": content,
#         "links": links,
#         "images": images
#     }
# if __name__ == "__main__":
#     data = scrape_nestle_site()
#     print(f"✅ Found {len(data['links'])} links and {len(data['images'])} images")
#     print("🔍 Sample text content:\n")
#     print(data['text'][:1000])  # Preview scraped text


# import requests
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin
# from playwright.sync_api import sync_playwright

# BASE_URL = "https://www.madewithnestle.ca"

# def scrape_page_with_playwright(url):
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=False)
#         # ✅ Create a browser context that mimics a real user
#         context = browser.new_context(
#             user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
#             java_script_enabled=True,
#             locale="en-US"
#         )
#         page = context.new_page()
#         page.set_default_timeout(60000)  # Optional: increase timeout
#         page.goto(url)
#         page.wait_for_timeout(5000)  # wait for JavaScript to load
#         html = page.content()
#         browser.close()

#     soup = BeautifulSoup(html, "html.parser")
#     paragraphs = [
#         tag.get_text(strip=True)
#         for tag in soup.find_all(['p', 'span', 'div', 'h1', 'h2', 'li'])
#         if tag.get_text(strip=True)
#     ]
#     tables = [str(table) for table in soup.find_all('table')]
#     content = "\n".join(paragraphs + tables)
#     return content, soup

# def scrape_all_pages():
#     visited = set()
#     to_visit = {BASE_URL}
#     all_text = ""

#     while to_visit:
#         current_url = to_visit.pop()
#         if current_url in visited:
#             continue
#         print(f"🔍 Scraping: {current_url}")
#         visited.add(current_url)

#         try:
#             content, soup = scrape_page_with_playwright(current_url)
#             all_text += content + "\n\n"

#             for a in soup.find_all("a", href=True):
#                 href = a["href"]
#                 full_url = urljoin(BASE_URL, href)
#                 if BASE_URL in full_url and full_url not in visited:
#                     to_visit.add(full_url)
#         except Exception as e:
#             print(f"❌ Failed to scrape {current_url}: {e}")

#     return all_text

# if __name__ == "__main__":
#     scraped_text = scrape_all_pages()
#     print(f"✅ Finished scraping. Total characters: {len(scraped_text)}")
#     print("🔍 Sample text content:\n")
#     print(scraped_text[:1000])
