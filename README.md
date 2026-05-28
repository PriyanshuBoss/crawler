# Ecommerce Store Crawler

A Python-based e-commerce crawler designed to crawl Shopify stores, extract all available hyperlinks/pages, and store the collected URLs into a JSON file for further processing and analysis.

This crawler is useful for:

* Product URL collection
* Store structure analysis
* SEO research
* Marketplace data collection
* Automation workflows

---

# 🚀 Features

* Crawls Shopify e-commerce stores
* Extracts all internal hyperlinks
* Stores crawled URLs in JSON format
* Lightweight and easy to configure
* Modular crawler architecture
* Supports scalable crawling workflows

---

# 🛠️ Tech Stack

* Python
* Requests / HTTP Fetching
* JSON Data Storage

---

# 📂 Project Structure

| File                | Description                                |
| ------------------- | ------------------------------------------ |
| `config.py`         | Project configuration and crawler settings |
| `constants.py`      | Stores constants and reusable variables    |
| `fetcher.py`        | Handles fetching and crawling logic        |
| `main.py`           | Main entry point of the crawler            |
| `product_urls.json` | Stores extracted URLs in JSON format       |

---

# ⚙️ How It Works

1. The crawler starts from a Shopify store URL
2. Fetches page content
3. Extracts hyperlinks from the store
4. Filters and processes URLs
5. Stores all collected links inside `product_urls.json`

---

# 📦 Installation

Clone the repository:

```bash id="2ngl7l"
git clone <repository-url>
```

Move into the project directory:

```bash id="v4lmpf"
cd ecommerce_crawler
```

Install dependencies:

```bash id="2f6l1f"
pip install -r requirements.txt
```

---

# ▶️ Usage

Run the crawler:

```bash id="f9t8fc"
python main.py
```

After execution, all extracted URLs will be saved in:

```text id="tzv0mx"
product_urls.json
```

---

# 🔧 Configuration

Update crawler settings inside:

```text id="d0mr4w"
config.py
```

You can configure:

* Store URL
* Crawl depth
* Request settings
* Output preferences

---

# 📄 Example Output

```json id="0ol3cn"
[
  "https://store.com/products/product-1",
  "https://store.com/products/product-2",
  "https://store.com/collections/all"
]
```

---

# 🌍 Use Cases

* Shopify store analysis
* Product URL extraction
* SEO crawling
* E-commerce automation
* Data collection pipelines

---

# ⚠️ Disclaimer

This project is intended for educational and research purposes only. Ensure you comply with website terms of service and robots.txt policies before crawling any website.

---

# 🤝 Contributing

Contributions and improvements are welcome.

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Open a Pull Request

---

# 👨‍💻 Author

Developed by PriyanshuBoss
