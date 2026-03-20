# LetsDoThisOneMoreTime

These are where my projects reside as I accrue more skills working with data! My projects usually have the category of:

* Either something I'm interested in (Pokemon, OSRS Pipeline)
* Something I can actually use for my daily life (Gmail)
* Something I build that actually can be used/answers an industry problem (Common Crawl, OSRS Pipeline)

---

## Current featured projects:

### Gmail ETL Pipeline (Financial + Job Application Tracker) (Finished)

**What does my inbox reveal about job hunting and financial habits?**

A personal ETL pipeline that extracts, classifies, and visualizes career and financial data from Gmail using secure APIs and machine learning.

#### Technologies Used:
* Gmail API with OAuth 2.0 for secure email access
* Python and Pandas for parsing and normalization
* Scikit-learn for logistic regression and classification of job related emails
* PostgreSQL and CSV for structured data storage
* Power BI for building KPIs and progress dashboards

---

### Pokemon TCG Card Prices ETL Pipeline (Finished)

**What really drives the price of collectible Pokémon cards?**

A market analytics dashboard that showcases trends in Pokémon TCG pricing using enriched metadata and external live data pipelines.

#### Technologies Used:
* Python and Pandas for scraping, enrichment, and data handling
* Apache Airflow for ETL scheduling and orchestration
* Power BI for real-time dashboard and DAX-based measures
* Data sources include PostgreSQL, CSV metadata, and external APIs (TCGPlayer, eBay)
* Slicers, filters, custom DAX measures, and interactive visuals for user-driven exploration

---
### Old School Runescape Player Analytics Pipeline (In Progress)

**What player habits can be discerned from consistently high performing players or clan members?**

A large-scale analytics pipeline extracted from WiseOldMan API built on top of official OSRS Hiscores page, player accounts are extracted and tracked over the course of 3+ months to examine player behavior and assign anamoly scores based on player behavior. Although this pipeline does NOT label anyone as a bot, it does aim to examine and locate suspicious patterns.

#### Technologies Used:
* Snowflake for data warehousing + cloud capabilities
* Dagster for orchestration
* PySpark, Python for transformation, processing, ingestion,
* Parquet format for efficient storage
* Azure Data Lake Storage GenII for storage + cloud friendliness
* Power BI for visualizations

---

### Common Crawl ETL Pipeline (In Progress)

**What jobs and/or skills are still in demand across the web?**

A large-scale job listing analytics project powered by public Common Crawl data, where job descriptions are extracted and processed using real-time streaming, batch workflows, and NLP techniques.

#### Technologies Used:
* Docker for containerization
* Airflow for orchestration
* PySpark, Python for transformation, processing, ingestion, NLP
* dbt for modular SQL transformation and lineage tracking
* Parquet format for efficient storage
* DuckDB for storage
* Power BI for visualizations

---

