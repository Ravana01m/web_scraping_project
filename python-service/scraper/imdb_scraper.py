"""IMDb movie review scraper.

Refactored from the original imdb_web_scraping.ipynb notebook.
Key improvements over original:
- Uses shared create_driver from common.py (adds headless, image blocking, etc.)
- try/finally for driver.quit() (was missing in original)
- Explicit waits replace time.sleep(2) at page load
- BeautifulSoup-based extraction after page load (original used slow element-by-element Selenium)
- max_reviews parameter to stop loading when enough reviews exist
- Structured output with review_characters

Preserves original CSS selectors:
- article.user-review-item
- span.ipc-see-more__text (Load More button)
- span.ipc-rating-star--rating
- div.ipc-overflowText--children div.ipc-html-content
- button.ipc-overflowText-overlay (See more buttons within reviews)
- Voting count selectors for likes/dislikes
"""

import re
import time
import logging
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from scraper.common import create_driver, make_waits, build_review_dict

logger = logging.getLogger(__name__)


def extract_title_id(url: str) -> str:
    """Extract IMDb title ID from various URL formats.
    
    Handles:
    - https://www.imdb.com/title/tt0468569/
    - https://www.imdb.com/title/tt0468569/reviews
    - https://www.imdb.com/title/tt0468569
    
    Original notebook logic: url.strip('/').split('/')[-1]
    Enhanced to handle /reviews suffix.
    """
    url = url.strip("/")
    parts = url.split("/")

    # Handle /reviews suffix
    if parts[-1] == "reviews":
        return parts[-2]
    return parts[-1]


def scrape_imdb(url: str, max_reviews: int = 100) -> list[dict]:
    """Scrape reviews from an IMDb movie/show page.
    
    Args:
        url: IMDb title URL (e.g., https://www.imdb.com/title/tt0468569/).
        max_reviews: Maximum number of reviews to collect.
    
    Returns:
        List of review dictionaries with rating, review, review_characters, likes, dislikes.
    """
    title_id = extract_title_id(url)
    reviews_url = f"https://www.imdb.com/title/{title_id}/reviews"
    logger.info(f"Starting IMDb scrape: {reviews_url} (max: {max_reviews})")

    driver = create_driver(headless=True)
    wait_short, wait_long = make_waits(driver, short=5, long=15)

    try:
        driver.get(reviews_url)

        # FIX: Replace original time.sleep(2) with explicit wait
        try:
            wait_short.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "article.user-review-item"))
            )
        except TimeoutException:
            logger.warning("Timeout waiting for initial review elements")
            # Page might have no reviews or different structure
            try:
                wait_long.until(lambda d: d.execute_script("return document.readyState") == "complete")
            except TimeoutException:
                pass

        # Click "Load More" until we have enough reviews or no more button
        # Original selector: span.ipc-see-more__text
        retries = 0
        while retries < 50:
            # Count current reviews
            current_count = len(driver.find_elements(By.CSS_SELECTOR, "article.user-review-item"))
            if current_count >= max_reviews:
                logger.info(f"Reached target count: {current_count} >= {max_reviews}")
                break

            try:
                load_more = wait_short.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "span.ipc-see-more__text"))
                )
                driver.execute_script("arguments[0].click();", load_more)
                logger.debug("Clicked Load More...")
                time.sleep(0.3)  # Original used 0.3 delay
            except TimeoutException:
                logger.info("No more 'Load More' button")
                break
            except WebDriverException:
                retries += 1
                if retries >= 3:
                    break

        # Click "See more" buttons to expand truncated reviews (original pattern)
        # Original selector: button.ipc-overflowText-overlay
        see_more_buttons = driver.find_elements(By.CSS_SELECTOR, "button.ipc-overflowText-overlay")
        logger.info(f"Expanding {len(see_more_buttons)} 'See more' buttons...")
        for btn in see_more_buttons:
            try:
                driver.execute_script("arguments[0].click();", btn)
                time.sleep(0.1)
            except Exception:
                pass

        # IMPROVEMENT: Use BeautifulSoup instead of element-by-element Selenium extraction
        soup = BeautifulSoup(driver.page_source, "html.parser")
        wrappers = soup.select("article.user-review-item")
        logger.info(f"Found {len(wrappers)} review elements in HTML")

        reviews = []
        for wrapper in wrappers[:max_reviews]:
            # Rating: span.ipc-rating-star--rating (original selector)
            rating_elem = wrapper.select_one("span.ipc-rating-star--rating")
            rating = rating_elem.get_text(strip=True) if rating_elem else None

            # Review text: div.ipc-overflowText--children div.ipc-html-content (original selector)
            text_elem = wrapper.select_one("div.ipc-overflowText--children div.ipc-html-content")
            if not text_elem:
                # Fallback selector from original notebook
                text_elem = wrapper.select_one("div[data-testid='review-overflow']")
            review_text = text_elem.get_text(" ", strip=True) if text_elem else ""

            # Likes (original selector)
            likes_elem = wrapper.select_one(
                "span.ipc-voting__label__count.ipc-voting__label__count--up"
            )
            likes = likes_elem.get_text(strip=True) if likes_elem else None

            # Dislikes (original selector)
            dislikes_elem = wrapper.select_one(
                "span.ipc-voting__label__count.ipc-voting__label__count--down"
            )
            dislikes = dislikes_elem.get_text(strip=True) if dislikes_elem else None

            if review_text or rating:
                reviews.append(build_review_dict(
                    rating=rating,
                    review_text=review_text,
                    likes=likes,
                    dislikes=dislikes,
                ))

        logger.info(f"Extracted {len(reviews)} reviews from IMDb")
        return reviews

    finally:
        try:
            driver.quit()
        except Exception:
            pass
