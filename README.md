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

## 📝 Authors
- **Khadija ABATTANE** - ENSAI 3A
