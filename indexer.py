import json
import re
import string
import os
from collections import defaultdict

# Set of stopwords to remove common words that do not contribute to search relevance
STOPWORDS = set("""
a an and are as at be but by for if in into is it no not of on or such that the their then there these they this to was will with
""".split())

def load_data(filepath):
    """
    Reads a JSONL file and loads its content into a list of dictionaries.

    Args:
        filepath (str): Path to the JSONL file.

    Returns:
        list: A list of dictionaries representing the product data.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return [json.loads(line) for line in f]

def extract_product_info(url):
    """
    Extracts the product ID and variant from a given product URL.

    Args:
        url (str): The URL of the product.

    Returns:
        tuple: A tuple containing the product ID (str) and the variant (str or None).
    """
    match = re.search(r'/product/(\d+)(?:\?variant=(.*))?', url)
    if match:
        return match.group(1), match.group(2)
    return None, None

def tokenize(text):
    """
    Tokenizes a given text by:
    - Lowercasing the text.
    - Removing punctuation.
    - Splitting the text into words.
    - Removing stopwords.

    Args:
        text (str): The input text.

    Returns:
        list: A list of meaningful tokens extracted from the text.
    """
    text = text.lower().translate(str.maketrans('', '', string.punctuation))
    tokens = text.split()
    return [token for token in tokens if token not in STOPWORDS]

def create_inverted_index(data, field):
    """
    Builds an inverted index mapping tokens from a specific field to the URLs of the documents containing them.

    Args:
        data (list): List of product dictionaries.
        field (str): The field to index (e.g., "title", "description").

    Returns:
        dict: An inverted index where keys are tokens and values are lists of document URLs.
    """
    index = defaultdict(list)
    for doc in data:
        tokens = tokenize(doc.get(field, ''))
        for token in tokens:
            if doc['url'] not in index[token]:  # Avoid duplicates
                index[token].append(doc['url'])
    return index

def create_positional_index(data, field):
    """
    Builds a positional index storing the position of each token in a given field.

    Args:
        data (list): List of product dictionaries.
        field (str): The field to index (e.g., "title", "description").

    Returns:
        dict: A dictionary where keys are tokens, and values are dictionaries mapping URLs to token positions.
    """
    index = defaultdict(lambda: defaultdict(list))
    for doc in data:
        tokens = tokenize(doc.get(field, ''))
        for pos, token in enumerate(tokens):
            index[token][doc['url']].append(pos)
    return index

def create_reviews_index(data):
    """
    Builds an index containing review statistics for each product.

    Args:
        data (list): List of product dictionaries.

    Returns:
        dict: A dictionary where keys are product URLs, and values contain:
            - total_reviews (int): Number of reviews.
            - average_score (float or None): Average rating of the product.
            - last_score (int or None): Last recorded review rating.
    """
    index = {}
    for doc in data:
        reviews = doc.get('product_reviews', [])
        ratings = [review.get('rating', 0) for review in reviews if 'rating' in review]
        if ratings:
            index[doc['url']] = {
                'total_reviews': len(ratings),
                'average_score': round(sum(ratings) / len(ratings), 2),
                'last_score': ratings[-1]
            }
        else:
            index[doc['url']] = {
                'total_reviews': 0,
                'average_score': None,
                'last_score': None
            }
    return index

def create_features_index(data):
    """
    Builds an inverted index for product features such as brand and origin.

    Args:
        data (list): List of product dictionaries.

    Returns:
        dict: A dictionary where keys are feature names, and values are dictionaries mapping feature values to product URLs.
    """
    index = defaultdict(lambda: defaultdict(list))
    for doc in data:
        for feature, value in doc.get('product_features', {}).items():
            value = value.lower()
            if doc['url'] not in index[feature][value]:  # Avoid duplicates
                index[feature][value].append(doc['url'])
    return index

def save_index(index, filepath):
    """
    Saves an index as a JSON file.

    Args:
        index (dict): The index to save.
        filepath (str): The path to the output file.
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=4)

def load_index(filepath):
    """
    Loads an index from a JSON file.

    Args:
        filepath (str): The path to the JSON file.

    Returns:
        dict: The loaded index.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    """
    Main function that orchestrates the indexing process:
    - Loads product data.
    - Extracts product IDs and variants.
    - Creates various indexes (inverted, positional, review, and feature indexes).
    - Saves all indexes to JSON files.
    """
    filepath = 'products.jsonl'  # Update this path if needed
    data = load_data(filepath)
    
    # Extract product IDs and variants
    for doc in data:
        doc['product_id'], doc['variant'] = extract_product_info(doc['url'])
    
    # Generate indexes
    title_index = create_inverted_index(data, 'title')
    description_index = create_inverted_index(data, 'description')
    title_positional_index = create_positional_index(data, 'title')
    description_positional_index = create_positional_index(data, 'description')
    reviews_index = create_reviews_index(data)
    features_index = create_features_index(data)
    
    # Save indexes
    os.makedirs("indexes", exist_ok=True)
    save_index(title_index, "indexes/title_index.json")
    save_index(description_index, "indexes/description_index.json")
    save_index(title_positional_index, "indexes/title_positional_index.json")
    save_index(description_positional_index, "indexes/description_positional_index.json")
    save_index(reviews_index, "indexes/reviews_index.json")
    save_index(features_index, "indexes/features_index.json")
    
    print("Indexing completed successfully!")

if __name__ == "__main__":
    main()
