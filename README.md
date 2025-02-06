# Web Indexing - TPs

## Web Crawler - TP1 ENSAI 2025 🕸️

Ce projet implémente un crawler web en Python. Le script explore des pages web, extrait des informations clés et priorise certaines pages selon des critères définis.


## ✨ Fonctionnalités

- **Extraction des données** :
  - Titre de la page.
  - Premier paragraphe.
  - Liste des liens internes.
- **Priorisation des URLs** :
  - Priorise les liens contenant le mot-clé `product`.
- **Limitation du crawling** :
  - Arrêt après avoir visité 50 pages.
- **Respect de robots.txt** :
  - Vérifie les permissions avant de crawler une URL.
- **Stockage des résultats** :
  - Les données sont sauvegardées dans un fichier JSON structuré.


## 🛠️ Installation

1. **Cloner le dépôt** :
   ```bash
   git clone https://github.com/khadijaabattane/crawler.git
   cd crawler
   ```

2. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

3. **Exécuter le script** :
   ```bash
   python crawler.py
   ```


## 📂 Structure du projet

```plaintext
├── crawler.py   
├── results.json         
├── requirements.txt     
├── README.md            
```


## 🖥️ Pré-requis

- Bibliothèques : `requests`, `beautifulsoup4`


# Web Indexing - TP2


## 📌 Project Description
This project aims to implement an **inverted indexing system** for a set of web products, allowing fast searches on product titles, descriptions, reviews, and features.

The Python script provides the following functionalities:
- **Extract product information** from a `products.jsonl` file
- **Create an inverted index** for titles and descriptions
- **Generate positional indexes** for words in titles and descriptions
- **Build a review index** (total reviews, average rating, last rating)
- **Index product features** (brand, origin, etc.)
- **Save and load indexes** in JSON format

## 📂 Generated Files Structure
The script generates the following files in the `indexes/` directory:

| **File Name**                        | **Content** |
|--------------------------------------|------------|
| `title_index.json` | Inverted index for titles (word -> list of URLs) |
| `description_index.json` | Inverted index for descriptions (word -> list of URLs) |
| `title_positional_index.json` | Positional index for words in titles |
| `description_positional_index.json` | Positional index for words in descriptions |
| `reviews_index.json` | Review index (total reviews, average score, last score) |
| `features_index.json` | Inverted index for features (brand, origin, etc.) |

## 🛠️ Index Implementation

### 1️⃣ Inverted Index for Titles and Descriptions
- **Format:** `{ "word": ["URL1", "URL2", ...] }`
- **Purpose:** Enables quick lookup of documents containing a specific word.

### 2️⃣ Positional Index for Titles and Descriptions
- **Format:** `{ "word": { "URL": [positions] } }`
- **Purpose:** Stores word positions to facilitate proximity-based searching.

### 3️⃣ Review Index
- **Format:** `{ "URL": { "total_reviews": X, "average_score": Y, "last_score": Z } }`
- **Purpose:** Helps prioritize the highest-rated products.

### 4️⃣ Feature Index (Brand, Origin, etc.)
- **Format:** `{ "feature": { "value": ["URL1", "URL2"] } }`
- **Purpose:** Enables filtering products based on characteristics.

## 🚀 Running the Script
### 1️⃣ Install Dependencies
No external dependencies are required; Python 3 is sufficient.

### 2️⃣ Execute the Script
```bash
python indexer.py
```

### 3️⃣ Verify the Indexes
The generated JSON files are located in the `indexes/` directory.



# Search Engine for Product Indexing 🔍

## Overview
This project is a **product search engine** that leverages multiple indexing techniques and ranking algorithms to deliver relevant search results. It includes:

- **Index Loading**: Loading product data and multiple indexes (brand, description, title, etc.).
- **Text Processing**: Tokenization, stopword removal, and synonym expansion.
- **Document Filtering**: Filtering documents based on token presence.
- **Ranking**: BM25 ranking algorithm, exact match scoring, and review-based ranking.
- **Testing & Optimization**: Query testing, result analysis, and parameter adjustment.

---

## 1. 📂 **Data Loading & Preparation** 

### 📁 Loading Indexes
The **`IndexLoader`** class loads all required index files from the specified directory:

- `brand_index.json`
- `description_index.json`
- `domain_index.json`
- `origin_index.json`
- `origin_synonyms.json`
- `reviews_index.json`
- `title_index.json`

### 📖 Text Tokenization
Implemented using **regex** and the **NLTK stopwords list**. The `TextProcessor.tokenize()` function:

- Converts text to lowercase.
- Removes stopwords (using NLTK).
- Keeps only alphabetic tokens.

### 📅 Synonym Expansion
The `expand_with_synonyms()` method expands query tokens using `origin_synonyms.json`, allowing broader search capabilities (e.g., "USA" expands to "United States", "America").

---

## 2. 🔢 **Document Filtering** 

### 🔎 Query Processing
1. **Tokenization**: Splits the query into tokens.
2. **Normalization**: Converts tokens to lowercase and removes stopwords.
3. **Synonym Expansion**: Expands tokens using the synonym dictionary.

### 🔍 Filtering Documents
The **`DocumentFilter`** class filters documents based on query tokens:

- **`filter_any_token()`**: Returns documents that contain **at least one** query token.
- **`filter_all_tokens()`**: Returns documents that contain **all** query tokens.

*Note*: Stopwords are excluded from filtering.

---

## 3. 🔢 **Ranking** 

### 🔄 Analyzing Relevant Signals

1. **BM25 Score**: Measures term frequency-inverse document frequency relevance.
2. **Exact Match**: Provides a score boost if the query exactly matches a product title or brand.
3. **Review Score**: Based on product ratings and number of reviews.
4. **Title Match**: Additional weight if query tokens appear in the product title.

### 📊 Ranking Algorithm
Implemented in the **`BM25Ranker`** class:

- **`compute_bm25_score()`**: Calculates BM25 for each document.
- **`compute_final_score()`**: Combines BM25, exact match, review scores, and title matches to produce a final ranking score.

**Scoring Weights**:
- BM25: 40%
- Exact Match: Fixed bonus of 2.0
- Review Score: 30%
- Title Match: 20%

---

## 4. 🔧 **Testing & Optimization** 

### 📄 Test Queries
Sample queries for testing the search engine:

- "**Box of Chocolate Candy**"
- "**Video Potions**"
- "**Gaming Sessions**"
- "**Stainless Steel Water Bottle**"

### 🔢 Result Analysis
- **Review the ranking** of returned documents.
- **Adjust weights and parameters** in the ranking algorithm to optimize results.

### 📃 Saving Results
Results are saved in a JSON format with the following structure:

```json
{
  "metadata": {
    "query": "Box of Chocolate Candy",
    "timestamp": "2025-02-06T12:00:00Z",
    "total_documents": 100,
    "filtered_documents": 10
  },
  "results": [
    {
      "title": "Box of Chocolate Candy",
      "url": "https://web-scraping.dev/product/1",
      "description": "Delicious assorted chocolate candies perfect for gifting.",
      "scores": {
        "bm25_score": 1.2,
        "exact_match_score": 2.0,
        "review_score": 0.9,
        "final_score": 4.1
      },
      "score": 4.1
    }
  ]
}
```

### Execute the Script
```bash
python search_engine.py
```


## 📝 Authors
- **Khadija ABATTANE** - ENSAI 3A



