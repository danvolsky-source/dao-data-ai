# Pre-Production Deployment Checklist

## Critical Configuration Items

Before deploying to production, the following items MUST be configured:

### 1. Legal Documentation (docs/regulatory/)

#### TERMS_OF_SERVICE.md
- [ ] Line 221: Replace `[Jurisdiction]` with actual legal jurisdiction (e.g., "Delaware, United States")
- [ ] Line 257: Replace `[Your Website]` with actual website URL
- [ ] Line 259: Replace `[Your Legal Address]` with actual legal business address
- [ ] Review entire document with legal counsel

#### PRIVACY_POLICY.md
- [ ] Line 247: Replace `[Specify region, e.g., US/EU]` with actual data storage location
- [ ] Line 247: Replace `[Primary Jurisdiction]` placeholders with actual jurisdiction
- [ ] Review entire document with legal counsel and DPO

#### MODEL_DOCUMENTATION.md
- [ ] Review all content for accuracy
- [ ] Update with actual model performance metrics when available
- [ ] Verify all contact emails exist and are monitored

### 2. Environment Variables

#### Required (Backend will not start without these):
- [ ] `SUPABASE_URL`: Your Supabase project URL
- [ ] `SUPABASE_KEY`: Your Supabase anon/public key
- [ ] `ADMIN_KEY`: Strong secret key for admin API access (minimum 32 characters)

#### Recommended:
- [ ] `DISCORD_BOT_TOKEN`: For live Discord sentiment analysis
- [ ] `SENTRY_DSN`: For error monitoring
- [ ] `LOG_LEVEL`: Set to "INFO" or "WARNING" for production

### 3. Database Setup

- [ ] Run migration: `backend/alembic/versions/001_add_ml_regulatory_tables.sql`
- [ ] Verify all tables created successfully
- [ ] Verify indexes created
- [ ] Test Row Level Security policies
- [ ] Set up automated backups

### 4. Security Configuration

- [ ] Generate strong `ADMIN_KEY` (use: `openssl rand -base64 32`)
- [ ] Enable HTTPS/TLS in production
- [ ] Configure CORS origins (replace `["*"]` with actual domains in `main.py`)
- [ ] Set up rate limiting on API endpoints
- [ ] Configure firewall rules
- [ ] Enable DDoS protection

### 5. Code Updates

#### backend/api/audit.py
- ✅ Already fixed: ADMIN_KEY now requires environment variable (no insecure default)

#### backend/regulatory/disclaimers.py
- ✅ Already fixed: Standardized all disclaimers to English

#### Logging
- [ ] Replace all `print()` statements with proper logging:
  - `backend/sentiment_service/discord_analyzer.py` line 217-218
  - `backend/sentiment_service/forum_analyzer.py` line 259
  - Any other print statements in production code

### 6. Contact Emails

Set up and monitor the following email addresses:
- [ ] legal@daodataai.com (or your domain)
- [ ] privacy@daodataai.com
- [ ] dpo@daodataai.com (Data Protection Officer)
- [ ] tech@daodataai.com
- [ ] security@daodataai.com
- [ ] press@daodataai.com
- [ ] feedback@daodataai.com
- [ ] audit@daodataai.com

### 7. Monitoring and Alerting

- [ ] Set up error monitoring (Sentry or similar)
- [ ] Configure API performance monitoring
- [ ] Set up database monitoring
- [ ] Configure audit log alerts
- [ ] Set up security incident alerts
- [ ] Configure uptime monitoring

### 8. Legal Review

- [ ] Have Terms of Service reviewed by legal counsel
- [ ] Have Privacy Policy reviewed by legal counsel and DPO
- [ ] Have Model Documentation reviewed for regulatory compliance
- [ ] Verify compliance with local laws (securities, data protection, etc.)
- [ ] Consider liability insurance

### 9. Testing

- [ ] Test all API endpoints with realistic data
- [ ] Test audit logging functionality
- [ ] Test sentiment analysis with real Discord/forum data
- [ ] Load testing on APIs
- [ ] Security penetration testing
- [ ] Test backup and recovery procedures

### 10. Documentation

- [ ] Update README with production deployment instructions
- [ ] Document API endpoints (OpenAPI/Swagger)
- [ ] Create runbook for common operations
- [ ] Document incident response procedures
- [ ] Create user guides

## Production Environment Variables Template

Create a `.env` file with these variables:

```bash
# Supabase Configuration (REQUIRED)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_public_key_here

# Admin Access (REQUIRED - Generate with: openssl rand -base64 32)
ADMIN_KEY=your_strong_secret_key_minimum_32_characters

# Optional Services
DISCORD_BOT_TOKEN=your_discord_bot_token_if_using_live_analysis
SENTRY_DSN=your_sentry_dsn_for_error_monitoring

# Logging
LOG_LEVEL=INFO

# Application
PORT=8000
ENVIRONMENT=production
```

## Security Notes

### DO NOT:
- ❌ Use default or weak admin keys
- ❌ Commit secrets to git
- ❌ Use development credentials in production
- ❌ Allow unrestricted CORS (`origins=["*"]`)
- ❌ Run without HTTPS/TLS
- ❌ Skip security audits

### DO:
- ✅ Use environment variables for all secrets
- ✅ Enable HTTPS/TLS
- ✅ Set up proper CORS restrictions
- ✅ Implement rate limiting
- ✅ Monitor audit logs regularly
- ✅ Keep dependencies updated
- ✅ Regular security scans

## Regulatory Compliance Notes

### Before Launch:
1. Consult with legal counsel specializing in:
   - Securities law (if applicable in your jurisdiction)
   - Data protection (GDPR/CCPA compliance)
   - Consumer protection laws
   - Cryptocurrency regulations

2. Ensure disclaimers are:
   - Prominently displayed
   - Clear and unambiguous
   - Legally reviewed
   - Updated regularly

3. Verify audit logging:
   - 7-year retention capability
   - Secure and tamper-proof
   - Accessible for regulatory audits
   - Regularly backed up

## Support

For questions about production deployment:
- Technical: tech@daodataai.com
- Legal: legal@daodataai.com
- Security: security@daodataai.com

---

**Last Updated:** December 18, 2025  
**Version:** 1.0.0

© 2025 DAO Data AI. All rights reserved.
