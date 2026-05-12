# Distributed AI Research Paper Crawler

A distributed web crawler system designed to crawl and analyze AI-related research papers from arXiv using Celery, Redis, MySQL, Bloom Filters, and Streamlit.

The project demonstrates distributed task processing, intelligent prioritization, duplicate detection, database normalization, and real-time visualization through a dashboard interface .

---

# Features

- Distributed crawling architecture
- Multi-worker parallel processing
- Celery task queue system
- Redis message broker
- Bloom Filter duplicate detection
- MySQL relational database storage
- AI-paper priority scoring
- robots.txt compliant crawling delays
- Streamlit analytics dashboard
- Automatic metadata extraction
- Keyword extraction from abstracts
- Scalable modular architecture

---

# Technologies Used

## Backend
- Python
- Celery
- Redis
- MySQL

## Frontend
- Streamlit

## Web Crawling
- Requests
- BeautifulSoup4

## Data Processing
- Bloom Filter
- Pandas

---

# Project Architecture

```text
Producer
   ↓
Celery Queue (Redis Broker)
   ↓
Distributed Workers
   ↓
MySQL Database
   ↓
Streamlit Dashboard
````

---

# Workflow

## 1. Producer

The producer fetches paper listings from arXiv.

Responsibilities:

* Crawl arXiv pages
* Rotate page batches using pagination
* Detect duplicates using Bloom Filter
* Assign AI-based priority scores
* Send tasks to Celery workers

---

## 2. Celery Queue

Celery distributes crawling tasks among multiple workers.

Responsibilities:

* Distributed task scheduling
* Parallel processing
* Worker management
* Fault tolerance

Redis is used as the broker and backend.

---

## 3. Workers

Workers process individual papers.

Responsibilities:

* Fetch abstract pages
* Parse metadata
* Extract authors
* Extract subjects
* Extract keywords
* Compute statistics
* Store data into MySQL
* Respect crawl delay for robots.txt compliance

---

## 4. MySQL Database

Stores all crawled paper information using a normalized relational schema.

Tables include:

* papers
* authors
* subjects
* keywords
* paper_authors
* paper_subjects
* paper_keywords
* paper_stats

---

## 5. Streamlit Dashboard

Displays crawled research papers and analytics.

Features:

* Paper search
* AI paper filtering
* Statistics display
* Database visualization
* Priority score display

---

# Duplicate Detection

Duplicate detection is implemented using a Bloom Filter.

Advantages:

* Memory efficient
* Fast lookup
* Scalable for large datasets
* Prevents duplicate task scheduling

---

# Priority Scoring

The crawler prioritizes AI-related papers using keyword scoring.

## Strong Keywords

* LLM
* Transformer
* Deep Learning
* Neural Network

## Weak Keywords

* AI
* NLP
* Computer Vision
* Machine Learning

Lower scores indicate higher crawl priority.

---

# Database Schema

## papers

Stores main paper metadata.

## authors

Stores author names.

## subjects

Stores subject categories.

## keywords

Stores extracted abstract keywords.

## paper_authors

Many-to-many relationship between papers and authors.

## paper_subjects

Many-to-many relationship between papers and subjects.

## paper_keywords

Many-to-many relationship between papers and keywords.

## paper_stats

Stores computed paper statistics.

---

# Installation

## 1. Clone Repository

```bash
git clone <repository-url>
cd WebCrawler
```

---

## 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# MySQL Setup

## Create Database

```sql
CREATE DATABASE crawler_db;
```

## Create User

```sql
CREATE USER 'crawler_user'@'localhost'
IDENTIFIED BY 'crawler_pass';

GRANT ALL PRIVILEGES ON crawler_db.*
TO 'crawler_user'@'localhost';

FLUSH PRIVILEGES;
```

---

# Redis Setup

Start Redis server:

```bash
redis-server
```

Test Redis:

```bash
redis-cli ping
```

Expected output:

```text
PONG
```

---

# Running the Project

## 1. Start Celery Workers

```bash
celery -A scripts.celery_app.celery worker --loglevel=info --concurrency=4
```

---

## 2. Run Producer

```bash
python3 -m scripts.producer
```

---

## 3. Launch Streamlit Dashboard

```bash
streamlit run app.py
```

---

# robots.txt Compliance

The crawler respects arXiv crawling policies by:

* Introducing delays between requests
* Limiting request frequency
* Using a custom User-Agent

Each worker waits before making another request.

---

# Scalability

The architecture supports horizontal scaling.

Additional workers can be added simply by increasing Celery concurrency:

```bash
celery -A scripts.celery_app.celery worker --concurrency=8
```

---

# Future Improvements

* Persistent Bloom Filters
* Docker deployment
* Advanced NLP analysis
* Recommendation system
* Elasticsearch integration
* Real-time monitoring
* Scheduled crawling
* Citation graph analysis

---

# Example Project Structure

```text
WebCrawler/
│
├── app.py
├── requirements.txt
├── README.md
│
├── scripts/
│   ├── producer.py
│   ├── worker.py
│   ├── celery_app.py
│   ├── db.py
│   ├── utils.py
│
├── screenshots/
│
└── venv/
```

---

# Learning Outcomes

This project demonstrates:

* Distributed systems
* Task queues
* Parallel processing
* Database normalization
* Web crawling
* Duplicate detection
* Data visualization
* Backend architecture
* Scalable system design

---

# Author

Developed as a distributed systems and web crawling project focused on scalable AI research paper collection and analysis.

```
```
>>>>>>> feature/firstcrawler-vg
