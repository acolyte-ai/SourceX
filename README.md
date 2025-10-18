# Crisis Fact-Check API - Deployment Guide

## Overview

This is a FastAPI-based news verification application with AI-powered fact-checking capabilities. The application uses multiple AI agents to analyze news claims and provide structured fact-checking results.

## Features

- AI-powered fact-checking using OpenAI and Anthropic models
- Multi-agent verification system
- Real-time claim analysis
- Structured JSON responses
- Web-based interface
- RESTful API endpoints

## Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Valid API keys for OpenAI and/or Anthropic

## Quick Start

### 1. Environment Setup

Copy the example environment file and configure your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
DEFAULT_MODEL=openai  # or anthropic
```

### 2. Development Deployment

```bash
# Build and start the application
docker-compose up --build

# The application will be available at:
# - API: http://localhost:8000
# - Web Interface: http://localhost:8000
# - API Documentation: http://localhost:8000/docs
```

### 3. Production Deployment

```bash
# Use the production configuration
docker-compose -f docker-compose.prod.yml up -d --build

# The application will be available at:
# - HTTP: http://localhost
# - HTTPS: http://localhost (if SSL certificates are configured)
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | - | OpenAI API key |
| `ANTHROPIC_API_KEY` | Yes | - | Anthropic API key |
| `DEFAULT_MODEL` | No | openai | Default AI model (openai/anthropic) |
| `OPENAI_MODEL_ID` | No | gpt-4o | OpenAI model to use |
| `ANTHROPIC_MODEL_ID` | No | claude-sonnet-4-5 | Anthropic model to use |
| `APP_ENV` | No | production | Environment (development/production) |
| `CORS_ORIGINS` | No | * | Allowed CORS origins |
| `REDIS_URL` | No | - | Redis URL for caching |

### API Endpoints

- `POST /fact-check` - Submit a claim for fact-checking
- `GET /health` - Health check endpoint
- `GET /stats` - System statistics
- `GET /docs` - API documentation (development only)

## Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **Environment Variables**: Use `.env` files for local development
3. **CORS**: Configure `CORS_ORIGINS` appropriately for your domain
4. **SSL**: Use HTTPS in production (configure SSL certificates)
5. **Rate Limiting**: Consider implementing rate limiting for production

## SSL Setup (Optional)

For HTTPS in production:

1. Create SSL directory:
```bash
mkdir ssl
```

2. Add your SSL certificates:
```
ssl/cert.pem  # Your SSL certificate
ssl/key.pem   # Your private key
```

3. Uncomment the HTTPS section in `nginx.conf`

## Monitoring

### Health Checks

The application includes built-in health checks:
- Docker health check on port 8000
- Endpoint: `GET /health`

### Logs

View application logs:
```bash
docker-compose logs -f
```

View Nginx logs (production):
```bash
docker-compose -f docker-compose.prod.yml logs -f nginx
```

## Scaling

### Horizontal Scaling

For production deployment with multiple instances:

```bash
# Scale the web service
docker-compose -f docker-compose.prod.yml up -d --scale web=3
```

### Performance Optimization

1. **Caching**: Enable Redis for response caching
2. **CDN**: Use a CDN for static assets
3. **Load Balancing**: Nginx provides basic load balancing
4. **Resource Limits**: Adjust memory/CPU limits in docker-compose

## Troubleshooting

### Common Issues

1. **API Key Errors**: Verify your API keys are correctly set in `.env`
2. **Port Conflicts**: Ensure ports 8000 and 80/443 are available
3. **Memory Issues**: Increase memory limits in docker-compose if needed
4. **CORS Issues**: Configure `CORS_ORIGINS` for your domain

### Debug Mode

Enable debug logging:
```bash
# Add to .env
APP_DEBUG=true
LOG_LEVEL=DEBUG
```

## Development

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### Testing

```bash
# Test the API
curl -X POST "http://localhost:8000/fact-check" \
     -H "Content-Type: application/json" \
     -d '{"claim_text":"Test claim","source_url":""}'
```

## API Usage Example

```javascript
// Frontend JavaScript example
const response = await fetch('http://localhost:8000/fact-check', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    claim_text: 'Your news claim here',
    source_url: 'https://example.com/article',
    crisis_category: 'general'
  })
});

const result = await response.json();
console.log(result);
```

## Deployment Checklist

- [ ] Configure environment variables
- [ ] Set up SSL certificates (production)
- [ ] Configure CORS origins
- [ ] Set up monitoring and logging
- [ ] Test all endpoints
- [ ] Verify health checks
- [ ] Configure backup strategy
- [ ] Set up alerting

## Support

For issues and questions:
1. Check the logs for error messages
2. Verify environment configuration
3. Test with the provided example endpoints
4. Check API key validity and permissions