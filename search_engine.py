import json
import string
import os
import nltk
from collections import defaultdict
from nltk.corpus import stopwords

nltk.download('stopwords')
STOPWORDS = set(stopwords.words('english'))

def load_index(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def tokenize(text):
    text = text.lower().translate(str.maketrans('', '', string.punctuation))
    tokens = text.split()
    return [token for token in tokens if token not in STOPWORDS]

indexes = {
    "title": load_index("title_index.json"),
    "description": load_index("description_index.json"),
    "reviews": load_index("reviews_index.json"),
    "origin": load_index("origin_index.json"),
    "brand": load_index("brand_index.json"),
    "domain": load_index("domain_index.json")
}

origin_synonyms = load_index("origin_synonyms.json") if os.path.exists("origin_synonyms.json") else {}

def expand_origin_query(query_terms):
    expanded_terms = set(query_terms)
    for term in query_terms:
        if term in origin_synonyms:
            expanded_terms.update(origin_synonyms[term])
    return list(expanded_terms)

def filter_by_all_tokens(query_terms, url):
    for term in query_terms:
        if not (
            (term in indexes["title"] and url in indexes["title"][term]) or
            (term in indexes["description"] and url in indexes["description"][term]) or
            (term in indexes["brand"] and url in indexes["brand"][term]) or
            (term in indexes["origin"] and url in indexes["origin"][term])
        ):
            return False
    return True

def log_history(query, metadata, results):
    history_entry = {
        "query": query,
        "metadata": metadata,
        "results": results
    }

    history_file = "search_history.json"
    if os.path.exists(history_file):
        with open(history_file, "r+", encoding="utf-8") as f:
            history = json.load(f)
            history.append(history_entry)
            f.seek(0)
            json.dump(history, f, indent=4)
    else:
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump([history_entry], f, indent=4)

def get_title(url):
    """ Retrieves the actual title from the title index. """
    for title, urls in indexes["title"].items():
        if url in urls:
            return title.capitalize()
    return "Title not available"

def get_description(url):
    """ Retrieves the actual description from the description index. """
    for desc, urls in indexes["description"].items():
        if url in urls:
            return desc
    return "Description not available"

def search(query):
    query_terms = tokenize(query)
    query_terms = expand_origin_query(query_terms)

    results = defaultdict(lambda: {"score": 0, "matches": []})

    for term in query_terms:
        if term in indexes["title"]:
            for url in indexes["title"][term]:
                results[url]["score"] += 5
                results[url]["matches"].append(f"Title match: {term}")

    for term in query_terms:
        if term in indexes["description"]:
            for url in indexes["description"][term]:
                results[url]["score"] += 3
                results[url]["matches"].append(f"Description match: {term}")

    for term in query_terms:
        if term in indexes["brand"]:
            for url in indexes["brand"][term]:
                results[url]["score"] += 4
                results[url]["matches"].append(f"Brand match: {term}")

    for term in query_terms:
        if term in indexes["origin"]:
            for url in indexes["origin"][term]:
                results[url]["score"] += 4
                results[url]["matches"].append(f"Origin match: {term}")

    for url in results:
        if url in indexes["reviews"]:
            review_data = indexes["reviews"][url]
            total_reviews = review_data.get("total_reviews", 0)
            avg_score = review_data.get("average_score", 0)
            results[url]["score"] += avg_score * 2
            results[url]["score"] += total_reviews * 0.5
            results[url]["matches"].append(f"Review score: {avg_score} (Total reviews: {total_reviews})")

    filtered_results = {url: info for url, info in results.items() if filter_by_all_tokens(query_terms, url)}
    sorted_results = sorted(filtered_results.items(), key=lambda x: x[1]["score"], reverse=True)

    formatted_results = {
        "total_documents": len(indexes["title"]),
        "filtered_documents": len(sorted_results),
        "results": []
    }

    print("\n🔍 **Search Results:**")
    for url, info in sorted_results[:10]:
        product_result = {
            "title": get_title(url),  # Fixed: Retrieve actual title
            "url": url,
            "description": get_description(url),  # Fixed: Retrieve actual description
            "score": info["score"]
        }
        formatted_results["results"].append(product_result)

        print(f"\n📌 **Product:** {product_result['title']}")
        print(f"🔗 URL: {product_result['url']}")
        print(f"📝 Description: {product_result['description']}")
        print(f"⭐ Score: {product_result['score']}")
        print(f"🎯 Matches: {', '.join(info['matches'])}")

    metadata = {
        "total_documents": formatted_results["total_documents"],
        "filtered_documents": formatted_results["filtered_documents"]
    }
    log_history(query, metadata, formatted_results["results"])

    output_filepath = "search_results.json"
    with open(output_filepath, "w", encoding="utf-8") as f:
        json.dump(formatted_results, f, indent=4)

    print(f"\n✅ Search results saved to `{output_filepath}`")
    print(f"✅ Search history updated in `search_history.json`")

if __name__ == "__main__":
    user_query = input("\n🔍 Enter your search query: ")
    search(user_query)
