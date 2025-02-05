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





---

### **🚀 TP3: Search Engine Using Indexing and Ranking**

# 📌 **Search Engine for Indexed Product Data**
This project is a **fast and efficient search engine** designed to query indexed product data. It supports:
- **Spelling correction** 📝
- **Query expansion using synonyms** 🔄
- **BM25 ranking for relevance** 📊
- **Parallelized search for speed** ⚡
- **Query history logging** 🗂️
- **Auto-suggestions for queries** 💡

---

## **📖 1️⃣ Use Cases & Features Implemented**
This search engine addresses multiple challenges commonly found in **text-based information retrieval systems**.

| **Feature** | **Problem Solved** | **Solution Implemented** |
|------------|------------------|----------------------|
| **Indexing** | Fast document lookup | Created **inverted indexes** for title, description, brand, origin, reviews, and domain |
| **Tokenization** | Normalize user input | Applied **NLTK stopwords filtering + punctuation removal** |
| **Spelling Correction** | Handle typos | Used **TextBlob correction** & **Fuzzy Matching** with `rapidfuzz` |
| **Query Expansion** | Improve recall with synonyms | Used **synonym mapping** (origin-based synonyms from `origin_synonyms.json`) |
| **Ranking (BM25)** | Prioritize most relevant results | Implemented **precomputed TF-IDF and BM25 scoring** |
| **Parallel Processing** | Speed up searches | Used **multithreading** (`threading.Thread`) for search execution |
| **Query Logging** | Maintain search history | Saved **all queries & results** in `query_history.json` |
| **Auto-suggestions** | Help users with queries | Built a **Trie-based suggestion system** for fast lookup |

---

## **🛠️ 2️⃣ Installation & Setup**
### **🔹 Install Dependencies**
This project uses Python 3 and requires some external libraries. Install them using:
```sh
pip install nltk textblob rapidfuzz
```

> 🛠️ **Note**: You may need to download the **NLTK stopwords**:
```python
import nltk
nltk.download('stopwords')
```

---

## **💡 3️⃣ How It Works**
### **🔎 Search Process**
1. **User enters a search query** (e.g., `"choco"`)
2. **Spelling correction is applied** (e.g., `"chocolate"`)
3. **Query expansion happens** (if applicable)
4. **Tokenization removes stopwords** (e.g., `"the best chocolate"` → `["chocolate"]`)
5. **Parallelized search runs**:
   - Looks up words in **title, description, brand, origin, and reviews**
   - Applies **BM25 ranking** to score results
6. **Results are sorted** by **relevance score**
7. **Results are displayed in the terminal** & **logged in `query_history.json`**

---

## **🖥️ 4️⃣ Usage**
### **Run the Search Engine**
To start the search engine:
```sh
python search_engine.py
```
You will be prompted to enter a query:
```
🔍 Enter your search query: chocolate
```

### **Example Terminal Output**
```
🔎 **Suggestions:** ['chocolate']

🔍 **Final Tokenized Query:** ['chocolate']

🔍 **Search Results:**

📌 **Product:** Box Of Chocolate Candy
🔗 URL: https://web-scraping.dev/product/1
⭐ Score: 15.2
🎯 Matches: Title match: chocolate, Review score: 4.5 (Total reviews: 12)

📌 **Product:** Dark Chocolate Bar
🔗 URL: https://web-scraping.dev/product/3
⭐ Score: 12.8
🎯 Matches: Title match: chocolate, Review score: 4.2 (Total reviews: 8)

✅ Query and results saved to `query_history.json`
```

---

## **📂 5️⃣ Query History Logging**
Each search is saved in `query_history.json`:
```json
[
    {
        "query": "chocolate candy",
        "metadata": {
            "total_documents": 156,
            "filtered_documents": 2
        },
        "results": [
            {
                "title": "Box of Chocolate Candy",
                "url": "https://web-scraping.dev/product/1",
                "description": "Indulge your sweet tooth...",
                "score": 15.2,
                "matches": ["Title match: chocolate", "Review score: 4.5"]
            }
        ]
    }
]
```

-


 

---

## **📜 8️⃣ Full Project Structure**
```
📂 search-engine
│── 🔹 search_engine.py    
│── 🔹 title_index.json    
│── 🔹 description_index.json  
│── 🔹 reviews_index.json  
│── 🔹 origin_index.json   
│── 🔹 brand_index.json    
│── 🔹 domain_index.json   
│── 🔹 origin_synonyms.json 
│── 🔹 query_history.json  
│── 🔹 README.md           
```

---
## 📝 Authors
- **Khadija ABATTANE** - ENSAI 3A


