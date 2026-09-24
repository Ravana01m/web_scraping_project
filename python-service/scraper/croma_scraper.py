"""Croma product review scraper.

Refactored from the original project_web_scrape.ipynb notebook.
Preserves all original CSS selectors and XPath patterns, with improvements:
- max_reviews parameter to stop scraping when enough reviews are collected
- Structured return format with review_characters
- Proper logging instead of print statements
- Shared browser configuration from common.py
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


def click_reviews_tab(driver, wait_short, wait_long):
    """Click the reviews tab on a Croma product page.
    
    Uses the same XPath from the original notebook with translate()
    for case-insensitive matching of 'review' text.
    """
    try:
        elem = wait_short.until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//a[contains(translate(normalize-space(.), 'REVIEWS', 'reviews'), 'review')]"
            ))
        )
        driver.execute_script("arguments[0].click();", elem)
        # Wait for review items to appear (original notebook pattern)
        try:
            wait_short.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "li.list-item")
            ))
        except TimeoutException:
            try:
                wait_long.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "li.list-item")
                ))
            except TimeoutException:
                time.sleep(0.5)
        return True
    except Exception:
        logger.warning("Could not find or click reviews tab")
        return False


def repeatedly_click_load_more(driver, wait_short, max_reviews: int, max_retries: int = 100):
    """Click 'Load More' / 'View All' buttons until enough reviews are loaded.
    
    Preserves the original notebook's XPath pattern for finding load more buttons
    with translate() for case-insensitive matching.
    Improvement: stops when max_reviews reviews are visible.
    """
    retries = 0
    prev_count = 0

    while retries < max_retries:
        reviews = driver.find_elements(
            By.CSS_SELECTOR,
            "li.list-item, div#reviewContainer div.bv-content-item"
        )
        curr_count = len(reviews)

        # Stop if we have enough reviews
        if curr_count >= max_reviews:
            logger.info(f"Reached target review count: {curr_count} >= {max_reviews}")
            break

        # Original XPath pattern from notebook for finding load more buttons
        buttons = driver.find_elements(
            By.XPATH,
            "//a[contains(translate(., 'LOAD MOREVIEW ALLREVIEWS', 'load moreview allreviews'), 'load more') or "
            "contains(translate(., 'VIEW ALL', 'view all'), 'view all') or "
            "contains(translate(., 'VIEW ALL REVIEWS', 'view all reviews'), 'view all reviews')] | "
            "//button[contains(translate(., 'LOAD MOREVIEW ALLREVIEWS', 'load moreview allreviews'), 'load more') or "
            "contains(., 'View All')]"
        )

        if not buttons:
            logger.info("No more load buttons found")
            break

        btn = buttons[0]
        if not (btn.is_displayed() and btn.is_enabled()):
            logger.info("Button not clickable anymore")
            break

        try:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            driver.execute_script("arguments[0].click();", btn)
        except WebDriverException:
            logger.debug("JS click failed, trying fallback")
            driver.execute_script("""
                const el = Array.from(document.querySelectorAll('a,button'))
                    .find(x => /(view\\s*all\\s*reviews|view\\s*all|load\\s*more)/i.test(x.textContent));
                if(el) el.click();
            """)

        try:
            wait_short.until(lambda d: len(d.find_elements(
                By.CSS_SELECTOR,
                "li.list-item, div#reviewContainer div.bv-content-item"
            )) > curr_count)
            prev_count = curr_count
            retries = 0
        except TimeoutException:
            retries += 1
            logger.debug(f"No new reviews loaded, retry: {retries}")

    final_count = len(driver.find_elements(
        By.CSS_SELECTOR,
        "li.list-item, div#reviewContainer div.bv-content-item"
    ))
    logger.info(f"Final review element count on page: {final_count}")


def extract_reviews_from_soup(soup, max_reviews: int) -> list[dict]:
    """Extract reviews from BeautifulSoup-parsed HTML.
    
    Preserves original CSS selectors from notebook:
    - li.list-item for review containers
    - div.cp-rating.user-review-rating for rating
    - div.desc.user-reviews-descr for review text
    With fallback selectors for alternative layouts.
    """
    reviews = []
    for li in soup.select("li.list-item"):
        if len(reviews) >= max_reviews:
            break

        # Original selectors from notebook
        rating_div = li.select_one("div.cp-rating.user-review-rating")
        rating_text = rating_div.get_text(" ", strip=True) if rating_div else ""
        rating_match = re.search(r"\(?\b(\d+(?:\.\d+)?)\b\)?", rating_text)
        rating = rating_match.group(1) if rating_match else None

        review_div = li.select_one("div.desc.user-reviews-descr")
        if not review_div:
            review_div = li.select_one(".review-text, .review-body, [itemprop='reviewBody']")

        if review_div:
            raw_text = review_div.get_text(" ", strip=True)
            review_text = re.sub(r"\s+", " ", raw_text)
        else:
            review_text = ""

        if review_text:
            reviews.append(build_review_dict(rating=rating, review_text=review_text))

    return reviews


def try_extract_from_iframes(driver, max_reviews: int) -> list[dict]:
    """Check iframes for review content.
    
    Preserves original notebook's iframe handling pattern.
    Some Croma pages load reviews in iframes.
    """
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    for idx, iframe in enumerate(iframes):
        try:
            driver.switch_to.frame(iframe)
            inner = driver.page_source
            if "list-item" in inner or "review" in inner.lower():
                soup = BeautifulSoup(inner, "html.parser")
                items = soup.select("li.list-item")
                if items:
                    driver.switch_to.default_content()
                    return extract_reviews_from_soup(soup, max_reviews)
            driver.switch_to.default_content()
        except Exception:
            try:
                driver.switch_to.default_content()
            except Exception:
                pass
            continue
    return []


def scrape_croma(url: str, max_reviews: int = 100) -> list[dict]:
    """Scrape reviews from a Croma product page.
    
    Args:
        url: Full Croma product URL.
        max_reviews: Maximum number of reviews to collect.
    
    Returns:
        List of review dictionaries with rating, review, review_characters, likes, dislikes.
    """
    logger.info(f"Starting Croma scrape: {url} (max: {max_reviews})")
    driver = create_driver(headless=True)
    wait_short, wait_long = make_waits(driver, short=5, long=15)

    try:
        driver.get(url)

        # Wait for page ready (original notebook pattern)
        try:
            wait_short.until(lambda d: d.execute_script("return document.readyState") in ("interactive", "complete"))
        except TimeoutException:
            time.sleep(0.5)

        # Try clicking the reviews tab
        clicked = click_reviews_tab(driver, wait_short, wait_long)
        if not clicked:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(0.4)
            clicked = click_reviews_tab(driver, wait_short, wait_long)

        # Load more reviews
        repeatedly_click_load_more(driver, wait_short, max_reviews, max_retries=12)

        # Try iframe first (original notebook pattern)
        soup_from_iframe = try_extract_from_iframes(driver, max_reviews)
        if soup_from_iframe:
            reviews = soup_from_iframe
        else:
            # Parse main page
            soup = BeautifulSoup(driver.page_source, "html.parser")
            reviews = extract_reviews_from_soup(soup, max_reviews)

        # Fallback: find elements with 'review' in class names (from original notebook)
        if not reviews:
            logger.warning("No reviews found with primary selectors, trying fallback")
            soup_all = BeautifulSoup(driver.page_source, "html.parser")
            fallback_items = [
                tag for tag in soup_all.find_all(True)
                if "review" in " ".join(tag.get("class", [])).lower()
            ]
            for tag in fallback_items[:max_reviews]:
                txt = tag.get_text(" ", strip=True)
                txt = re.sub(r"\s+", " ", txt)
                if len(txt) > 20:
                    reviews.append(build_review_dict(rating=None, review_text=txt))

        logger.info(f"Extracted {len(reviews)} reviews from Croma")
        return reviews

    finally:
        try:
            driver.quit()
        except Exception:
            pass
