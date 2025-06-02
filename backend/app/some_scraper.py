from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

PAGES_TO_SCRAPE = [
    "https://www.madewithnestle.ca/kit-kat",
    "https://www.madewithnestle.ca/kit-kat/kitkat-classic-tablet",
    "https://www.madewithnestle.ca/kit-kat/kitkat-classic-tablet#facts",
    "https://www.madewithnestle.ca/smarties",
    "https://www.madewithnestle.ca/recipes"
]

def scrape_with_playwright(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
            java_script_enabled=True,
            locale="en-US",
        )
        page = context.new_page()
        page.set_default_timeout(60000)
        page.goto(url)
        page.wait_for_timeout(4000)
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")
    paragraphs = [
        tag.get_text(strip=True)
        for tag in soup.find_all(['p', 'span', 'div', 'h1', 'h2', 'li'])
        if tag.get_text(strip=True)
    ]
    tables = [str(table) for table in soup.find_all('table')]
    return "\n".join(paragraphs + tables)

def scrape_all_pages():
    docs = []
    for url in PAGES_TO_SCRAPE:
        print(f"🔍 Scraping {url}")
        try:
            page_text = scrape_with_playwright(url)
            print(f"✅ Scraped {len(page_text)} characters")
            docs.append({"url": url, "text": page_text})
        except Exception as e:
            print(f"❌ Failed to scrape {url}: {e}")
    return docs

if __name__ == "__main__":
    results = scrape_all_pages()
    print(f"✅ Scraped {len(results)} pages total")
    print("\n🔍 Sample document:")
    print(results[0] if results else "No data scraped.")
    # Pretty print the list of dictionaries
    import json

    for i, entry in enumerate(results):
        print(f"\n📄 Document {i+1} from URL: {entry['url']}")
        print(json.dumps({
            "url": entry["url"],
            "text": entry["text"][:3000] + "..." if len(entry["text"]) > 3000 else entry["text"]
        }, indent=2))
