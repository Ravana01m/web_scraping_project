import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from scraper.croma_scraper import scrape_croma
from scraper.imdb_scraper import scrape_imdb
from analysis.review_analyzer import analyze_reviews
from analysis.summarizer import generate_summary

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="Review Intelligence API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScrapeRequest(BaseModel):
    platform: str
    url: str
    max_reviews: int = 100

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/scrape")
def scrape_and_analyze(request: ScrapeRequest):
    logger.info(f"Received scrape request for {request.platform}: {request.url}")
    try:
        reviews = []
        if request.platform.lower() == "croma":
            reviews = scrape_croma(request.url, request.max_reviews)
        elif request.platform.lower() == "imdb":
            reviews = scrape_imdb(request.url, request.max_reviews)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported platform: {request.platform}")

        analysis = analyze_reviews(reviews)
        summary = generate_summary(reviews)

        return {
            "reviews": reviews,
            "totalReviews": analysis.get("totalReviews", 0),
            "averageRating": analysis.get("averageRating", 0.0),
            "ratingDistribution": analysis.get("ratingDistribution", {}),
            "sentiment": analysis.get("sentiment", {}),
            "summary": summary
        }
    except Exception as e:
        logger.error(f"Error during scrape: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
