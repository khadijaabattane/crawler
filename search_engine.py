import json
import re
import os
import math
from datetime import datetime
from typing import List, Set, Dict
import nltk
from nltk.corpus import stopwords

# 📖 Downloading NLTK stopwords
nltk.download("stopwords")
STOPWORDS = set(stopwords.words("english"))

# 📂 Class to load indexes and product data
class IndexLoader:
    def __init__(self, index_path: str = "./"):
        self.index_path = index_path
        self.indexes = self.load_indexes()
        self.products = self.load_products()

    def load_indexes(self) -> Dict[str, dict]:
        """
        Load all index files from the specified directory.
        Returns a dictionary with index names as keys and their data as values.
        """
        index_files = [
            "indexes_fournis/brand_index.json",
            "indexes_fournis/description_index.json",
            "indexes_fournis/domain_index.json",
            "indexes_fournis/origin_index.json",
            "indexes_fournis/origin_synonyms.json",
            "indexes_fournis/reviews_index.json",
            "indexes_fournis/title_index.json"
        ]
        return {os.path.basename(file).replace(".json", ""): self.load_file(file) for file in index_files}

    def load_file(self, filename: str) -> dict:
        """
        Load a single JSON file and return its content.
        """
        with open(os.path.join(self.index_path, filename), "r") as f:
            return json.load(f)

    def load_products(self) -> Dict[str, dict]:
        """
        Load product data from a JSONL file.
        Each line in the file represents a product.
        """
        products = {}
        with open(os.path.join(self.index_path, "indexes_fournis/products.jsonl"), "r") as f:
            for line in f:
                product = json.loads(line)
                products[product["url"]] = product
        return products

# 🌍 Class for text processing tasks
class TextProcessor:
    @staticmethod
    def tokenize(text: str) -> List[str]:
        """
        Tokenize the input text, converting it to lowercase, removing stopwords and keeping only alphabetic tokens.
        """
        return [token for token in re.findall(r'\b\w+(?:-\w+)*\b', text.lower()) if token.isalpha() and token not in STOPWORDS]

    @staticmethod
    def expand_with_synonyms(tokens: List[str], synonyms_dict: Dict[str, List[str]]) -> List[str]:
        """
        Expand the query tokens with synonyms from the provided dictionary.
        """
        expanded_tokens = set(tokens)
        for token in tokens:
            for key, synonyms in synonyms_dict.items():
                if token == key or token in synonyms:
                    expanded_tokens.update(synonyms)
                    expanded_tokens.add(key)
        return list(expanded_tokens)

# 🔍 Class for document filtering based on query tokens
class DocumentFilter:
    def __init__(self, indexes: Dict[str, dict]):
        self.indexes = indexes

    def filter_any_token(self, tokens: List[str]) -> Set[str]:
        """
        Filter documents that contain at least one of the query tokens.
        """
        matching_docs = set()
        for token in tokens:
            matching_docs.update(self.indexes['title_index'].get(token, {}).keys())
            matching_docs.update(self.indexes['description_index'].get(token, {}).keys())
            matching_docs.update(self.indexes['brand_index'].get(token, []))
            matching_docs.update(self.indexes['origin_index'].get(token, []))
        return matching_docs

    def filter_all_tokens(self, tokens: List[str]) -> Set[str]:
        """
        Filter documents that contain all of the query tokens.
        """
        if not tokens:
            return set()
        matching_docs = self.filter_any_token([tokens[0]])
        for token in tokens[1:]:
            matching_docs &= self.filter_any_token([token])
        return matching_docs

