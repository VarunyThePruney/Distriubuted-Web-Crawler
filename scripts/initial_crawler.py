import requests
from bs4 import BeautifulSoup

URL = "https://www.w3schools.com/mongodb/mongodb_mongosh_find.php"

def crawl_page(URL):
    print(f"Crawling: {URL}")
    
    respose = requests.get(URL, timeout=5)
    respose.raise_for_status()
    
    soup = BeautifulSoup(respose.text, 'html.parser')
    
    title = soup.title.string if soup.title else "No title found"
    
    links = []
    for a in soup.find_all("a", href=True):
        links.append(a["href"])

    print("title:", title)
    print("num links found:", len(links))
    print("links:", links[:40])


if __name__ == "__main__":
    crawl_page(URL)