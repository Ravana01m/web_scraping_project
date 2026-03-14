# web_scraping_project
Project Overview

This project focuses on web scraping, data collection, and analysis of user reviews and ratings from two platforms:
Croma – Electronics product reviews
IMDb – Movie ratings and reviews
The scraped data is stored as a dataset and can be used for sentiment analysis, recommendation systems, or data analysis tasks.
The goal of this project is to demonstrate web scraping, dataset creation, and data preprocessing for machine learning or data science applications.

Features
Scrapes ratings and reviews from Croma product pages
Scrapes movie ratings and user reviews from IMDb
Stores data in structured dataset format (CSV/JSON)
Extracts important fields such as:
Review text
Rating
Product/Movie name
Reviewer name
Date of review
Ready-to-use dataset for sentiment analysis or ML models

Technologies Used
Python
BeautifulSoup
Requests
Pandas
Jupyter Notebook / Python Scripts

review-analysis-project/
│
├── data/
│   ├── croma_reviews.csv
│   └── imdb_reviews.csv
│
├── scraper/
│   ├── croma_scraper.py
│   └── imdb_scraper.py
│
├── notebooks/
│   └── analysis.ipynb
│
├── requirements.txt
└── README.md