# 📊 Class for ranking documents using BM25 and other signals
class BM25Ranker:
    def __init__(self, indexes: Dict[str, dict], products: Dict[str, dict]):
        self.indexes = indexes
        self.products = products

    def compute_bm25_score(self, doc_url: str, query_tokens: List[str], k1: float = 1.5, b: float = 0.75) -> float:
        """
        Compute the BM25 score for a document given a list of query tokens.
        """
        score = 0
        doc = self.products[doc_url]
        doc_text = f"{doc.get('title', '')} {doc.get('description', '')}"
        doc_tokens = TextProcessor.tokenize(doc_text)

        avg_doc_length = 300  
        doc_length = len(doc_tokens)

        for token in query_tokens:
            tf = doc_tokens.count(token)
            doc_count = len(self.indexes['title_index'].get(token, {})) + len(self.indexes['description_index'].get(token, {}))

            if doc_count == 0:
                continue

            idf = math.log((len(self.products) - doc_count + 0.5) / (doc_count + 0.5) + 1)
            numerator = tf * (k1 + 1)
            denominator = tf + k1 * (1 - b + b * (doc_length / avg_doc_length))
            score += idf * (numerator / denominator)

        return score

    def compute_final_score(self, doc_url: str, query: str, query_tokens: List[str]) -> Dict[str, float]:
        """
        Compute the final ranking score for a document, combining BM25, exact match, title match, and review scores.
        """
        doc = self.products[doc_url]
        scores = {
            'bm25_score': self.compute_bm25_score(doc_url, query_tokens) * 0.4,
            'exact_match_score': 0,
            'title_match_score': 0,
            'review_score': 0,
            'final_score': 0
        }

        # 🔍 Exact match bonus
        if query.lower().strip() == doc.get('title', '').lower().strip() or query.lower().strip() == doc.get('brand', '').lower().strip():
            scores['exact_match_score'] = 2.0

        # 📅 Title match bonus (tokens found in the title)
        title_tokens = TextProcessor.tokenize(doc.get('title', ''))
        title_matches = sum(1 for token in query_tokens if token in title_tokens)
        scores['title_match_score'] = title_matches * 0.2

        # 🌟 Review score based on user ratings
        if doc_url in self.indexes['reviews_index']:
            review_data = self.indexes['reviews_index'][doc_url]
            base_review_score = (review_data['mean_mark'] * 0.3 + min(review_data['total_reviews'], 10) * 0.1)
            scores['review_score'] = base_review_score * 0.3

        scores['final_score'] = sum(scores.values())
        return scores

# 📁 Function to save search results in JSON format
def save_results_as_json(results: Dict, query: str):
    """
    Save the search results to a JSON file with metadata.
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"search_results_{query.replace(' ', '_')}_{timestamp}.json"
    with open(filename, 'w') as f:
        json.dump(results, f, indent=4)
    print(f"Results saved to {filename}")

# 🔧 Main execution block
if __name__ == "__main__":
    # Initialize components
    index_loader = IndexLoader(index_path="./")
    text_processor = TextProcessor()
    doc_filter = DocumentFilter(index_loader.indexes)
    ranker = BM25Ranker(index_loader.indexes, index_loader.products)

    # 📄 Test queries to evaluate the search engine
    test_queries = [
        "Box of Chocolate Candy",
        "Organic Coffee Beans",
        "Black Cotton T-shirt",
        "Running Shoes for Men",
        "Gaming Laptop with RGB Keyboard",
        "Reusable Stainless Steel Water Bottle",
        "American Made Products",
    ]

    # Process each query
    for query in test_queries:
        print(f"\n=== Query: {query} ===")
        tokens = text_processor.tokenize(query)
        expanded_tokens = text_processor.expand_with_synonyms(tokens, index_loader.indexes['origin_synonyms'])

        matching_docs = doc_filter.filter_any_token(expanded_tokens)

        ranked_docs = []
        for doc_url in matching_docs:
            scores = ranker.compute_final_score(doc_url, query, expanded_tokens)
            doc = index_loader.products.get(doc_url, {"title": "No Title", "description": ""})
            ranked_docs.append({
                'title': doc['title'],
                'url': doc_url,
                'description': doc['description'],
                'scores': scores,
                'score': round(scores['final_score'], 3)
            })

        ranked_docs.sort(key=lambda x: x['score'], reverse=True)

        results = {
            'metadata': {
                'query': query,
                'timestamp': datetime.now().isoformat(),
                'total_documents': len(index_loader.products),
                'filtered_documents': len(matching_docs)
            },
            'results': ranked_docs
        }

        # Display top 3 results
        for i, doc in enumerate(ranked_docs[:3], 1):
            print(f"{i}. {doc['title']} (Score: {doc['score']})")
            print(f"URL: {doc['url']}")
            print(f"Description: {doc['description'][:200]}...")
            print(f"Scores: {doc['scores']}")
            print("-" * 50)

        # Save the results
        save_results_as_json(results, query)
