# Production Deployment Checklist

## Pre-Deployment Preparation

### Environment Configuration
- [ ] Copy `.env.example` to `.env` and configure all variables
- [ ] Set `APP_ENV=production`
- [ ] Configure `CORS_ORIGINS` with your domain(s)
- [ ] Add valid OpenAI API key
- [ ] Add valid Anthropic API key
- [ ] Choose default AI model (`DEFAULT_MODEL`)
- [ ] Configure model IDs (`OPENAI_MODEL_ID`, `ANTHROPIC_MODEL_ID`)

### SSL Certificates (Recommended for Production)
- [ ] Create `ssl/` directory
- [ ] Add SSL certificate (`ssl/cert.pem`)
- [ ] Add private key (`ssl/key.pem`)
- [ ] Uncomment HTTPS configuration in `nginx.conf`

### Security
- [ ] Review CORS settings
- [ ] Configure firewall rules
- [ ] Set up monitoring and alerting
- [ ] Plan backup strategy

## Deployment Steps

### 1. System Preparation
- [ ] Install Docker and Docker Compose
- [ ] Ensure sufficient disk space (minimum 5GB)
- [ ] Configure system limits (if needed)

### 2. Application Deployment
```bash
# Deploy the application
./deploy.sh production

# Or manually:
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

### 3. Post-Deployment Verification
- [ ] Check application health: `curl http://localhost/health`
- [ ] Verify API endpoints are accessible
- [ ] Test fact-checking functionality
- [ ] Check logs for errors: `docker-compose -f docker-compose.prod.yml logs`
- [ ] Verify SSL configuration (if applicable)

## Testing

### Functional Tests
- [ ] Test claim submission endpoint
- [ ] Verify JSON response format
- [ ] Test error handling
- [ ] Verify CORS headers

### Load Testing
- [ ] Test with concurrent requests
- [ ] Monitor resource usage
- [ ] Verify response times

### Security Tests
- [ ] Test for exposed API documentation (should be disabled in production)
- [ ] Verify CORS restrictions
- [ ] Test rate limiting (if implemented)

## Monitoring and Maintenance

### Health Checks
- [ ] Monitor application health endpoint
- [ ] Set up automated health checks
- [ ] Configure alerting for failures

### Log Management
- [ ] Set up log rotation
- [ ] Configure log aggregation
- [ ] Monitor error logs

### Performance Monitoring
- [ ] Monitor response times
- [ ] Track resource usage
- [ ] Set up performance alerts

## Backup and Recovery

### Data Backup
- [ ] Identify data to backup
- [ ] Set up automated backups
- [ ] Test backup restoration

### Disaster Recovery
- [ ] Document recovery procedures
- [ ] Test recovery scenarios
- [ ] Prepare rollback plan

## Scaling Considerations

### Horizontal Scaling
- [ ] Test multiple container instances
- [ ] Configure load balancing
- [ ] Monitor resource distribution

### Performance Optimization
- [ ] Enable Redis caching (if needed)
- [ ] Configure CDN for static assets
- [ ] Optimize database queries

## Security Best Practices

### API Security
- [ ] Implement rate limiting
- [ ] Use HTTPS in production
- [ ] Validate all inputs
- [ ] Sanitize outputs

### Infrastructure Security
- [ ] Regular security updates
- [ ] Network segmentation
- [ ] Access control policies
- [ ] Security monitoring

## Ongoing Maintenance

### Regular Tasks
- [ ] Update dependencies
- [ ] Review logs
- [ ] Monitor performance
- [ ] Security scans

### Emergency Procedures
- [ ] Emergency contact information
- [ ] Incident response plan
- [ ] Communication procedures

## Troubleshooting Guide

### Common Issues and Solutions

1. **Application won't start**
   - Check environment variables
   - Verify API keys
   - Review logs: `docker-compose logs`

2. **API requests failing**
   - Check API key validity
   - Verify model configuration
   - Monitor rate limits

3. **Performance issues**
   - Check resource usage
   - Review logs for bottlenecks
   - Consider scaling

4. **SSL problems**
   - Verify certificate paths
   - Check certificate validity
   - Review nginx configuration

## Contact and Support

- Documentation: `README.md`
- Issues: Check logs first
- Emergency: Have rollback plan ready