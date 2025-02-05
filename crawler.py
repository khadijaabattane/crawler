import json
import urllib.robotparser
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
import time

# Configuration initiale
START_URL = "https://web-scraping.dev/products"
MAX_PAGES = 50
OUTPUT_FILE = "results.json"
CRAWL_DELAY = 1  # Délai en secondes entre les requêtes


def is_valid_url(url, base_domain):
    """
    Vérifie si une URL est valide et appartient au même domaine.

    Args:
        url (str): L'URL à valider.
        base_domain (str): Le domaine de base pour la comparaison.

    Returns:
        bool: True si l'URL est valide et appartient au même domaine, False sinon.
    """
    parsed = urlparse(url)
    return parsed.netloc == base_domain and parsed.scheme in {"http", "https"}


def get_urls(soup, base_url, base_domain):
    """
    Extrait tous les liens valides d'une page HTML et les convertit en liens absolus.

    Args:
        soup (BeautifulSoup): L'objet BeautifulSoup représentant la page HTML.
        base_url (str): L'URL de base pour convertir les liens relatifs en absolus.
        base_domain (str): Le domaine de base pour filtrer les liens internes.

    Returns:
        list: Une liste de liens absolus appartenant au domaine.
    """
    links = [urljoin(base_url, a['href']) for a in soup.find_all('a', href=True)]
    return [link for link in links if is_valid_url(link, base_domain)]


def can_fetch(url):
    """
    Vérifie si une URL peut être crawlée en respectant les règles du fichier robots.txt.

    Args:
        url (str): L'URL à vérifier.

    Returns:
        bool: True si l'URL peut être crawlée, False sinon.
    """
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(urljoin(url, "/robots.txt"))
    rp.read()
    return rp.can_fetch("*", url)


def extract_page_data(url):
    """
    Analyse une page HTML et extrait son titre, premier paragraphe et liens.

    Args:
        url (str): L'URL de la page à analyser.

    Returns:
        dict: Un dictionnaire contenant le titre, le premier paragraphe, et les liens de la page.
              Retourne None en cas d'erreur.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.title.string if soup.title else ""
        first_paragraph = soup.find('p').get_text(strip=True) if soup.find('p') else ""
        base_domain = urlparse(url).netloc
        links = get_urls(soup, url, base_domain)

        return {
            "title": title,
            "url": url,
            "first_paragraph": first_paragraph,
            "links": links
        }
    except Exception as e:
        print(f"Error fetching or parsing {url}: {e}")
        return None


def fetch_page(queue, visited, results, base_domain):
    """
    Traite une URL, extrait les données de la page et ajoute de nouveaux liens à la file d'attente.

    Args:
        queue (deque): La file d'attente des URLs à visiter.
        visited (set): L'ensemble des URLs déjà visitées.
        results (list): La liste des résultats collectés.
        base_domain (str): Le domaine de base pour filtrer les liens internes.

    Returns:
        None
    """
    current_url = queue.popleft()
    if current_url in visited:
        return

    if not can_fetch(current_url):
        print(f"Skipping {current_url}, disallowed by robots.txt")
        return

    print(f"Crawling: {current_url}")
    data = extract_page_data(current_url)
    if data:
        results.append({
            "title": data["title"],
            "url": data["url"],
            "first_paragraph": data["first_paragraph"],
            "links": data["links"]
        })
        for link in data["links"]:
            if "product" in link and link not in visited:
                queue.append(link)

    visited.add(current_url)
    time.sleep(CRAWL_DELAY)  # Respecte un délai entre les requêtes


def crawl(start_url, max_pages):
    """
    Lance le processus de crawling.

    Args:
        start_url (str): L'URL de départ pour le crawling.
        max_pages (int): Le nombre maximum de pages à crawler.

    Returns:
        list: Une liste de dictionnaires contenant les informations collectées pour chaque page.
    """
    base_domain = urlparse(start_url).netloc
    visited = set()
    queue = deque([start_url])
    results = []

    while queue and len(visited) < max_pages:
        fetch_page(queue, visited, results, base_domain)

    return results


def execute_crawler():
    """
    Point d'entrée principal du script. Lance le crawling et sauvegarde les résultats dans un fichier JSON.

    Returns:
        None
    """
    results = crawl(START_URL, MAX_PAGES)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)
    print(f"Crawling terminé. Résultats sauvegardés dans {OUTPUT_FILE}")


if __name__ == "__main__":
    execute_crawler()
