import json
import string
import os
import nltk
import math
import threading
from collections import defaultdict
from nltk.corpus import stopwords
from textblob import TextBlob
from rapidfuzz import process

# Download stopwords (only needed once)
nltk.download('stopwords')
STOPWORDS = set(stopwords.words('english'))

### 🔹 LOAD INDEXES ###
def load_index(filepath):
    """Loads a JSON index from file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

indexes = {
    "title": load_index("title_index.json"),
    "description": load_index("description_index.json"),
    "reviews": load_index("reviews_index.json"),
    "origin": load_index("origin_index.json"),
    "brand": load_index("brand_index.json"),
    "domain": load_index("domain_index.json")
}

origin_synonyms = load_index("origin_synonyms.json") if os.path.exists("origin_synonyms.json") else {}

### 🔹 SPELLING CORRECTION ###
def correct_spelling(query):
    """Corrects spelling mistakes using fuzzy matching and TextBlob."""
    known_words = set(indexes["title"].keys()) | set(indexes["description"].keys()) | set(indexes["brand"].keys()) | set(indexes["origin"].keys())

    if query in known_words:
        return query

    best_match = process.extractOne(query, known_words, score_cutoff=80)
    if best_match:
        return best_match[0]

    return str(TextBlob(query).correct())

### 🔹 TOKENIZATION ###
def tokenize(text):
    """Tokenizes text, removes punctuation & stopwords."""
    text = text.lower().translate(str.maketrans('', '', string.punctuation))
    return [token for token in text.split() if token not in STOPWORDS]

def tokenize_with_correction(text):
    """Tokenizes and applies spelling correction."""
    tokens = tokenize(text)
    return [correct_spelling(token) for token in tokens]

### 🔹 QUERY EXPANSION ###
def expand_origin_query(query_terms):
    """Expands query using synonyms from origin index."""
    expanded_terms = set(query_terms)
    for term in query_terms:
        if term in origin_synonyms:
            expanded_terms.update(origin_synonyms[term])
    return list(expanded_terms)

### 🔹 PRECOMPUTED BM25 RANKING ###
precomputed_tf_idf = {}

def precompute_tf_idf():
    """Precomputes TF-IDF for faster searching."""
    total_docs = len(indexes["title"])
    for term in indexes["description"]:
        df = len(indexes["description"][term])
        idf = math.log((total_docs - df + 0.5) / (df + 0.5) + 1)
        precomputed_tf_idf[term] = idf

precompute_tf_idf()

### 🔹 PARALLEL SEARCH FUNCTION ###
def search_parallel(term, results):
    """Searches for a term in parallel and updates results."""
    if term in indexes["title"]:
        for url in indexes["title"][term]:
            results[url]["score"] += 5 * precomputed_tf_idf.get(term, 1)
            results[url]["matches"].append(f"Title match: {term}")

    if term in indexes["description"]:
        for url in indexes["description"][term]:
            results[url]["score"] += 3 * precomputed_tf_idf.get(term, 1)
            results[url]["matches"].append(f"Description match: {term}")

    if term in indexes["brand"]:
        for url in indexes["brand"][term]:
            results[url]["score"] += 4
            results[url]["matches"].append(f"Brand match: {term}")

### 🔹 SEARCH FUNCTION WITH RESULTS DISPLAYED IN TERMINAL ###
def search(query):
    """Processes query, retrieves ranked search results, and stores history in JSON."""
    corrected_query = correct_spelling(query)

    if corrected_query.lower() != query.lower():
        print(f"🛑 Did you mean: **{corrected_query}**?")

    query_terms = tokenize_with_correction(corrected_query)
    query_terms = expand_origin_query(query_terms)

    print("\n🔍 **Final Tokenized Query:**", query_terms)

    results = defaultdict(lambda: {"score": 0, "matches": []})

    # Search each query term in parallel
    threads = []
    for term in query_terms:
        thread = threading.Thread(target=search_parallel, args=(term, results))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    # Sort results by score
    sorted_results = sorted(results.items(), key=lambda x: x[1]["score"], reverse=True)

    # 📌 **FORMAT RESULTS IN JSON WITH METADATA**
    search_entry = {
        "query": query,
        "metadata": {
            "total_documents": len(indexes["title"]),
            "filtered_documents": len(sorted_results)
        },
        "results": []
    }

    if len(sorted_results) == 0:
        print("\n⚠ No matching documents found.")
    else:
        print("\n🔍 **Search Results:**")

    # PRINT RESULTS IN TERMINAL
    for url, info in sorted_results[:10]:  # Show Top 10 in Terminal
        print("\n📌 **Product:**", url.split("/")[-1].replace("-", " ").title())
        print(f"🔗 URL: {url}")
        print(f"⭐ Score: {info['score']}")
        print(f"🎯 Matches: {', '.join(info['matches'])}")

        # Store full results in JSON
        search_entry["results"].append({
            "title": url.split("/")[-1].replace("-", " ").title(),
            "url": url,
            "description": "Description not available",
            "score": info["score"],
            "matches": info["matches"]
        })

    # 📌 **UPDATE QUERY HISTORY JSON**
    history_filepath = "query_history.json"

    if os.path.exists(history_filepath):
        with open(history_filepath, "r", encoding="utf-8") as f:
            query_history = json.load(f)
    else:
        query_history = []

    query_history.append(search_entry)

    with open(history_filepath, "w", encoding="utf-8") as f:
        json.dump(query_history, f, indent=4)

    print("\n✅ Query and results saved to `query_history.json`")

### 🔹 QUERY SUGGESTIONS ###
def suggest_query(prefix):
    """Suggests possible queries based on user input."""
    suggestions = [term for term in indexes["title"].keys() if term.startswith(prefix.lower())]
    return suggestions if suggestions else ["No suggestions found"]

if __name__ == "__main__":
    user_query = input("\n🔍 Enter your search query: ")

    # Show autocomplete suggestions
    suggestions = suggest_query(user_query)
    print("\n🔎 **Suggestions:**", suggestions)

    # Perform search
    search(user_query)
