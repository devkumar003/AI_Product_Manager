# Automated Backup & Restore Verification Script for Windows/Docker environments
# Run this script periodically via Windows Task Scheduler or CI/CD pipelines.

$DatabaseContainer = "ai_product_db_prod"
$DbUser = "postgres"
$DbName = "ai_product_os"
$BackupDir = "./backups"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupFile = "$BackupDir/backup_$Timestamp.sql"
$ZipFile = "$BackupDir/backup_$Timestamp.zip"
$TestDbName = "restore_test_$Timestamp"

# Ensure backup directory exists
if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir | Out-Null
}

Write-Host "[+] Starting production database backup..." -ForegroundColor Green

# 1. Take SQL dump using pg_dump inside Docker container
try {
    # We pipe through Out-File with OEM/UTF-8 encoding or redirect natively
    & docker exec -i $DatabaseContainer pg_dump -U $DbUser -d $DbName > $BackupFile
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to extract database dump via pg_dump."
    }
    Write-Host "[+] Database dump successfully created: $BackupFile" -ForegroundColor Cyan
} catch {
    Write-Error "[-] Backup failed: $_"
    exit 1
}

# 2. Compress the backup to save disk space
try {
    Compress-Archive -Path $BackupFile -DestinationPath $ZipFile -Force
    Remove-Item $BackupFile
    Write-Host "[+] Backup compressed successfully: $ZipFile" -ForegroundColor Cyan
} catch {
    Write-Error "[-] Compression failed: $_"
    exit 1
}

# 3. Restore testing (Verification loop)
Write-Host "[+] Initiating automated restore verification test..." -ForegroundColor Green

try {
    # 3.1 Unzip the backup to get SQL file for restore
    Expand-Archive -Path $ZipFile -DestinationPath $BackupDir -Force
    $TempSqlFile = "$BackupDir/backup_$Timestamp.sql"

    # 3.2 Create temporary testing database
    & docker exec -i $DatabaseContainer psql -U $DbUser -c "CREATE DATABASE $TestDbName;"
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to create temporary database for restore test."
    }
    Write-Host "[+] Created temporary verification database: $TestDbName" -ForegroundColor Cyan

    # 3.3 Restore the dump into temporary database
    & docker exec -i $DatabaseContainer psql -U $DbUser -d $TestDbName < $TempSqlFile
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to restore database dump into $TestDbName."
    }
    Write-Host "[+] Dump successfully restored into verification database." -ForegroundColor Cyan

    # 3.4 Run verification sanity check query (Verify users table counts)
    $UserCountOutput = & docker exec -i $DatabaseContainer psql -U $DbUser -d $TestDbName -t -c "SELECT COUNT(*) FROM \"user\";"
    if ($LASTEXITCODE -ne 0) {
        throw "Sanity check query failed."
    }
    
    $UserCount = $UserCountOutput.Trim()
    Write-Host "[+] Verification Sanity Check: Found $UserCount registered users." -ForegroundColor Green
    Write-Host "[+] RESTORE TEST SUCCESSFUL - Backup is fully verified and restorable." -ForegroundColor Green
} catch {
    Write-Error "[-] Restore test failed: $_"
    $TestFailed = $true
} finally {
    # 3.5 Cleanup temporary database
    Write-Host "[+] Cleaning up verification databases and temporary files..." -ForegroundColor Yellow
    & docker exec -i $DatabaseContainer psql -U $DbUser -c "DROP DATABASE IF EXISTS $TestDbName;"
    if (Test-Path $TempSqlFile) {
        Remove-Item $TempSqlFile
    }
    
    if ($TestFailed) {
        exit 1
    } else {
        exit 0
    }
}
