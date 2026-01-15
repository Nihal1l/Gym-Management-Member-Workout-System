# Render Deployment Guide - Gym Management API

## Overview
This guide walks you through deploying your Gym Management API to Render.com in less than 10 minutes.

## Prerequisites
- GitHub account with your code pushed
- Render.com account (free - sign up at https://render.com/)
- Git installed locally

---

## Step 1: Push Code to GitHub

### 1.1 Create GitHub Repository
1. Go to https://github.com/new
2. Create a new repository named `gym-management-api`
3. **DO NOT** initialize with README (your code already has it)

### 1.2 Push Local Code
```bash
cd C:\Users\HP\Desktop\Gym-Management-Member-Workout-System

# Add GitHub remote
git remote add origin https://github.com/YOUR_USERNAME/gym-management-api.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Replace `YOUR_USERNAME` with your actual GitHub username**

---

## Step 2: Deploy to Render

### 2.1 Connect GitHub to Render
1. Go to https://render.com/ and sign up
2. Click **"New"** → **"Web Service"**
3. Click **"Connect GitHub account"**
4. Authorize Render to access your GitHub
5. Search for and select your `gym-management-api` repository

### 2.2 Configure Web Service
**Name:** `gym-management-api`
**Environment:** `Python 3`
**Region:** Choose closest to you
**Branch:** `main`

**Build Command:**
```
pip install -r requirements.txt
```

**Start Command:**
```
gunicorn gym_management.wsgi
```

### 2.3 Add Environment Variables
In the Render dashboard, add these environment variables:

```
DEBUG=False
SECRET_KEY=[Render will generate automatically]
ALLOWED_HOSTS=gym-management-api.onrender.com
DB_ENGINE=django.db.backends.postgresql
```

**Note:** Other DB variables will be auto-set by PostgreSQL service

### 2.4 Create PostgreSQL Database
1. Click **"New"** → **"PostgreSQL"**
2. **Name:** `gym-database`
3. **Region:** Same as web service
4. **PostgreSQL Version:** 15
5. **Plan:** Free (sufficient for testing)

### 2.5 Connect Database to Web Service
1. After PostgreSQL is created, go back to your web service
2. Add environment variables for database connection
3. You'll get `DATABASE_URL` from PostgreSQL service - add to web service

---

## Step 3: Configure Django for Production

### 3.1 Update Settings (Already Done ✓)
Your `settings.py` already supports:
- Environment variables via `python-decouple`
- PostgreSQL configuration
- DEBUG mode control

### 3.2 Verify ALLOWED_HOSTS
In your web service environment variables, set:
```
ALLOWED_HOSTS=your-service-name.onrender.com
```

---

## Step 4: Verify Deployment

### 4.1 Check Build Logs
1. In Render dashboard, click your web service
2. Go to **"Logs"** tab
3. Verify you see: `"Starting gunicorn..."`
4. Wait for **Status: Live** (green)

### 4.2 Test API Endpoints
Once deployment is live:

**Login Endpoint:**
```bash
curl -X POST https://YOUR_SERVICE_NAME.onrender.com/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"superadmin@gym.com","password":"SuperAdmin@123"}'
```

**Get API Status:**
```
https://YOUR_SERVICE_NAME.onrender.com/api/v1/auth/login/
```

### 4.3 Access Admin Panel
```
https://YOUR_SERVICE_NAME.onrender.com/admin/
```
Login with: `superadmin@gym.com` / `SuperAdmin@123`

---

## Step 5: Create Test Data (Optional)

Run the test data creation command:
```bash
# Via Render Shell (in dashboard)
python manage.py create_test_data
```

Or via curl:
```bash
curl -X POST https://YOUR_SERVICE_NAME.onrender.com/api/v1/users/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

---

## Testing Your Deployed API

### Using Postman
1. Import `postman/Gym_Management_API.postman_collection.json`
2. Update `{{base_url}}` to your Render URL:
   ```
   https://gym-management-api.onrender.com
   ```
3. Test endpoints

### API Endpoints Available
- `POST /api/v1/auth/login/` - Login
- `GET /api/v1/users/` - List users
- `POST /api/v1/users/` - Create user
- `GET /api/v1/workout-plans/` - List plans
- `POST /api/v1/workout-plans/` - Create plan
- `GET /api/v1/workout-tasks/` - List tasks
- And 19+ more endpoints

### Test Users
```
Super Admin: superadmin@gym.com / SuperAdmin@123
Manager 1: manager1@gym.com / Manager@123
Trainer 1: trainer1@gym.com / Trainer@123
Member 1: member1@gym.com / Member@123
```

---

## Troubleshooting

### Issue: "Build failed"
**Solution:**
- Check build logs in Render dashboard
- Verify `requirements.txt` is in root directory
- Check Python syntax errors

### Issue: "502 Bad Gateway"
**Solution:**
- Check web service logs
- Verify database connection
- Ensure `Procfile` exists and is correct

### Issue: "Database connection error"
**Solution:**
- Verify PostgreSQL service is running
- Check database environment variables
- Verify `DB_ENGINE=django.db.backends.postgresql`

### Issue: "Static files not loading"
**Solution:**
- Not needed for API-only backend
- If needed: Run `python manage.py collectstatic`

---

## Performance Notes

**Free Tier Limitations:**
- Web service spins down after 15 minutes of inactivity
- PostgreSQL limited to 90 days
- 512MB RAM
- Sufficient for testing and demos

**For Production:**
- Upgrade to paid plans
- Add Redis for caching
- Consider CDN for static files
- Monitor performance in Render dashboard

---

## Next Steps

1. ✅ Push code to GitHub
2. ✅ Deploy to Render
3. ✅ Test all endpoints
4. ✅ Share public API URL
5. ✅ Monitor logs and performance

---

## Your Deployed API URL

Once deployed, your API will be accessible at:
```
https://gym-management-api.onrender.com/api/v1/
```

**Admin Panel:**
```
https://gym-management-api.onrender.com/admin/
```

**API Documentation:**
```
https://gym-management-api.onrender.com/api/docs/
```

---

## Support

- Render Docs: https://render.com/docs
- Django Docs: https://docs.djangoproject.com
- DRF Docs: https://www.django-rest-framework.org

---

**Deployment Time:** ~5-10 minutes
**Status:** Ready to deploy! 🚀
