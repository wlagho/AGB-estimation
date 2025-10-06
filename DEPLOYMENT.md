# SHCAP Production Deployment Guide

## Production Checklist

### Security
- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Set `FLASK_ENV=production`
- [ ] Enable HTTPS/SSL
- [ ] Configure secure session cookies
- [ ] Review and harden RLS policies
- [ ] Set up firewall rules
- [ ] Enable rate limiting
- [ ] Configure CORS if needed

### Email Configuration
- [ ] Set up production SMTP server
- [ ] Verify email sending works
- [ ] Configure SPF and DKIM records
- [ ] Set appropriate sender domain

### Database
- [ ] Verify Supabase production settings
- [ ] Set up database backups
- [ ] Configure connection pooling
- [ ] Monitor database performance

### Application
- [ ] Test all features in staging
- [ ] Set up logging and monitoring
- [ ] Configure error tracking (e.g., Sentry)
- [ ] Set up health check endpoints
- [ ] Test with realistic user load

## Deployment Options

### Option 1: Heroku

1. Install Heroku CLI
2. Create a Heroku app:
```bash
heroku create shcap-platform
```

3. Set environment variables:
```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DATABASE_URL=your-database-url
heroku config:set MAIL_SERVER=smtp.gmail.com
# ... set all other variables
```

4. Deploy:
```bash
git push heroku main
```

### Option 2: DigitalOcean/AWS/GCP with Gunicorn

1. Install Gunicorn:
```bash
pip install gunicorn
```

2. Create a systemd service file (`/etc/systemd/system/shcap.service`):
```ini
[Unit]
Description=SHCAP Flask Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/shcap
Environment="PATH=/var/www/shcap/venv/bin"
ExecStart=/var/www/shcap/venv/bin/gunicorn --workers 4 --bind 0.0.0.0:8000 wsgi:app

[Install]
WantedBy=multi-user.target
```

3. Start the service:
```bash
sudo systemctl start shcap
sudo systemctl enable shcap
```

4. Configure Nginx as reverse proxy:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Option 3: Docker

1. Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "wsgi:app"]
```

2. Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    env_file:
      - .env
    restart: unless-stopped
```

3. Build and run:
```bash
docker-compose up -d
```

## Production Environment Variables

Create a `.env.production` file:

```env
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=<generate-strong-random-key>

# Database
SUPABASE_URL=your-production-supabase-url
SUPABASE_KEY=your-production-supabase-key
DATABASE_URL=your-production-database-url

# Email Configuration
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=apikey
MAIL_PASSWORD=your-sendgrid-api-key
MAIL_DEFAULT_SENDER=noreply@yourdomain.com

# Session Configuration
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
```

## Generate Strong Secret Key

```python
import secrets
print(secrets.token_hex(32))
```

## SSL/HTTPS Setup

### Using Let's Encrypt with Certbot

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Monitoring and Logging

### Set up application logging

Add to `app.py`:

```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/shcap.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('SHCAP startup')
```

### Monitor application health

Create a health check endpoint:

```python
@app.route('/health')
def health():
    return {'status': 'healthy', 'database': 'connected'}, 200
```

## Database Backup

Set up automated Supabase backups or use pg_dump:

```bash
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql
```

## Performance Optimization

1. Enable response compression
2. Set up CDN for static assets
3. Configure Redis for session storage
4. Implement database query caching
5. Use connection pooling

## Security Hardening

1. Set up rate limiting with Flask-Limiter
2. Enable CORS properly if needed
3. Add security headers:
```python
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
```

## Scaling Considerations

- Use load balancer for multiple instances
- Configure Redis for shared session storage
- Set up database read replicas
- Implement caching layer (Redis/Memcached)
- Use CDN for static assets

## Maintenance

Regular tasks:
- Monitor application logs
- Review security updates
- Database optimization
- Backup verification
- Performance monitoring
- Update dependencies
- Clean up expired tokens

## Rollback Plan

1. Keep previous version tagged
2. Test rollback in staging
3. Document rollback steps
4. Have database backup ready
5. Test rollback procedure regularly
