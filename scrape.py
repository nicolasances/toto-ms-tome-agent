from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def scrape_blog(url):
    # Initialize Playwright
    with sync_playwright() as p:
        # Launch a headless browser
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Navigate to the blog page
        page.goto(url, wait_until="networkidle")
        
        # Optionally wait for a specific element to load (e.g., content container)
        # page.wait_for_selector("div.blog-content")
        
        # Extract the content of the blog
        blog_content = page.content()  # Get the entire page HTML
        # blog_text = page.inner_text("page-body-div")  # Extract text from a specific element
        
        # Close the browser
        browser.close()
        
        soup = BeautifulSoup(blog_content, "html.parser")
        paragraphs = soup.find_all("p")
        for idx, p in enumerate(paragraphs, start=1):
            print(f"Paragraph {idx}: {p.get_text(strip=True)}")
        
        return {
            "html": blog_content,
            # "text": blog_text
        }

if __name__ == "__main__":
    # blog_url = "https://snails-shop-mta.craft.me/PaZe4KH5lo6NXF"  # Replace with your blog's URL
    blog_url = "https://snails-shop-mta.craft.me/RsmQFFdlfFLR0S"  # Replace with your blog's URL
    result = scrape_blog(blog_url)
    
    # with open('blog.txt', 'w') as file: 
    #     file.write(result["html"])
    # print("Blog Text:\n", result["html"])

