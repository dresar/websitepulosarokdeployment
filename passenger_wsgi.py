import os
import sys
from django.core.wsgi import get_wsgi_application

# Add the project directory to Python path
sys.path.insert(0, '/home/expedien/public_html/pulosarok.my.id')

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pulosarok_website.settings')

# Deployment Configuration - Mode Tidak Ketat
os.environ['DEBUG'] = 'False'
os.environ['SECRET_KEY'] = 'oqh+m&9%q9%(r5ti-u^d-@s80p#%0il#hv@)iqmx2u^3vke&kq'
os.environ['ALLOWED_HOSTS'] = 'pulosarok.my.id,www.pulosarok.my.id,localhost,127.0.0.1,expedien.my.id'

# Database Configuration
os.environ['DATABASE_ENGINE'] = 'django.db.backends.sqlite3'
os.environ['DATABASE_NAME'] = 'db.sqlite3'
os.environ['DATABASE_USER'] = ''
os.environ['DATABASE_PASSWORD'] = ''
os.environ['DATABASE_HOST'] = ''
os.environ['DATABASE_PORT'] = ''

# Security Settings - Mode Tidak Ketat
os.environ['SECURE_SSL_REDIRECT'] = 'False'
os.environ['SECURE_HSTS_SECONDS'] = '0'
os.environ['SECURE_HSTS_INCLUDE_SUBDOMAINS'] = 'False'
os.environ['SECURE_HSTS_PRELOAD'] = 'False'
os.environ['CSRF_COOKIE_SECURE'] = 'False'
os.environ['SESSION_COOKIE_SECURE'] = 'False'
os.environ['SECURE_BROWSER_XSS_FILTER'] = 'True'
os.environ['SECURE_CONTENT_TYPE_NOSNIFF'] = 'True'
os.environ['X_FRAME_OPTIONS'] = 'SAMEORIGIN'

# Session Settings - Mode Fleksibel
os.environ['SESSION_COOKIE_HTTPONLY'] = 'True'
os.environ['SESSION_COOKIE_SAMESITE'] = 'Lax'
os.environ['SESSION_COOKIE_AGE'] = '3600'
os.environ['SESSION_EXPIRE_AT_BROWSER_CLOSE'] = 'False'

# CSRF Settings - Mode Fleksibel
os.environ['CSRF_COOKIE_HTTPONLY'] = 'True'
os.environ['CSRF_COOKIE_SAMESITE'] = 'Lax'
os.environ['CSRF_TRUSTED_ORIGINS'] = 'https://pulosarok.my.id,https://www.pulosarok.my.id,http://localhost:8000'

# Static and Media Files
os.environ['STATIC_URL'] = '/static/'
os.environ['STATIC_ROOT'] = '/home/expedien/public_html/pulosarok.my.id/staticfiles/'
os.environ['MEDIA_URL'] = '/media/'
os.environ['MEDIA_ROOT'] = '/home/expedien/public_html/pulosarok.my.id/media/'

# Logging Configuration
os.environ['LOG_LEVEL'] = 'INFO'
os.environ['LOG_FILE'] = '/home/expedien/public_html/pulosarok.my.id/logs/django.log'

# CORS Settings
os.environ['CORS_ALLOWED_ORIGINS'] = 'https://pulosarok.my.id,https://www.pulosarok.my.id,http://localhost:8000'
os.environ['CORS_ALLOW_CREDENTIALS'] = 'True'

# Cache Configuration - Disable untuk development
os.environ['CACHE_BACKEND'] = 'django.core.cache.backends.dummy.DummyCache'
os.environ['CACHE_MIDDLEWARE_SECONDS'] = '0'

# Performance Settings
os.environ['CONN_MAX_AGE'] = '0'
os.environ['CONN_MAX_AGE_OPTIONS'] = '0'

# Environment
os.environ['ENVIRONMENT'] = 'production'
os.environ['DEPLOYMENT_MODE'] = 'hosting'

# Resource Limits untuk cPanel
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['NUMEXPR_NUM_THREADS'] = '1'
os.environ['VECLIB_MAXIMUM_THREADS'] = '1'
os.environ['NUMBA_NUM_THREADS'] = '1'

# Admin Configuration
os.environ['ADMIN_URL'] = 'admin-panel/'
os.environ['LOGIN_URL'] = '/custom-login-redirect/'
os.environ['LOGIN_REDIRECT_URL'] = '/admin-panel/'
os.environ['LOGOUT_REDIRECT_URL'] = '/admin-panel/login/'

# Maintenance Mode - Disabled
os.environ['MAINTENANCE_MODE'] = 'False'
os.environ['MAINTENANCE_MODE_IGNORE_ADMIN'] = 'True'
os.environ['MAINTENANCE_MODE_IGNORE_STAFF'] = 'True'

# Security Monitoring - Disabled untuk hosting
os.environ['SECURITY_MONITORING'] = 'False'
os.environ['INTRUSION_DETECTION'] = 'False'
os.environ['MALWARE_SCANNING'] = 'False'
os.environ['VULNERABILITY_SCANNING'] = 'False'

# Compliance - Disabled untuk hosting
os.environ['AUDIT_LOGGING'] = 'False'
os.environ['COMPLIANCE_MODE'] = 'False'
os.environ['PRIVACY_MODE'] = 'False'

# Rate Limiting - Disabled
os.environ['RATE_LIMIT_ENABLED'] = 'False'

# Error Reporting - Disabled
os.environ['ERROR_REPORTING'] = 'False'

# Get WSGI application
application = get_wsgi_application()
