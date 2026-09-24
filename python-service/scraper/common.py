"""Shared browser configuration and utilities for all scrapers."""

import os
import re
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)


def create_driver(headless: bool = True, disable_images: bool = True, page_load_strategy: str = "eager"):
    """Create a configured Chrome WebDriver instance.
    
    Reuses the optimized configuration from the original Croma scraper notebook:
    - Headless mode for server deployment
    - Disabled images and notifications for performance
    - Eager page load strategy
    - Anti-detection user agent
    - Docker-compatible flags (no-sandbox, disable-dev-shm-usage)
    
    Args:
        headless: Run browser without visible window.
        disable_images: Block image loading for faster scraping.
        page_load_strategy: 'eager', 'normal', or 'none'.
    
    Returns:
        Configured Chrome WebDriver instance.
    """
    logger.info("Creating WebDriver instance")
    chrome_options = Options()

    # Core stability flags (from original notebook)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

    if headless:
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--window-size=1920,1080")

    # Performance: disable images and notifications (from original notebook)
    if disable_images:
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.notifications": 2,
        }
        chrome_options.add_experimental_option("prefs", prefs)

    chrome_options.page_load_strategy = page_load_strategy

    # Anti-detection user agent (from original notebook)
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    # Docker support: allow custom Chrome/ChromeDriver paths
    chrome_bin = os.environ.get("CHROME_BIN")
    if chrome_bin:
        chrome_options.binary_location = chrome_bin

    chromedriver_path = os.environ.get("CHROMEDRIVER_PATH")
    if chromedriver_path:
        service = Service(chromedriver_path)
    else:
        service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(1)
    return driver


def make_waits(driver, short: int = 5, long: int = 15):
    """Create short and long WebDriverWait instances.
    
    Args:
        driver: WebDriver instance.
        short: Timeout in seconds for short waits.
        long: Timeout in seconds for long waits.
    
    Returns:
        Tuple of (short_wait, long_wait) WebDriverWait instances.
    """
    return WebDriverWait(driver, short), WebDriverWait(driver, long)


def normalize_review_text(text: str) -> str:
    """Clean and normalize review text while preserving all characters.
    
    Collapses multiple whitespace into single spaces but preserves
    all original characters including punctuation, emojis, etc.
    
    Args:
        text: Raw review text.
    
    Returns:
        Cleaned review text.
    """
    return re.sub(r"\s+", " ", text).strip()


def build_review_dict(
    rating: str | None,
    review_text: str,
    likes: str | None = None,
    dislikes: str | None = None,
) -> dict:
    """Build a standardized review dictionary with character-wise representation.
    
    CRITICAL: Uses list(review_text) to create character array.
    This preserves spaces, punctuation, emojis, numbers, special characters,
    capitalization, and character order.
    
    Args:
        rating: Rating value as string (e.g., "5", "4.5") or None.
        review_text: The review text content.
        likes: Number of likes as string or None.
        dislikes: Number of dislikes as string or None.
    
    Returns:
        Dictionary with rating, review, review_characters, likes, dislikes.
    """
    cleaned_text = normalize_review_text(review_text) if review_text else ""
    return {
        "rating": rating,
        "review": cleaned_text,
        "review_characters": list(cleaned_text),  # list(review), NOT split()
        "likes": likes,
        "dislikes": dislikes,
    }
