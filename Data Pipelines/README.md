# LetsDoThisOneMoreTime

These are where my projects reside as I accrue more skills working with data! My projects usually have the category of:

* Either something I'm interested in (Pokemon)
* Something I can actually use for my daily life (Gmail)
* Something I build that actually can be used/answers an industry problem + learn new technologies (Job Common Crawl)

---

## Current featured projects:

### Into the Job-iverse

**What jobs and/or skills are still in demand across the web?**

A large-scale job listing analytics project powered by public Common Crawl data, where job descriptions are extracted and processed using real-time streaming, batch workflows, and NLP techniques.

#### Technologies Used:
* Apache Kafka for distributed streaming data ingestion
* Apache Airflow for DAG-based orchestration
* PySpark and Pandas for transformation and processing
* dbt for modular SQL transformation and lineage tracking
* Parquet format for efficient storage
* Docker for containerized environment
* Python for orchestration and NLP

---

### Across the Gmail-iverse

**What does my inbox reveal about job hunting and financial habits?**

A personal ETL pipeline that extracts, classifies, and visualizes career and financial data from Gmail using secure APIs and machine learning.

#### Technologies Used:
* Gmail API with OAuth 2.0 for secure email access
* Python and Pandas for parsing and normalization
* Scikit-learn for logistic regression and classification of job related emails
* PostgreSQL and CSV for structured data storage
* Power BI for building KPIs and progress dashboards

---

### Beyond the Card-iverse

**What really drives the price of collectible Pokémon cards?**

A market analytics dashboard that showcases trends in Pokémon TCG pricing using enriched metadata and external live data pipelines.

#### Technologies Used:
* Python and Pandas for scraping, enrichment, and data handling
* Apache Airflow for ETL scheduling and automation
* Power BI for real-time dashboard and DAX-based measures
* Data sources include PostgreSQL, CSV metadata, and external APIs (TCGPlayer, eBay)
* Slicers, filters, custom DAX measures, and interactive visuals for user-driven exploration
