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

