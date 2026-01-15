# Quick Heroku Deployment - 10 Minutes

## 1. Install Heroku CLI
Download from: https://devcenter.heroku.com/articles/heroku-cli

**Windows (PowerShell):**
```powershell
choco install heroku-cli
# or download installer from the link above
```

## 2. Login to Heroku
```bash
heroku login
```

## 3. Create Your App
```bash
heroku create your-unique-app-name
# Example: heroku create gym-api-2024
```

**Save your app URL!** It will look like: `https://gym-api-2024.herokuapp.com`

## 4. Add PostgreSQL Database
```bash
heroku addons:create heroku-postgresql:hobby-dev
```

## 5. Set Environment Variables
```bash
# Generate a new secret key and use it
heroku config:set SECRET_KEY=your-super-long-secret-key-here-use-something-unique

heroku config:set DEBUG=False

heroku config:set ALLOWED_HOSTS=gym-api-2024.herokuapp.com
```

## 6. Deploy
```bash
git push heroku main
```

Wait for deployment to complete (2-5 minutes).

## 7. Create Test Users
```bash
heroku run python manage.py create_test_data
```

## ✅ Done!

Your API is now live at: `https://your-app-name.herokuapp.com`

### Test It:
```powershell
$response = Invoke-WebRequest -Uri "https://your-app-name.herokuapp.com/api/v1/auth/login/" `
  -Method POST `
  -Body '{"email":"superadmin@gym.com","password":"SuperAdmin@123"}' `
  -ContentType "application/json"

$response.Content
```

### Access Points:
- API: `https://your-app-name.herokuapp.com/api/v1/`
- Admin: `https://your-app-name.herokuapp.com/admin/`
- Docs: `https://your-app-name.herokuapp.com/api/docs/`

---

## Troubleshooting

**Check logs:**
```bash
heroku logs --tail
```

**Restart app:**
```bash
heroku restart
```

**View database:**
```bash
heroku pg:info
```

For more help, see `HEROKU_DEPLOYMENT.md` for detailed instructions.
