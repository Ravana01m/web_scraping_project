const { v4: uuidv4 } = require('uuid');
const pythonService = require('../services/pythonService');

// In-memory job store
const jobs = new Map();

/**
 * Validates a URL
 * @param {string} urlString 
 * @returns {boolean}
 */
const isValidUrl = (urlString) => {
    try {
        new URL(urlString);
        return true;
    } catch (e) {
        return false;
    }
};

/**
 * Starts a scraping job
 */
const startScrape = (req, res) => {
    const { platform, url, maxReviews = 100 } = req.body;

    // Validation
    if (!platform || (platform !== 'croma' && platform !== 'imdb')) {
        return res.status(400).json({ error: "Invalid platform. Must be 'croma' or 'imdb'." });
    }
    if (!url || !isValidUrl(url)) {
        return res.status(400).json({ error: "Invalid URL." });
    }
    if (platform === 'croma' && !url.includes('croma.com')) {
        return res.status(400).json({ error: "URL must contain 'croma.com' for Croma platform." });
    }
    if (platform === 'imdb' && !url.includes('imdb.com')) {
        return res.status(400).json({ error: "URL must contain 'imdb.com' for IMDB platform." });
    }
    const maxRevInt = parseInt(maxReviews, 10);
    if (isNaN(maxRevInt) || maxRevInt < 1 || maxRevInt > 500) {
        return res.status(400).json({ error: "maxReviews must be an integer between 1 and 500." });
    }

    const jobId = uuidv4();
    const job = {
        jobId,
        platform,
        url,
        maxReviews: maxRevInt,
        status: 'queued',
        createdAt: new Date(),
        completedAt: null,
        data: null,
        error: null
    };

    jobs.set(jobId, job);

    // Start async process
    processJob(job);

    return res.status(202).json({ jobId, status: 'queued' });
};

/**
 * Process job asynchronously
 * @param {Object} job 
 */
const processJob = async (job) => {
    try {
        job.status = 'scraping';
        // Python service will do scraping and analysis
        const results = await pythonService.callPythonScraper({
            platform: job.platform,
            url: job.url,
            maxReviews: job.maxReviews
        });
        
        // Setting analyzing status would be here if pythonService returned intermediate status, 
        // but since it's a single blocking call we jump to completed
        job.status = 'completed';
        job.data = results;
        job.completedAt = new Date();
    } catch (error) {
        job.status = 'failed';
        job.error = error.message;
        job.completedAt = new Date();
        console.error(`Job ${job.jobId} failed:`, error);
    }
};

/**
 * Gets the status of a scraping job
 */
const getJobStatus = (req, res) => {
    const { jobId } = req.params;
    const job = jobs.get(jobId);

    if (!job) {
        return res.status(404).json({ error: 'Job not found' });
    }

    return res.json(job);
};

/**
 * Escapes CSV field
 */
const escapeCSV = (field) => {
    if (field == null) return '""';
    const stringField = String(field);
    if (stringField.includes('"') || stringField.includes(',') || stringField.includes('\n')) {
        return `"${stringField.replace(/"/g, '""')}"`;
    }
    return stringField;
};

/**
 * Downloads the job results as a CSV
 */
const downloadCsv = (req, res) => {
    const { jobId } = req.params;
    const job = jobs.get(jobId);

    if (!job) {
        return res.status(404).json({ error: 'Job not found' });
    }

    if (job.status !== 'completed' || !job.data) {
        return res.status(400).json({ error: 'Job is not completed yet' });
    }

    const reviews = job.data.reviews || [];
    
    // Generate CSV
    const headers = ['rating', 'review', 'review_characters', 'likes', 'dislikes'];
    const csvRows = [];
    csvRows.push(headers.join(','));

    for (const r of reviews) {
        const row = [
            escapeCSV(r.rating),
            escapeCSV(r.review),
            escapeCSV(r.review_characters ? JSON.stringify(r.review_characters) : ''),
            escapeCSV(r.likes),
            escapeCSV(r.dislikes)
        ];
        csvRows.push(row.join(','));
    }

    const csvContent = csvRows.join('\n');

    res.setHeader('Content-Type', 'text/csv');
    res.setHeader('Content-Disposition', `attachment; filename="reviews_${jobId}.csv"`);
    return res.send(csvContent);
};

module.exports = {
    startScrape,
    getJobStatus,
    downloadCsv
};
