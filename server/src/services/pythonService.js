/**
 * Service to interact with the Python scraping backend
 */

const PYTHON_SERVICE_URL = process.env.PYTHON_SERVICE_URL || 'http://localhost:8000';

/**
 * Calls the Python scraper
 * @param {Object} params
 * @param {string} params.platform
 * @param {string} params.url
 * @param {number} params.maxReviews
 * @returns {Promise<Object>}
 */
const callPythonScraper = async ({ platform, url, maxReviews }) => {
    const controller = new AbortController();
    // 5 minutes timeout
    const timeoutId = setTimeout(() => controller.abort(), 5 * 60 * 1000);

    try {
        const response = await fetch(`${PYTHON_SERVICE_URL}/scrape`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                platform,
                url,
                max_reviews: maxReviews
            }),
            signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
            let errorMsg = `Python service returned status ${response.status}`;
            try {
                const errData = await response.json();
                if (errData.detail) errorMsg = errData.detail;
            } catch (e) {
                // Ignore JSON parsing error on failure
            }
            throw new Error(errorMsg);
        }

        return await response.json();
    } catch (error) {
        clearTimeout(timeoutId);
        if (error.name === 'AbortError') {
            throw new Error('Timeout: Python service took longer than 5 minutes.');
        }
        throw new Error(`Failed to call Python service: ${error.message}`);
    }
};

module.exports = {
    callPythonScraper
};
