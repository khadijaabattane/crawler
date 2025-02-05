import json
import string
import os
from collections import defaultdict

# Load indexes from JSON files
def load_index(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

# Tokenization function: removes punctuation, converts to lowercase, and splits into words
def tokenize(text):
    text = text.lower().translate(str.maketrans('', '', string.punctuation))
    return text.split()

# Load all indexes
indexes = {
    "title": load_index("title_index.json"),
    "description": load_index("description_index.json"),
    "reviews": load_index("reviews_index.json"),
    "origin": load_index("origin_index.json"),
    "brand": load_index("brand_index.json"),
    "domain": load_index("domain_index.json")
}

# Load origin synonyms (if applicable)
origin_synonyms = load_index("origin_synonyms.json") if os.path.exists("origin_synonyms.json") else {}

def expand_origin_query(query_terms):
    """
    Expands query terms using synonyms from the origin index.
    """
    expanded_terms = set(query_terms)
    for term in query_terms:
        if term in origin_synonyms:
            expanded_terms.update(origin_synonyms[term])
    return list(expanded_terms)

def search(query):
    """
    Searches for products based on the user query and returns results in JSON format.

    Ranking factors:
    - Title match (highest weight)
    - Description match
    - Brand and origin match (extra relevance boost)
    - Review scores (average rating, number of reviews)
    """
    query_terms = tokenize(query)
    query_terms = expand_origin_query(query_terms)

    results = defaultdict(lambda: {"score": 0, "matches": []})

    # Search in title index
    for term in query_terms:
        if term in indexes["title"]:
            for url in indexes["title"][term]:
                results[url]["score"] += 5  # High weight for title matches
                results[url]["matches"].append(f"Title match: {term}")

    # Search in description index
    for term in query_terms:
        if term in indexes["description"]:
            for url in indexes["description"][term]:
                results[url]["score"] += 3  # Medium weight for description matches
                results[url]["matches"].append(f"Description match: {term}")

    # Search in brand index
    for term in query_terms:
        if term in indexes["brand"]:
            for url in indexes["brand"][term]:
                results[url]["score"] += 4  # Brand relevance
                results[url]["matches"].append(f"Brand match: {term}")

    # Search in origin index
    for term in query_terms:
        if term in indexes["origin"]:
            for url in indexes["origin"][term]:
                results[url]["score"] += 4  # Origin relevance
                results[url]["matches"].append(f"Origin match: {term}")

    # Apply review-based ranking boost
    for url in results:
        if url in indexes["reviews"]:
            review_data = indexes["reviews"][url]
            total_reviews = review_data.get("total_reviews", 0)
            avg_score = review_data.get("average_score", 0)
            last_score = review_data.get("last_score", 0)

            # Boost based on review score and number of reviews
            results[url]["score"] += avg_score * 2  # Average review score contributes to ranking
            results[url]["score"] += total_reviews * 0.5  # More reviews = slightly higher ranking

            results[url]["matches"].append(f"Review score: {avg_score} (Total reviews: {total_reviews})")

    # Sort results by score (highest first)
    sorted_results = sorted(results.items(), key=lambda x: x[1]["score"], reverse=True)

    # Format results as JSON
    formatted_results = {
        "total_documents": len(indexes["title"]),  # Total indexed products
        "filtered_documents": len(sorted_results),  # Number of matching products
        "results": []
    }

    for url, info in sorted_results[:10]:  # Limit to top 10 results
        formatted_results["results"].append({
            "title": url.split("/")[-1].replace("-", " ").title(),  # Extracting title from URL
            "url": url,
            "description": "Description not available",  # Placeholder if description is missing
            "score": info["score"]
        })

    return json.dumps(formatted_results, indent=4)

# Example usage
if __name__ == "__main__":
    user_query = input("Enter your search query: ")
    result_json = search(user_query)
    print(result_json)
