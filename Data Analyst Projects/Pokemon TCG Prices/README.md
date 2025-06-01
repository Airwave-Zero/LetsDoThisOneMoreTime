Pokemon TCG API Dashboard and ETL Pipeline
#LetsDoThisOneMoreTime Pokémon TCG Dashboard & ETL Pipeline

Overview
===============
This project is a comprehensive data analytics and visualization attempt for the Pokémon Trading Card Game (TCG). It consists of a full ETL pipeline that extracts, transforms, and loads card metadata and pricing information into a .csv, which is then visualized through an interactive Power BI dashboard. The data was then enriched further via Python (using pandas) to get even more metadata.
The goal was to explore the growing demand in Pokemon TCG markets, and discern noticeable changes in pricing and gameplay designs.

The conclusion(s) seem to be that the most important factors for pricing are:
Individual Pokmemon Popularity (e.g. Carizards are typically more expensive than almost any random Pokemon)
Card Condition
Card Age (i.e. when the card came out)

Project Scope
===============
ETL Pipeline: Python-based pipeline that integrates data from static CSVs and dynamic sources (eBay scraping).
Data Model: Cleaned and structured datasets supporting Power BI dashboards.
Dashboard: Power BI visuals showcasing trends in card attributes, evolution chains, pricing, and more.

Features
===============
Dashboard Highlights

Gameplay Balance Analysis: Track average HP, retreat cost, and weaknesses by card type and generation.
Design Trends: Analyze type diversity, number of attacks over time
Market Behavior: Integrate eBay pricing to analyze value distribution by rarity, artist, and type.
Individual Popularity: Show pricing disparities between most popularly sold Pokemon
Artist Insights: Discover which artists contribute most to various card types and trends.

ETL Pipeline Highlights
===============
Data Sources:
Static: CSV dataset with metadata, evolution, attack stats, etc.
Dynamic: Python scraper pulling current price data from eBay listings.

Transformations:
Flatten nested card attributes (e.g. weaknesses).
Clean inconsistent listing names
Merge eBay data on card name or ID.

Loading:
Export cleaned datasets to .csv or .xlsx for Power BI ingestion.

Technologies Used
=================
Python: Pandas, Requests, BeautifulSoup, Regex
Power BI: Data modeling, DAX measures, dynamic filters, and drill-through pages
Data:
Pokémon TCG CSV (custom-compiled dataset)
eBay price scraping (via Python)

Pipeline Structure
===============
eBayCardPrices/ contains price listings .csvs for the top 25 Pokemon featured in the project
eBay_Script.py handles the entire process of connecting to eBay, parsing the BeautifulSoup, extracting and normalizing the prices, and exporting to .csv/dataframe for PowerBI usage
pkmn_tcg_data.pbix and .pdf show the actual visualizations
TCG_Artist_Script.py groups and summarizes the artist counts of all of the cards in the database
TCG_Script handles looking up prices of all cards and the various rarities on the official TCGPlayer API


Future Enhancements
===============
Scrape a different website to see various market averages (e.g. Facebook Marketplace)
Migrate the pipeline to Dagster or Airflow for orchestration.
Store historical price tracking over time in a database.