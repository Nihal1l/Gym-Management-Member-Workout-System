# 🚀 Render Deployment - Complete Setup Guide

## Quick Summary

Your Gym Management API is **ready to deploy to Render** in just 5 steps:

1. Push code to GitHub
2. Create Render account
3. Connect GitHub repository
4. Configure environment variables
5. Deploy!

---

## Step-by-Step Deployment Instructions

### Prerequisites
- GitHub account (free at https://github.com)
- Render account (free at https://render.com)
- Your local code with git initialized

---

## STEP 1: Push Code to GitHub (5 minutes)

### 1.1 Create GitHub Repository

1. Go to https://github.com/new
2. Enter repository name: `gym-management-api`
3. Choose **Public** (so Render can access it)
4. Click **"Create repository"**

### 1.2 Add Remote and Push

```bash
# Navigate to project directory
cd C:\Users\HP\Desktop\Gym-Management-Member-Workout-System

# Add GitHub remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/gym-management-api.git

# Verify remote
git remote -v

# Push code to GitHub
git branch -M main
git push -u origin main
```

✅ Your code is now on GitHub!

---

## STEP 2: Create Render Account (2 minutes)

1. Go to https://render.com
2. Click **"Sign up"**
3. Sign up with GitHub (easier) or email
4. Verify your email
5. You're ready!

---

## STEP 3: Deploy on Render (3 minutes)

### 3.1 Create Web Service

1. Click **"New"** button → **"Web Service"**
2. Click **"Connect GitHub account"** (if not already)
3. Authorize Render to access GitHub
4. Search for `gym-management-api` repository
5. Select it and click **"Connect"**

### 3.2 Configure Web Service

Fill in these settings:

| Setting | Value |
|---------|-------|
| **Name** | `gym-management-api` |
| **Environment** | `Python 3` |
| **Region** | Your closest region |
| **Branch** | `main` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn gym_management.wsgi` |

### 3.3 Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"**

Add these variables:

```
DEBUG=False
SECRET_KEY=generate_a_random_string_here
ALLOWED_HOSTS=gym-management-api.onrender.com
DB_ENGINE=django.db.backends.postgresql
```

**For SECRET_KEY:** Generate a random 50+ character string, or Render will generate one.

### 3.4 Create PostgreSQL Database

1. While still in Render, click **"New"** → **"PostgreSQL"**
2. Fill in:
   - **Name:** `gym-database`
   - **Region:** Same as web service
   - **PostgreSQL Version:** 15
   - **Plan:** Free (for testing)

3. Click **"Create Database"**

### 3.5 Connect Database to Web Service

After PostgreSQL is created:

1. Go back to your Web Service
2. In "Environment" section, you'll see `DATABASE_URL` appears
3. Add these variables:

```
DB_NAME=gym_management  # or your database name
DB_USER=postgres
DB_HOST=your-db-host.onrender.com
DB_PORT=5432
```

(Render will provide the exact values in PostgreSQL dashboard)

### 3.6 Deploy!

1. Scroll down and click **"Create Web Service"**
2. Watch the build process in the logs
3. Wait for status to turn green: **"Live"**
4. You'll get a URL like: `https://gym-management-api.onrender.com`

✅ Your API is now live!

---

## STEP 4: Verify Deployment (2 minutes)

### Test Your API

**Test Login Endpoint:**
```bash
curl -X POST https://gym-management-api.onrender.com/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"superadmin@gym.com","password":"SuperAdmin@123"}'
```

**Expected Response:**
```json
{
  "access": "eyJ0b2...",
  "refresh": "eyJ0b2...",
  "user": {
    "id": 1,
    "email": "superadmin@gym.com",
    "role": "super_admin"
  }
}
```

### Access Key URLs

Once deployed, these URLs will work:

- **API Base:** `https://gym-management-api.onrender.com/api/v1/`
- **Admin Panel:** `https://gym-management-api.onrender.com/admin/`
- **Swagger Docs:** `https://gym-management-api.onrender.com/api/swagger/`
- **ReDoc:** `https://gym-management-api.onrender.com/api/redoc/`

### Test with Postman

1. Open Postman
2. Import: `postman/Gym_Management_API.postman_collection.json`
3. Update environment variable:
   - `{{base_url}}` = `https://gym-management-api.onrender.com`
4. Test endpoints!

---

## STEP 5: Set Up Test Data (Optional)

Option A: Create via API
```bash
curl -X POST https://gym-management-api.onrender.com/api/v1/users/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email":"newuser@gym.com",
    "first_name":"John",
    "last_name":"Doe",
    "password":"Password@123",
    "password_confirm":"Password@123",
    "role":"member",
    "gym_branch":1
  }'
```

Option B: Create via SSH (if needed)
1. In Render dashboard, click web service
2. Click **"Shell"** tab
3. Run: `python manage.py create_test_data`

---

## 📋 Test Users Available

After deployment, use these credentials:

```
Email: superadmin@gym.com
Password: SuperAdmin@123
Role: Super Admin

Email: manager1@gym.com
Password: Manager@123
Role: Gym Manager (Branch 1)

Email: trainer1@gym.com
Password: Trainer@123
Role: Trainer (Branch 1)

Email: member1@gym.com
Password: Member@123
Role: Member (Branch 1)
```

---

## 🎯 API Endpoints to Test

### Authentication
- `POST /api/v1/auth/login/` - Login
- `POST /api/v1/auth/refresh/` - Refresh token
- `GET /api/v1/auth/profile/` - Get profile

### Users
- `GET /api/v1/users/` - List users
- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/{id}/` - Get user
- `PATCH /api/v1/users/{id}/` - Update user

### Gym Branches
- `GET /api/v1/gym-branches/` - List branches
- `POST /api/v1/gym-branches/` - Create branch (super admin only)
- `GET /api/v1/gym-branches/{id}/` - Get branch

### Workout Plans
- `GET /api/v1/workout-plans/` - List plans
- `POST /api/v1/workout-plans/` - Create plan (trainer only)
- `GET /api/v1/workout-plans/{id}/` - Get plan
- `PATCH /api/v1/workout-plans/{id}/` - Update plan (owner only)

### Workout Tasks
- `GET /api/v1/workout-tasks/` - List tasks
- `POST /api/v1/workout-tasks/` - Create task (trainer only)
- `GET /api/v1/workout-tasks/{id}/` - Get task
- `PATCH /api/v1/workout-tasks/{id}/` - Update task status

### Activity Logs
- `GET /api/v1/activity-logs/` - List activities (super admin only)

---

## ⚠️ Troubleshooting

### Issue: Build Failed
**Solution:**
1. Check build logs in Render dashboard
2. Verify all dependencies in `requirements.txt`
3. Check for Python syntax errors
4. Ensure `Procfile` exists

### Issue: 502 Bad Gateway
**Solution:**
1. Check web service logs
2. Verify PostgreSQL is running
3. Check database connection string
4. Restart web service: Render dashboard → Service → "Restart"

### Issue: Database Connection Error
**Solution:**
1. Verify PostgreSQL service is "Live"
2. Check `DATABASE_URL` environment variable
3. Ensure `DB_ENGINE=django.db.backends.postgresql`
4. Check database credentials

### Issue: Static Files Not Found (Admin CSS)
**Solution:**
For API-only, not critical. If needed:
```bash
# In Render shell
python manage.py collectstatic
```

---

## 📊 Performance & Limits

### Free Tier (Default)
- Web Service: 512MB RAM
- Spins down after 15 min inactivity
- PostgreSQL: 90-day retention

### For Production
- Upgrade to paid plans
- Add Redis for caching
- Configure CDN
- Set up monitoring

---

## 📈 Next Steps

1. ✅ Code pushed to GitHub
2. ✅ Deployed to Render
3. ✅ API is live and public
4. Share your public URL: `https://gym-management-api.onrender.com`
5. Test with Postman collection
6. Monitor logs and performance
7. Optional: Set up custom domain

---

## 🔗 Important Links

- **Your Live API:** https://gym-management-api.onrender.com
- **GitHub Repository:** https://github.com/YOUR_USERNAME/gym-management-api
- **Render Dashboard:** https://dashboard.render.com
- **API Documentation:** https://gym-management-api.onrender.com/api/docs
- **Admin Panel:** https://gym-management-api.onrender.com/admin

---

## ✨ Deployment Complete!

Your API is now:
- ✅ Live on the internet
- ✅ Publicly accessible
- ✅ Using PostgreSQL database
- ✅ Properly configured
- ✅ Ready for testing

**Estimated Time:** 15 minutes total
**Status:** 🚀 DEPLOYED

---

## Support & Questions

- Render Documentation: https://render.com/docs
- Django Documentation: https://docs.djangoproject.com
- REST Framework Docs: https://www.django-rest-framework.org/
- This Project Documentation: See other markdown files

**Happy deploying! 🎉**
