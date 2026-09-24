require('dotenv').config();
const express = require('express');
const cors = require('cors');
const healthRoutes = require('./routes/healthRoutes');
const scrapeRoutes = require('./routes/scrapeRoutes');
const errorHandler = require('./middleware/errorHandler');

const app = express();

const FRONTEND_URL = process.env.FRONTEND_URL;
if (FRONTEND_URL && FRONTEND_URL !== '*') {
    const allowedOrigins = FRONTEND_URL.split(',').map(url => url.trim());
    app.use(cors({
        origin: (origin, callback) => {
            if (!origin || allowedOrigins.includes(origin) || origin.endsWith('.vercel.app')) {
                callback(null, true);
            } else {
                callback(null, true);
            }
        },
        credentials: true
    }));
} else {
    app.use(cors());
}

app.use(express.json());

// Routes
app.use('/api/health', healthRoutes);
app.use('/api/scrape', scrapeRoutes);

// Error Handler
app.use(errorHandler);

const PORT = process.env.NODE_PORT || 5000;

if (require.main === module) {
    app.listen(PORT, () => {
        console.log(`Server listening on port ${PORT}`);
    });
}

module.exports = app;
