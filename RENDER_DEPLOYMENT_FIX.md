# Render.com Deployment Fix

## Issue Identified

**Error:** 400 Bad Request on `https://gym-management-member-workout-system-8e9d.onrender.com/`

**Root Cause:** ALLOWED_HOSTS mismatch - the deployment hostname wasn't in the allowed hosts list.

---

## Solution

### Step 1: Update Environment Variables on Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Select the **gym-management-member-workout-system** service
3. Go to **Settings** → **Environment**
4. Update or add these variables:

| Key | Value |
|-----|-------|
| `ALLOWED_HOSTS` | `gym-management-member-workout-system-8e9d.onrender.com,localhost` |
| `DEBUG` | `False` |
| `SECRET_KEY` | *(generate a secure key)* |
| `DB_ENGINE` | `django.db.backends.postgresql` |
| `DB_NAME` | *(from your PostgreSQL URL)* |
| `DB_USER` | *(from your PostgreSQL URL)* |
| `DB_PASSWORD` | *(from your PostgreSQL URL)* |
| `DB_HOST` | *(from your PostgreSQL URL)* |
| `DB_PORT` | `5432` |

### Step 2: Deploy with Updated Configuration

1. Commit and push to GitHub:
```bash
git add .env.render render.yaml
git commit -m "Fix: Update ALLOWED_HOSTS for Render deployment"
git push origin main
```

2. Render will automatically redeploy
3. Or manually trigger: Dashboard → Service → **Manual Deploy**

### Step 3: Verify Deployment

After deployment completes:

```bash
# Check if API is responding
curl https://gym-management-member-workout-system-8e9d.onrender.com/api/v1/

# Expected: {"detail":"Authentication credentials were not provided."}
# OR redirect to API documentation

# If 400 error persists:
curl -i https://gym-management-member-workout-system-8e9d.onrender.com/
# Check response headers for error details
```

---

## Alternative: Environment Setup

If Render env vars are not set, create `.env` in the Render environment:

```bash
# SSH into Render (if available) or update via Environment tab

ALLOWED_HOSTS=gym-management-member-workout-system-8e9d.onrender.com,localhost
DEBUG=False
SECRET_KEY=your-very-secure-key-here-change-this

# Database (from Render PostgreSQL)
DATABASE_URL=postgresql://user:password@host:port/dbname
```

---

## Files Updated

### 1. `.env.render` ✅
- Updated ALLOWED_HOSTS to match actual deployment domain
- Contains all required environment variables

### 2. `render.yaml` ✅ (NEW)
- IaC (Infrastructure as Code) configuration
- Defines service, database, and environment setup
- Can be used with `render` CLI or as reference

### 3. `Procfile` ✓ (Already correct)
- Release: Runs migrations and creates test data
- Web: Starts Gunicorn with 4 workers

---

## Debugging

### Check Logs on Render

1. Dashboard → gym-api service
2. **Logs** tab to see:
   - Build logs
   - Deployment logs
   - Runtime errors

### Common Issues

| Issue | Solution |
|-------|----------|
| 400 Bad Request | Update ALLOWED_HOSTS |
| 500 Internal Error | Check database connection |
| Migration failed | Verify DATABASE_URL format |
| Static files missing | Run `collectstatic` after deployment |
| Import errors | Ensure `requirements-prod.txt` has all dependencies |

### Manual Testing

```bash
# Test API endpoint
curl https://gym-management-member-workout-system-8e9d.onrender.com/api/v1/

# Test login
curl -X POST https://gym-management-member-workout-system-8e9d.onrender.com/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"superadmin@gym.com","password":"SuperAdmin@123"}'

# Check if test data was created
curl https://gym-management-member-workout-system-8e9d.onrender.com/api/v1/users/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Production Checklist

- [x] ALLOWED_HOSTS configured correctly
- [ ] SECRET_KEY is unique and strong
- [ ] DEBUG set to False
- [ ] Database credentials secure
- [ ] Gunicorn workers optimized (4 workers for free tier)
- [ ] Migrations run successfully
- [ ] Test data created
- [ ] HTTPS enabled (automatic on Render)
- [ ] CORS configured for frontend
- [ ] Logging configured
- [ ] Error monitoring setup (optional)

---

## Next Steps

After fixing the 400 error:

1. **Test all endpoints** using Postman collection
2. **Monitor logs** for any runtime errors
3. **Check database** to ensure test data was created
4. **Set up monitoring** (Sentry, DataDog, etc.)
5. **Configure backups** for PostgreSQL database
6. **Plan scaling** strategy if needed

---

## Support Resources

- [Render Docs - Django](https://render.com/docs/deploy-django)
- [Django ALLOWED_HOSTS](https://docs.djangoproject.com/en/4.2/ref/settings/#allowed-hosts)
- [Gunicorn Configuration](https://docs.gunicorn.org/)
- [PostgreSQL Connection Issues](https://www.postgresql.org/docs/current/libpq-envars.html)

---

## Quick Reference

**Deployment URL:** `https://gym-management-member-workout-system-8e9d.onrender.com`

**API Base URL:** `https://gym-management-member-workout-system-8e9d.onrender.com/api/v1/`

**Admin Panel:** `https://gym-management-member-workout-system-8e9d.onrender.com/admin/`

**Test User:** superadmin@gym.com / SuperAdmin@123

---

**Updated:** January 15, 2026
