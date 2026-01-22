import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

URL = "https://www.w3schools.com/mongodb/mongodb_mongosh_find.php"
max_pages = 5

visited = set()
queue = [URL]

def crawl_page(URL):
    print(f"Crawling: {URL}")
    try:
        respose = requests.get(URL, timeout=5)
        respose.raise_for_status()
    except requests.RequestException as ex:
        print(f"Failed {URL}: {ex}")
        return []
    
    soup = BeautifulSoup(respose.text, 'html.parser')
    
    title = soup.title.string if soup.title else "No title found"
    print("title:", title)

    links = []
    for a in soup.find_all("a", href=True):
        href = a['href']
        
        full_url = urljoin(URL, href)
        if urlparse(full_url).scheme in ("http", "https"):
            links.append(full_url)
    return links

def start_crawl():
    while queue and len(visited) < max_pages:
        curr_url = queue.pop(0)
        
        if curr_url in visited:
            continue
        visited.add(curr_url)
        
        new_links = crawl_page(curr_url)
        for link in new_links:
            if link not in visited and link not in queue:
                queue.append(link)
    


if __name__ == "__main__":
    start_crawl()