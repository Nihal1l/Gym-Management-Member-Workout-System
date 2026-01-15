# Database Dumps & Backups

This directory contains database dumps and backups for the Gym Management API.

## Files

### 1. `db_backup.sqlite3` (Primary Backup)
**Format:** SQLite 3 Database File  
**Size:** ~200 KB  
**Contains:** Complete schema + test data  
**Updated:** January 15, 2026

#### To Restore:
```bash
# Windows
copy db_backup.sqlite3 ..\db.sqlite3
python manage.py migrate

# macOS/Linux
cp db_backup.sqlite3 ../db.sqlite3
python manage.py migrate
```

### 2. `db_schema.sql` (Schema Definition)
**Format:** SQL DDL  
**Size:** ~4 KB  
**Contains:** CREATE TABLE statements and indexes  
**Updated:** January 15, 2026

#### To Use:
```bash
# SQLite
sqlite3 db.sqlite3 < db_schema.sql

# PostgreSQL
psql -U postgres -d gym_db -f db_schema.sql
```

### 3. `db_dump.json` (Data Dump - when available)
**Format:** JSON (Django dumpdata format)  
**Contains:** Gym API data only (excludes auth tables)  
**Note:** Generated via `python manage.py dumpdata gym_api`

#### To Restore:
```bash
python manage.py loaddata db_dump.json
```

## How to Create Backups

### SQLite Backup
```bash
# Manual backup
cp db.sqlite3 dumps/db_backup_$(date +%Y%m%d_%H%M%S).sqlite3

# Or use the backup script
bash backup_database.sh
```

### JSON Dump
```bash
# Export gym_api models only
python manage.py dumpdata gym_api --indent 2 > dumps/db_dump.json

# Export specific app models
python manage.py dumpdata gym_api.User --indent 2 > dumps/users.json
```

### PostgreSQL Dump
```bash
# Full database backup
pg_dump -U postgres -d gym_db > dumps/gym_db_backup.sql

# Schema only
pg_dump -U postgres -d gym_db --schema-only > dumps/gym_db_schema.sql

# Data only
pg_dump -U postgres -d gym_db --data-only > dumps/gym_db_data.sql
```

## Database Configuration

All backups are created from the configured database in `.env`:

```bash
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
```

For PostgreSQL, update `.env` with:
```bash
DB_ENGINE=django.db.backends.postgresql
DB_NAME=gym_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

## Test Data

The backups contain the following test data (created by `create_test_data` command):

### Users
- 1 Super Admin
- 2 Gym Managers
- 3 Trainers
- 3 Members

### Data
- 2 Gym Branches
- 2 Workout Plans
- 6 Workout Tasks

See [QUICK_START.md](../QUICK_START.md) for test credentials.

## Automated Backup Script

Use `backup_database.sh` to automatically:
1. Create timestamped backups
2. Generate schema dumps
3. Export CSV files
4. Include restore instructions

```bash
bash ../backup_database.sh
```

## Retention Policy

- **Development:** Keep last 5 backups
- **Production:** Keep daily backups for 30 days, weekly for 6 months

## Restore Procedure

### From SQLite Backup (Quickest)
```bash
# Stop the server
# Restore database
cp dumps/db_backup.sqlite3 db.sqlite3
# Restart server
python manage.py runserver
```

### From JSON Dump
```bash
# This preserves IDs and relationships
python manage.py loaddata dumps/db_dump.json
```

### From Fresh Schema
```bash
# Reset database (caution!)
rm db.sqlite3
python manage.py migrate
python manage.py create_test_data
```

## Troubleshooting

### "Unable to serialize database" error
**Solution:** Exclude problematic tables:
```bash
python manage.py dumpdata gym_api --exclude auth --indent 2 > db_dump.json
```

### "no such table" error
**Solution:** Run migrations first:
```bash
python manage.py migrate
```

### SQLite locked database error
**Solution:** Ensure no other process is using the database, then try again:
```bash
# Check for locks (on Unix)
lsof db.sqlite3

# Force close if needed (use with caution)
rm db.sqlite3-journal
```

## Verification

After restoring, verify the database:

```bash
# Check table count
python manage.py dbshell
SELECT COUNT(*) FROM gym_api_user;
SELECT COUNT(*) FROM gym_api_gymbranch;
SELECT COUNT(*) FROM gym_api_workoutplan;
SELECT COUNT(*) FROM gym_api_workoutask;

# Or use Django ORM
python manage.py shell
>>> from gym_api.models import User, GymBranch
>>> User.objects.count()
>>> GymBranch.objects.count()
```

## Security

⚠️ **Important:** These backups contain test data. For production:
- Never commit backups to version control
- Store backups in secure locations
- Use strong encryption for sensitive data
- Regularly test restore procedures
- Keep backups off-site

## Support

For issues, see:
- [DATABASE_SCHEMA.md](../DATABASE_SCHEMA.md) - Schema details
- [README.md](../README.md) - Database section
- [DEVELOPMENT_NOTES.md](../DEVELOPMENT_NOTES.md) - Troubleshooting

---

**Last Updated:** January 15, 2026  
**Database Version:** 1.0
