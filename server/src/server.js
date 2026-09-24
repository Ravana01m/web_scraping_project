require('dotenv').config();
const express = require('express');
const cors = require('cors');
const healthRoutes = require('./routes/healthRoutes');
const scrapeRoutes = require('./routes/scrapeRoutes');
const errorHandler = require('./middleware/errorHandler');

const app = express();

const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:5173';
app.use(cors({ origin: FRONTEND_URL }));

app.use(express.json());

// Routes
app.use('/api/health', healthRoutes);
app.use('/api/scrape', scrapeRoutes);

// Error Handler
app.use(errorHandler);

const PORT = process.env.NODE_PORT || 5000;

app.listen(PORT, () => {
    console.log(`Server listening on port ${PORT}`);
});
