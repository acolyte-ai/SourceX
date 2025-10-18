#!/bin/bash

# Crisis Fact-Check API Deployment Script
# Usage: ./deploy.sh [development|production]

set -e

ENVIRONMENT=${1:-development}
echo "🚀 Starting deployment for $ENVIRONMENT environment..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please copy .env.example to .env and configure it."
    exit 1
fi

# Check if API keys are configured
if ! grep -q "OPENAI_API_KEY=your_openai_api_key_here" .env; then
    echo "✅ API keys appear to be configured"
else
    echo "⚠️  Please configure your API keys in .env file"
fi

case $ENVIRONMENT in
    "development")
        echo "🔧 Starting development deployment..."
        docker-compose down
        docker-compose build --no-cache
        docker-compose up -d
        echo "✅ Development deployment complete!"
        echo "📱 Application available at: http://localhost:8000"
        echo "📚 API docs at: http://localhost:8000/docs"
        ;;
    "production")
        echo "🏭 Starting production deployment..."
        docker-compose -f docker-compose.prod.yml down
        docker-compose -f docker-compose.prod.yml build --no-cache
        docker-compose -f docker-compose.prod.yml up -d
        echo "✅ Production deployment complete!"
        echo "📱 Application available at: http://localhost"
        ;;
    *)
        echo "❌ Unknown environment: $ENVIRONMENT"
        echo "Usage: ./deploy.sh [development|production]"
        exit 1
        ;;
esac

echo "🔍 Checking application health..."
sleep 10

if [ "$ENVIRONMENT" = "development" ]; then
    HEALTH_URL="http://localhost:8000/health"
else
    HEALTH_URL="http://localhost/health"
fi

if curl -f $HEALTH_URL > /dev/null 2>&1; then
    echo "✅ Application is healthy!"
else
    echo "⚠️  Health check failed. Check logs with: docker-compose logs"
fi

echo "🎉 Deployment completed!"