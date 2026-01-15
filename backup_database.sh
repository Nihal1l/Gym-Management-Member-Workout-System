#!/bin/bash

# Database Dump and Backup Script

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Gym Management API - Database Dump Script ===${NC}\n"

# Determine database type and dump accordingly
DB_ENGINE=${DB_ENGINE:-"sqlite3"}

if [ "$DB_ENGINE" == "postgresql" ] || [ "$DB_ENGINE" == "django.db.backends.postgresql" ]; then
    echo -e "${YELLOW}PostgreSQL Database Detected${NC}"
    
    DB_NAME=${DB_NAME:-"gym_db"}
    DB_USER=${DB_USER:-"postgres"}
    DB_HOST=${DB_HOST:-"localhost"}
    DB_PORT=${DB_PORT:-"5432"}
    
    # Create dumps directory
    mkdir -p dumps
    
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    DUMP_FILE="dumps/gym_db_${TIMESTAMP}.sql"
    
    echo -e "${YELLOW}Creating PostgreSQL dump...${NC}"
    pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" > "$DUMP_FILE"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Database dump created: $DUMP_FILE${NC}"
        echo -e "${GREEN}✓ Size: $(du -h $DUMP_FILE | cut -f1)${NC}"
    else
        echo -e "${RED}✗ Failed to create database dump${NC}"
        exit 1
    fi
    
    # Also create a schema-only dump
    SCHEMA_FILE="dumps/gym_db_schema_${TIMESTAMP}.sql"
    echo -e "${YELLOW}Creating schema dump...${NC}"
    pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" --schema-only > "$SCHEMA_FILE"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Schema dump created: $SCHEMA_FILE${NC}"
    fi
    
    # Create CSV exports for data analysis
    echo -e "${YELLOW}Creating CSV exports...${NC}"
    mkdir -p dumps/csv
    
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "COPY gym_api_user TO STDOUT WITH CSV HEADER;" > dumps/csv/users.csv
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "COPY gym_api_gymbranch TO STDOUT WITH CSV HEADER;" > dumps/csv/gym_branches.csv
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "COPY gym_api_workoutplan TO STDOUT WITH CSV HEADER;" > dumps/csv/workout_plans.csv
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "COPY gym_api_workoutask TO STDOUT WITH CSV HEADER;" > dumps/csv/workout_tasks.csv
    
    echo -e "${GREEN}✓ CSV exports created in dumps/csv/${NC}"
    
else
    echo -e "${YELLOW}SQLite Database Detected${NC}"
    
    DB_PATH=${DB_NAME:-"db.sqlite3"}
    
    mkdir -p dumps
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    DUMP_FILE="dumps/gym_db_${TIMESTAMP}.sqlite3"
    
    echo -e "${YELLOW}Backing up SQLite database...${NC}"
    cp "$DB_PATH" "$DUMP_FILE"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Database backup created: $DUMP_FILE${NC}"
        echo -e "${GREEN}✓ Size: $(du -h $DUMP_FILE | cut -f1)${NC}"
    else
        echo -e "${RED}✗ Failed to backup database${NC}"
        exit 1
    fi
    
    # Create JSON dump
    echo -e "${YELLOW}Creating JSON dump...${NC}"
    JSON_FILE="dumps/gym_db_${TIMESTAMP}.json"
    python manage.py dumpdata > "$JSON_FILE"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ JSON dump created: $JSON_FILE${NC}"
        echo -e "${GREEN}✓ Size: $(du -h $JSON_FILE | cut -f1)${NC}"
    fi
fi

echo -e "\n${GREEN}=== Database Dump Complete ===${NC}"
echo -e "${YELLOW}Backup location: $(pwd)/dumps/${NC}"
echo -e "\n${YELLOW}To restore from backup:${NC}"
if [ "$DB_ENGINE" == "postgresql" ] || [ "$DB_ENGINE" == "django.db.backends.postgresql" ]; then
    echo -e "psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME < $DUMP_FILE"
else
    echo -e "cp $DUMP_FILE db.sqlite3"
    echo -e "or"
    echo -e "python manage.py loaddata $JSON_FILE"
fi
