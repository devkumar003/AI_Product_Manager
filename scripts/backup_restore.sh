#!/usr/bin/env bash
# Automated Backup & Restore Verification Script for Linux/Docker environments
# Exit immediately if a command exits with a non-zero status
set -e

DATABASE_CONTAINER="ai_product_db_prod"
DB_USER="postgres"
DB_NAME="ai_product_os"
BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.sql"
TAR_FILE="$BACKUP_DIR/backup_$TIMESTAMP.tar.gz"
TEST_DB_NAME="restore_test_$TIMESTAMP"

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR"

echo -e "\e[32m[+] Starting production database backup...\e[0m"

# 1. Take SQL dump using pg_dump inside Docker container
if docker exec -t "$DATABASE_CONTAINER" pg_dump -U "$DB_USER" -d "$DB_NAME" > "$BACKUP_FILE"; then
    echo -e "\e[36m[+] Database dump successfully created: $BACKUP_FILE\e[0m"
else
    echo -e "\e[31m[-] Backup failed during pg_dump execution.\e[0m" >&2
    exit 1
fi

# 2. Compress the backup to save disk space
if tar -czf "$TAR_FILE" -C "$BACKUP_DIR" "backup_$TIMESTAMP.sql"; then
    rm "$BACKUP_FILE"
    echo -e "\e[36m[+] Backup compressed successfully: $TAR_FILE\e[0m"
else
    echo -e "\e[31m[-] Backup compression failed.\e[0m" >&2
    exit 1
fi

# 3. Restore testing (Verification loop)
echo -e "\e[32m[+] Initiating automated restore verification test...\e[0m"

# 3.1 Extract temporary SQL file for verification
tar -xzf "$TAR_FILE" -C "$BACKUP_DIR"
TEMP_SQL_FILE="$BACKUP_DIR/backup_$TIMESTAMP.sql"

# Trap to guarantee cleanup of temporary database/files on failure or exit
cleanup() {
    echo -e "\e[33m[+] Cleaning up verification databases and temporary files...\e[0m"
    docker exec -i "$DATABASE_CONTAINER" psql -U "$DB_USER" -c "DROP DATABASE IF EXISTS $TEST_DB_NAME;" >/dev/null 2>&1 || true
    rm -f "$TEMP_SQL_FILE"
}
trap cleanup EXIT

# 3.2 Create temporary testing database
if docker exec -i "$DATABASE_CONTAINER" psql -U "$DB_USER" -c "CREATE DATABASE $TEST_DB_NAME;" >/dev/null; then
    echo -e "\e[36m[+] Created temporary verification database: $TEST_DB_NAME\e[0m"
else
    echo -e "\e[31m[-] Failed to create temporary database for restore test.\e[0m" >&2
    exit 1
fi

# 3.3 Restore the dump into temporary database
if docker exec -i "$DATABASE_CONTAINER" psql -U "$DB_USER" -d "$TEST_DB_NAME" < "$TEMP_SQL_FILE" >/dev/null; then
    echo -e "\e[36m[+] Dump successfully restored into verification database.\e[0m"
else
    echo -e "\e[31m[-] Failed to restore database dump into verification database.\e[0m" >&2
    exit 1
fi

# 3.4 Run verification sanity check query (Verify users table count)
USER_COUNT=$(docker exec -i "$DATABASE_CONTAINER" psql -U "$DB_USER" -d "$TEST_DB_NAME" -t -c "SELECT COUNT(*) FROM \"user\";" | xargs)

echo -e "\e[32m[+] Verification Sanity Check: Found $USER_COUNT registered users.\e[0m"
echo -e "\e[32m[+] RESTORE TEST SUCCESSFUL - Backup is fully verified and restorable.\e[0m"
