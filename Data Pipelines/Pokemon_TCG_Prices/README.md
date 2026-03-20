# LetsDoThisOneMoreTime Pokémon TCG Dashboard & ETL Pipeline

## Overview

This project is a comprehensive data analytics and visualization attempt for the Pokémon Trading Card Game (TCG). It consists of a full ETL pipeline that extracts, transforms, and loads card metadata and pricing information into a `.csv`, which is then visualized through an interactive Power BI dashboard. The data was further enriched via Python (using pandas) to add even more metadata.

The goal was to explore the growing demand in Pokémon TCG markets and discern noticeable changes in pricing and gameplay designs. 

### Conclusion(s)

The primary factors driving card pricing appear to be:
* Individual Pokémon popularity (e.g., Charizards are typically more expensive than random Pokémon)
* Card age (i.e., when the card came out)
* Card set (related to age, but not necessarily)


## Project Scope

* **ETL Pipeline**: Python-based pipeline that integrates data from static CSVs and dynamic sources (TCGPlayer, eBay scraping).
* **Data Model**: Cleaned and structured datasets supporting Power BI dashboards.
* **Dashboard**: Power BI visuals showcasing trends in card attributes, evolution chains, pricing, and more.


## Features

### Dashboard Highlights

* **Gameplay Balance Analysis**: Track average HP, retreat cost, and weaknesses by card type and generation.
* **Design Trends**: Analyze type diversity and number of attacks over time.
* **Market Behavior**: Integrate eBay pricing to analyze value distribution by rarity, artist, and type.
* **Individual Popularity**: Show pricing disparities between the most popularly sold Pokémon.
* **Artist Insights**: Discover which artists contribute most to various card types and trends.


### ETL Pipeline Highlights

#### Data Sources:
* **Static**: CSV dataset with metadata, evolution, attack stats, etc.
* **Dynamic**: Python scraper pulling current price data from eBay listings.

#### Transformations:
* Flatten nested card attributes (e.g., weaknesses).
* Clean inconsistent listing names.
* Merge eBay data on card name or ID.

#### Loading:
* Export cleaned datasets to `.csv` or `.xlsx` for Power BI ingestion.


## Technologies Used

* **Python**: Pandas, Requests, BeautifulSoup, Regex
* **Power BI**: Data modeling, DAX measures, dynamic filters, and drill-through pages
* **Data**: 
    * Pokémon TCG CSV (custom-compiled dataset)
    * eBay price scraping (via Python)

## Future Enhancements

* Scrape a different website to see various market averages (e.g., Facebook Marketplace)
* Migrate the pipeline to Dagster or Airflow for orchestration
* Store historical price tracking over time in a database