import json
import urllib.robotparser
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from collections import deque

# Configuration initiale
START_URL = "https://web-scraping.dev/products"
MAX_PAGES = 50
OUTPUT_FILE = "results.json"

# Fonction pour vérifier les droits d'accès selon robots.txt
def can_fetch(url):
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(urljoin(url, "/robots.txt"))
    rp.read()
    return rp.can_fetch("*", url)

# Fonction pour analyser le contenu d'une page HTML
def parse_html(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.title.string if soup.title else ""
        first_paragraph = ""
        if (p := soup.find('p')):
            first_paragraph = p.get_text(strip=True)
        
        links = [urljoin(url, a['href']) for a in soup.find_all('a', href=True)]
        return {
            "title": title,
            "url": url,
            "first_paragraph": first_paragraph,
            "links": links
        }
    except Exception as e:
        print(f"Error parsing {url}: {e}")
        return None

# Fonction principale pour le crawling
def crawl(start_url, max_pages):
    visited = set()
    queue = deque([start_url])
    results = []

    while queue and len(visited) < max_pages:
        current_url = queue.popleft()
        if current_url in visited:
            continue

        if not can_fetch(current_url):
            print(f"Skipping {current_url}, disallowed by robots.txt")
            continue

        print(f"Crawling: {current_url}")
        data = parse_html(current_url)
        if data:
            results.append({
                "title": data["title"],
                "url": data["url"],
                "first_paragraph": data["first_paragraph"],
                "links": [link for link in data["links"] if "product" in link]
            })

            # Ajouter de nouveaux liens à la file d'attente
            for link in data["links"]:
                if link not in visited and "product" in link:
                    queue.append(link)

        visited.add(current_url)

    return results

# Lancer le crawling et stocker les résultats
def main():
    results = crawl(START_URL, MAX_PAGES)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)
    print(f"Crawling terminé. Résultats sauvegardés dans {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
