# Heroku Deployment Guide - Gym Management API

## Prerequisites

1. **Heroku Account** - Sign up at https://www.heroku.com (free tier available)
2. **Heroku CLI** - Download from https://devcenter.heroku.com/articles/heroku-cli
3. **Git** - Already initialized in your project
4. **PostgreSQL Database** - Heroku provides free tier

## Step-by-Step Deployment

### Step 1: Install Heroku CLI

**Windows:**
```powershell
# Download and install from https://cli-assets.heroku.com/heroku-x64.exe
# Or use scoop/chocolatey
choco install heroku-cli
```

**Mac/Linux:**
```bash
curl https://cli-assets.heroku.com/install.sh | sh
```

### Step 2: Login to Heroku

```bash
heroku login
```

This will open your browser to authenticate. Log in with your Heroku account.

### Step 3: Create Heroku App

```bash
cd C:\Users\HP\Desktop\Gym-Management-Member-Workout-System
heroku create your-app-name
```

⚠️ **Replace `your-app-name` with a unique name** (e.g., `gym-management-api-xyz`)

**Note:** If successful, you'll get a public URL like: `https://gym-management-api-xyz.herokuapp.com`

### Step 4: Add PostgreSQL Database

```bash
heroku addons:create heroku-postgresql:hobby-dev
```

This automatically sets the `DATABASE_URL` environment variable.

### Step 5: Set Environment Variables

```bash
# Secret key (generate a new one for production)
heroku config:set SECRET_KEY=your-super-secret-key-here-change-this

# Debug mode (turn OFF in production)
heroku config:set DEBUG=False

# Allowed hosts
heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com,localhost

# Database
heroku config:set DB_ENGINE=django.db.backends.postgresql
```

### Step 6: Configure Settings for Heroku

The settings.py file needs one update for Heroku. Run this command:

```bash
heroku config:set DJANGO_SETTINGS_MODULE=gym_management.settings
```

### Step 7: Deploy to Heroku

```bash
git push heroku main
```

This will:
1. Push your code to Heroku
2. Run migrations automatically
3. Deploy the app

**Expected Output:**
```
remote: -----> Building on the Heroku-20 stack
remote: -----> Using buildpack: heroku/python
...
remote: Verifying deploy... done.
remote: https://gym-management-api-xyz.herokuapp.com deployed to Heroku
```

### Step 8: Create Test Users

```bash
heroku run python manage.py create_test_data
```

This creates test users in the Heroku database.

### Step 9: Create Admin User (Optional)

```bash
heroku run python manage.py createsuperuser
```

Follow the prompts to create an admin account.

## 🎉 Your Hosted API is Live!

After deployment, your API will be accessible at:

```
https://your-app-name.herokuapp.com/api/v1/
```

### Access Points:

- **API Base:** `https://your-app-name.herokuapp.com/api/v1/`
- **Admin Panel:** `https://your-app-name.herokuapp.com/admin/`
- **API Docs:** `https://your-app-name.herokuapp.com/api/docs/`
- **Login Endpoint:** `https://your-app-name.herokuapp.com/api/v1/auth/login/`

## Testing Your Deployed API

### 1. Test Login

```bash
# Using PowerShell
$response = Invoke-WebRequest -Uri "https://your-app-name.herokuapp.com/api/v1/auth/login/" `
  -Method POST `
  -Body '{"email":"superadmin@gym.com","password":"SuperAdmin@123"}' `
  -ContentType "application/json"

$response.Content | ConvertFrom-Json | ConvertTo-Json
```

### 2. Update Postman Collection

In your Postman collection, update the `base_url` variable:
- **Before:** `http://localhost:8000`
- **After:** `https://your-app-name.herokuapp.com`

Then test all endpoints with your deployed API.

## Monitoring & Logs

### View Logs

```bash
heroku logs --tail
```

### View App Status

```bash
heroku ps
```

### Open App in Browser

```bash
heroku open
```

## Troubleshooting

### Issue: "Application error" page

**Solution:** Check logs
```bash
heroku logs --tail
```

### Issue: "Invalid DATABASE_URL"

**Solution:** Ensure PostgreSQL addon is attached
```bash
heroku addons
```

### Issue: "502 Bad Gateway"

**Solution:** Restart the app
```bash
heroku restart
```

### Issue: Static files not loading

**Solution:** Collect static files
```bash
heroku run python manage.py collectstatic --noinput
```

## Environment Variables Reference

Your Heroku app should have these config variables:

```
DATABASE_URL          # Auto-set by PostgreSQL addon
DEBUG                 # False
SECRET_KEY            # Your production secret key
ALLOWED_HOSTS         # your-app-name.herokuapp.com
DJ ANGO_SETTINGS_MODULE # gym_management.settings
```

Check current config:
```bash
heroku config
```

## Scaling & Performance

### View Current Dynos

```bash
heroku ps
```

### Scale Up Web Dynos (if needed)

```bash
heroku ps:scale web=2
```

## Custom Domain (Optional)

To use your own domain:

```bash
heroku domains:add yourdomain.com
```

Then update your DNS settings according to Heroku's instructions.

## Useful Commands

```bash
# View app info
heroku info

# Stop/restart app
heroku ps:stop
heroku restart

# Remote shell
heroku run bash

# Database backup
heroku pg:backups:capture

# Clear database
heroku pg:reset DATABASE

# Deploy from specific branch
git push heroku feature-branch:main
```

## Cost Estimation

**Free Tier (Development):**
- Web dyno: Free (sleeps after 30 min inactivity)
- PostgreSQL: Free (10k rows max)
- Monthly cost: **$0**

**Hobby Tier (Production):**
- Web dyno: $7/month (always on)
- PostgreSQL: $9/month (10GB database)
- Monthly cost: **$16/month**

## Next Steps

1. ✅ Deploy to Heroku (completed above)
2. Test all API endpoints
3. Update Postman collection with public URL
4. Create documentation with public URL
5. Share API URL with reviewers

---

## Support

For issues:
- Heroku Docs: https://devcenter.heroku.com/
- Django Docs: https://docs.djangoproject.com/
- DRF Docs: https://www.django-rest-framework.org/

Your API is now live and accessible to anyone on the internet! 🚀
