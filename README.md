# ArticleScraper

Django application for scraping articles from web pages using Selenium, with REST API for accessing scraped data.

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
  - [Using pip](#using-pip)
  - [Using uv (recommended)](#using-uv-recommended)
- [Configuration](#configuration)
  - [Environment Variables for Localhost](#environment-variables-for-localhost)
  - [Environment Variables for Docker](#environment-variables-for-docker)
- [Running the Project](#running-the-project)
  - [Localhost Development](#localhost-development)
  - [Docker Development](#docker-development)
- [Using the Scraper](#using-the-scraper)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Assumptions and Limitations](#assumptions-and-limitations)

---

<a id="features"></a>
## 🚀 Features

- **Web Scraping**: Extracts articles from web pages using Selenium (supports JavaScript-rendered content)
- **Date Parsing**: Intelligent date extraction supporting:
  - ISO 8601 formats
  - Polish and English textual dates (e.g., "10 września 2024", "12 November 2023")
  - Relative dates (e.g., "3 hours ago", "2 godziny temu")
  - Meta tags (article:published_time, og:published_time)
- **REST API**: Browse and filter scraped articles
- **Duplicate Prevention**: Automatically skips already scraped URLs
- **Error Handling**: Detects and skips 404/500 error pages

---

<a id="tech-stack"></a>
## 🛠 Tech Stack

- **Python 3.14+**
- **Django 5.2+**
- **Django REST Framework**
- **PostgreSQL**
- **Selenium** with Chrome/Chromium
- **Beautiful Soup 4** for HTML parsing
- **dateparser** for intelligent date parsing
- **Docker & Docker Compose** for containerization

---

<a id="installation"></a>
## 📦 Installation

### Prerequisites

- Python 3.14+
- PostgreSQL
- Chrome/Chromium browser (for local development)

### Using pip

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Samekmat/article-scraper.git
   cd ArticleScraper
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # or
   .venv\Scripts\activate  # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Using uv (recommended)

1. **Install uv** (if not already installed):
   ```bash
   # Linux/Mac
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   
   # Or using pip
   pip install uv
   ```

2. **Clone the repository:**
   ```bash
   git clone https://github.com/Samekmat/article-scraper.git
   cd ArticleScraper
   ```

3. **Create virtual environment and install dependencies:**
   ```bash
   uv venv
   source .venv/bin/activate  # Linux/Mac
   # or
   .venv\Scripts\activate  # Windows
   
   uv sync
   ```

4. **Add new packages (if needed):**
   ```bash
   uv add package-name
   ```

---

<a id="configuration"></a>
## ⚙️ Configuration

### Environment Variables for Localhost

Create a \`.env\` file in the project root:

```env
# PostgreSQL Database Configuration
DB_NAME=article_db
DB_USER=article_user
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432

# Django Secret Key
# Generate: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
SECRET_KEY=your-secret-key-here

# Selenium Configuration (Local Mode)
REMOTE_SELENIUM=false

# Optional: Custom Chrome binary path
# CHROME_BINARY=/usr/bin/chromium
```

### Environment Variables for Docker

For Docker, create a \`.env\` file with these settings:

```env
# PostgreSQL Database Configuration (Docker)
DB_NAME=article_db
DB_USER=article_user
DB_PASSWORD=yourpassword
DB_HOST=db  # Docker service name
DB_PORT=5432

# Django Secret Key
SECRET_KEY=your-secret-key-here

# Selenium Configuration (Remote Mode)
REMOTE_SELENIUM=true
SELENIUM_URL=http://selenium:4444/wd/hub

# Chrome binary for Docker
CHROME_BINARY=/usr/bin/chromium
```

**Note:** You can use \`.env.dist\` as a template - copy it to \`.env\` and update values.

---

<a id="running-the-project"></a>
## 🏃 Running the Project

### Localhost Development

1. Ensure database is available and .env is configured.
- Create a PostgreSQL database and user that match values in your .env.
- You can use any tool you prefer
- Example .env keys: DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD.

2. Apply migrations:
```bash
python manage.py migrate
```

3. Run development server:
```bash
python manage.py runserver
```

4. Access the application:
- API: http://localhost:8000/api/articles/
- Admin: http://localhost:8000/admin/

### Docker Development

1. Build and start containers:
```bash
docker-compose up --build
```

2. View logs:
```bash
docker-compose logs -f
# or only the web service
# docker-compose logs -f web
```

3. Apply database migrations:
```bash
docker-compose exec web python manage.py migrate
```

4. Run tests:
```bash
docker-compose exec web python manage.py test
```

5. Run scraper:
```bash
# Without arguments: scrapes 4 predefined task URLs
docker-compose exec web python manage.py scrape_articles

# With URLs (positional)
docker-compose exec web python manage.py scrape_articles https://example.com/a https://example.com/b

# Or with --urls flag
docker-compose exec web python manage.py scrape_articles --urls https://example.com/a https://example.com/b
```

6. Stop and remove containers:
```bash
docker-compose down
# Remove volumes (⚠️ deletes database data)
# docker-compose down -v
```

---

<a id="using-the-scraper"></a>
## 🕷 Using the Scraper

### Scrape Articles Command

The scraper is a Django management command. You can:
- run it with no arguments to scrape 4 predefined task URLs, or
- pass URLs as positional arguments, or
- pass URLs with the --urls flag.

```bash
# 1) No arguments → scrapes 4 predefined task URLs
python manage.py scrape_articles

# 2) Positional URLs
python manage.py scrape_articles https://example.com/article1 https://example.com/article2

# 3) Using --urls flag
python manage.py scrape_articles --urls https://example.com/article1 https://example.com/article2

# Docker variants
docker-compose exec web python manage.py scrape_articles
docker-compose exec web python manage.py scrape_articles https://example.com/article1 https://example.com/article2
docker-compose exec web python manage.py scrape_articles --urls https://example.com/article1 https://example.com/article2
```

### What the Scraper Does

1. ✅ Checks if URL already exists (skips duplicates)
2. ✅ Loads page with Selenium (waits for JavaScript)
3. ✅ Extracts title, content, and publication date
4. ✅ Parses dates in multiple formats (Polish/English)
5. ✅ Detects and skips error pages (404, 500)
6. ✅ Handles timeouts and network errors
7. ✅ Saves article to database
8. ✅ Logs all operations to \`scraper.log\`

### Scraper Logs

Check scraper activity:
```bash
tail -f scraper.log
```

---

<a id="api-endpoints"></a>
## 🌐 API Endpoints

### Base URL
```
http://localhost:8000/api/
```

### 1. List All Articles

**Endpoint:** `GET /api/articles/`

**Description:** Returns list of all scraped articles

**Example Request:**
```bash
curl http://localhost:8000/api/articles/
```

**Example Response:**
```json
[
  {
    "id": 1,
    "title": "Example Article Title",
    "html_content": "<html>...</html>",
    "plain_text_content": "Article text content...",
    "source_url": "https://example.com/article",
    "published_at": "2025-10-17T00:00:00",
    "source_domain": "example.com"
  },
  {
    "id": 2,
    "title": "Another Article",
    "html_content": "<html>...</html>",
    "plain_text_content": "More content...",
    "source_url": "https://site2.com/news",
    "published_at": "2025-10-16T00:00:00",
    "source_domain": "site2.com"
  }
]
```

### 2. Filter Articles by Source Domain

**Endpoint:** `GET /api/articles/?source=<domain>`

**Description:** Returns articles from specific domain

**Example Request:**
```bash
curl http://localhost:8000/api/articles/?source=example.com
```

**Example Response:**
```json
[
  {
    "id": 1,
    "title": "Example Article Title",
    "html_content": "<html>...</html>",
    "plain_text_content": "Article text content...",
    "source_url": "https://example.com/article",
    "published_at": "2025-10-17T00:00:00",
    "source_domain": "example.com"
  }
]
```

### 3. Get Single Article

**Endpoint:** `GET /api/articles/<id>/`

**Description:** Returns details of a specific article

**Example Request:**
```bash
curl http://localhost:8000/api/articles/1/
```

**Example Response:**
```json
{
  "id": 1,
  "title": "Example Article Title",
  "html_content": "<html>...</html>",
  "plain_text_content": "Article text content...",
  "source_url": "https://example.com/article",
  "published_at": "2025-10-17T00:00:00",
  "source_domain": "example.com"
}
```

**Error Response (404):**
```json
{
  "detail": "Not found."
}
```

### API Notes

- ✅ **Read-only API**: Only GET requests are supported (no POST, PUT, DELETE)
- ✅ **Pagination**: Not implemented (returns all results)
- ✅ **Authentication**: Not required (public API)
- ✅ **Content-Type**: \`application/json\`

---

<a id="testing"></a>
## 🧪 Testing

### Run All Tests

```bash
# Localhost
python manage.py test

# Docker
docker-compose exec web python manage.py test
```

---

<a id="project-structure"></a>
## 📁 Project Structure

```text
ArticleScraper/
├── api/                          # REST API app
│   ├── migrations/
│   ├── tests/
│   │   └── test_api.py           # API endpoint tests
│   ├── serializers.py            # DRF serializers
│   ├── urls.py                   # API URL routing
│   └── views.py                  # API views
├── articles/                     # Main articles app
│   ├── management/
│   │   └── commands/
│   │       └── scrape_articles.py  # Scraper command
│   ├── migrations/
│   ├── tests/
│   │   ├── test_models.py        # Model tests
│   │   └── test_scraper.py       # Scraper tests
│   ├── models.py                 # Article model
│   ├── scraper.py                # Scraping logic
│   └── views.py
├── ArticleScraper/               # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── .env                          # Environment variables (not in git)
├── .env.dist                     # Environment template
├── .gitignore                    # Gitignore file
├── docker-compose.yml            # Docker Compose config
├── Dockerfile                    # Docker image definition
├── manage.py                     # Django management script
├── pyproject.toml                # uv dependencies
├── requirements.txt              # pip dependencies
├── scraper.log                   # Scraper logs (not in git)
├── README.md                     # This file
└── uv.lock                       # uv lock file
```

---
<a id="assumptions-and-limitations"></a>
## ⚠️ Assumptions and Limitations

### Assumptions

1. **PostgreSQL Database**: Project assumes PostgreSQL
2. **Chrome/Chromium**: Selenium requires Chrome or Chromium browser
3. **JavaScript Support**: Uses Selenium for JS-rendered content
4. **Date Normalization**: All dates stored as midnight (00:00:00) if time is not specified
5. **UTF-8 Encoding**: Assumes UTF-8 for all scraped content
6. **Read-Only API**: API only supports GET requests

### Limitations

1. **No Pagination**: API returns all results (may be slow for large datasets)
2. **No Rate Limiting**: No protection against API abuse
3. **No Authentication**: API is public (no user permissions)
4. **Single Scraper Instance**: No parallel/distributed scraping
5. **Timeout Fixed**: 20-second page load timeout (hardcoded)
6. **Error Detection Heuristics**: Uses keywords for 404/500 detection (may have false positives)
7. **Date Parsing**: May fail for uncommon date formats
8. **Content Length Check**: Pages < 200 characters rejected (may exclude legitimate short pages)
9. **No Retry Logic**: Failed scrapes are not retried automatically
10. **No Content Deduplication**: Only URL-based duplicate detection

### Known Issues

- **Selenium Memory**: Chrome instances may consume significant memory
- **Docker Network**: Requires proper network configuration for Selenium Grid
- **Logging**: All logs go to \`scraper.log\` (may grow large over time)

---
