import express from 'express';
import dotenv from 'dotenv';
import helmet from 'helmet';
import corsMiddleware from './middleware/cors.js';
import { errorHandler, notFound } from './middleware/errorHandler.js';
import userRoutes from './routes/userRoutes.js';

// Load environment variables
dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

// Security middleware
app.use(helmet({
  crossOriginEmbedderPolicy: false,
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", "data:", "https:"],
    },
  },
}));

// CORS middleware
app.use(corsMiddleware);

// Body parsing middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Request logging middleware
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
  next();
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    success: true,
    message: 'MayaCode Backend API is running',
    timestamp: new Date().toISOString(),
    version: process.env.API_VERSION || 'v1'
  });
});

// API routes
app.use('/api/v1/user', userRoutes);

// Welcome route
app.get('/', (req, res) => {
  res.json({
    success: true,
    message: 'Welcome to MayaCode Backend API',
    version: process.env.API_VERSION || 'v1',
    endpoints: {
      health: '/health',
      userProfile: '/api/v1/user/profile',
      userActions: '/api/v1/user/actions',
      userDocuments: '/api/v1/user/documents',
      dashboardSummary: '/api/v1/user/dashboard-summary'
    },
    timestamp: new Date().toISOString()
  });
});

// 404 handler
app.use(notFound);

// Error handling middleware (must be last)
app.use(errorHandler);

// Start server
app.listen(PORT, () => {
  console.log(`🚀 MayaCode Backend API running on port ${PORT}`);
  console.log(`📊 Health check: http://localhost:${PORT}/health`);
  console.log(`🌐 API Base URL: http://localhost:${PORT}/api/v1`);
  console.log(`📝 Environment: ${process.env.NODE_ENV || 'development'}`);
});

export default app; 