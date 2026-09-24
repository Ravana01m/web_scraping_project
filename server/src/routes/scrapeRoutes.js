const express = require('express');
const router = express.Router();
const scrapeController = require('../controllers/scrapeController');

router.post('/', scrapeController.startScrape);
router.get('/:jobId', scrapeController.getJobStatus);
router.get('/:jobId/download', scrapeController.downloadCsv);

module.exports = router;
