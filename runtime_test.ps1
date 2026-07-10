$ErrorActionPreference = "Continue"
$base = "http://127.0.0.1:8000/api/v1"
$results = @()

function Test-Endpoint {
    param($Name, $Method, $Url, $Body, $Headers, $ContentType)
    $start = Get-Date
    try {
        $params = @{Uri=$Url; Method=$Method; Headers=$Headers}
        if ($Body) { $params.Body = $Body }
        if ($ContentType) { $params.ContentType = $ContentType } else { $params.ContentType = "application/json" }
        $resp = Invoke-RestMethod @params
        $ms = ((Get-Date) - $start).TotalMilliseconds
        Write-Host "PASS | $Name | ${ms}ms"
        return @{Name=$Name; Status="PASS"; Ms=[math]::Round($ms); Data=$resp}
    } catch {
        $ms = ((Get-Date) - $start).TotalMilliseconds
        $err = $_.Exception.Message.Substring(0, [Math]::Min(200, $_.Exception.Message.Length))
        Write-Host "FAIL | $Name | $err"
        return @{Name=$Name; Status="FAIL"; Ms=[math]::Round($ms); Error=$err}
    }
}

# === AUTH TESTS ===
Write-Host "`n=== AUTHENTICATION ==="
# Login
$loginResult = Test-Endpoint -Name "Login" -Method POST -Url "$base/auth/login" `
    -Body "username=runtime_qa@example.com&password=TestPassword123!" `
    -ContentType "application/x-www-form-urlencoded"

if ($loginResult.Status -eq "PASS") {
    $token = $loginResult.Data.access_token
    $refreshToken = $loginResult.Data.refresh_token
} else {
    # Try signup first
    $signup = Test-Endpoint -Name "Signup" -Method POST -Url "$base/auth/signup" `
        -Body '{"full_name":"Runtime Tester","username":"runtime_qa2","email":"runtime_qa2@example.com","password":"TestPassword123!"}'
    $loginResult = Test-Endpoint -Name "Login-Retry" -Method POST -Url "$base/auth/login" `
        -Body "username=runtime_qa2@example.com&password=TestPassword123!" `
        -ContentType "application/x-www-form-urlencoded"
    $token = $loginResult.Data.access_token
    $refreshToken = $loginResult.Data.refresh_token
}

$h = @{Authorization="Bearer $token"}

# Token Refresh
Test-Endpoint -Name "Token-Refresh" -Method POST -Url "$base/auth/refresh?refresh_token=$refreshToken" -Headers $h

# Get Profile
$profile = Test-Endpoint -Name "Get-Profile" -Method GET -Url "$base/users/me" -Headers $h

# Logout
Test-Endpoint -Name "Logout" -Method POST -Url "$base/auth/logout" -Headers $h

# Health Check
Test-Endpoint -Name "Health-Check" -Method GET -Url "$base/health"

# === WORKSPACE DISCOVERY ===
Write-Host "`n=== WORKSPACE DISCOVERY ==="
$userId = $profile.Data.id

# Get workspaces via user endpoint
$wsResp = Test-Endpoint -Name "Get-User-Workspaces" -Method GET -Url "$base/users/me/workspaces" -Headers $h
$wsId = $null
if ($wsResp.Status -eq "PASS" -and $wsResp.Data.Count -gt 0) {
    $wsId = $wsResp.Data[0].id
    Write-Host "  Workspace ID: $wsId"
} else {
    # Try organizations route
    $orgResp = Test-Endpoint -Name "Get-Orgs" -Method GET -Url "$base/users/me/organizations" -Headers $h
    if ($orgResp.Status -eq "PASS") {
        $orgId = $orgResp.Data[0].id
        $wsListResp = Test-Endpoint -Name "Get-Org-Workspaces" -Method GET -Url "$base/workspaces/$orgId" -Headers $h
        if ($wsListResp.Status -eq "PASS" -and $wsListResp.Data.Count -gt 0) {
            $wsId = $wsListResp.Data[0].id
            Write-Host "  Workspace ID: $wsId"
        }
    }
}

if (-not $wsId) {
    Write-Host "WARN: No workspace found, trying DB query..."
    # Fallback: query DB directly
    $dbPath = "c:\Users\mansu\Desktop\AI_Product_Manager\backend\development.db"
    if (Test-Path $dbPath) {
        $wsId = & python -c "import sqlite3; c=sqlite3.connect(r'$dbPath'); r=c.execute('SELECT id FROM workspaces LIMIT 1').fetchone(); print(r[0] if r else '')" 2>$null
        Write-Host "  DB Workspace ID: $wsId"
    }
}

if (-not $wsId) { Write-Host "FATAL: Cannot proceed without workspace ID"; exit 1 }

# === PROJECT TESTS ===
Write-Host "`n=== PROJECTS ==="
$projBody = '{"name":"AI Resume Builder","description":"An AI-powered resume builder","slug":"ai-resume-builder","status":"Planning","priority":"High"}'
$projCreate = Test-Endpoint -Name "Create-Project" -Method POST -Url "$base/projects/$wsId" -Headers $h -Body $projBody
$projId = if ($projCreate.Status -eq "PASS") { $projCreate.Data.id } else { $null }

Test-Endpoint -Name "List-Projects" -Method GET -Url "$base/projects/$wsId" -Headers $h

if ($projId) {
    Test-Endpoint -Name "Get-Project" -Method GET -Url "$base/projects/$wsId/$projId" -Headers $h
    Test-Endpoint -Name "Project-Dashboard" -Method GET -Url "$base/projects/$wsId/$projId/dashboard" -Headers $h
}

# === DOCUMENT TESTS ===
Write-Host "`n=== DOCUMENTS ==="
$docBody = '{"name":"Test PRD Doc","category":"prd","content":"# PRD for AI Resume Builder"}'
$docCreate = Test-Endpoint -Name "Create-Document" -Method POST -Url "$base/documents/$wsId" -Headers $h -Body $docBody
Test-Endpoint -Name "List-Documents" -Method GET -Url "$base/documents/$wsId" -Headers $h

# === AI ORCHESTRATOR TEST ===
Write-Host "`n=== AI ORCHESTRATOR (Multi-Agent Pipeline) ==="
$aiBody = '{"idea":"I want to build an AI Resume Builder that uses AI to generate professional resumes","industry":"HR Tech"}'
$aiResult = Test-Endpoint -Name "AI-Generate-Product" -Method POST -Url "$base/ai/$wsId/generate" -Headers $h -Body $aiBody
if ($aiResult.Status -eq "PASS") {
    Write-Host "  Refined Title: $($aiResult.Data.refined_idea.refined_title)"
    Write-Host "  PRD Title: $($aiResult.Data.prd.prd_title)"
    Write-Host "  User Stories Count: $($aiResult.Data.prd.user_stories.Count)"
    Write-Host "  API Endpoints Count: $($aiResult.Data.architecture.api_endpoints.Count)"
    Write-Host "  DB Schema DDL Count: $($aiResult.Data.architecture.database_schema_ddl.Count)"
}

# === AI CHAT TEST ===
Write-Host "`n=== AI CHAT ==="
$chatBody = '{"message":"Add payment gateway to the AI Resume Builder. What requirements, database changes, API changes, and frontend changes are needed?","model":"gpt-4o","provider":"openai"}'
Test-Endpoint -Name "AI-Chat" -Method POST -Url "$base/ai/$wsId/chat" -Headers $h -Body $chatBody

# === PLANNING ENGINE TESTS ===
Write-Host "`n=== PLANNING ENGINE ==="
# Goals
$goalBody = '{"name":"Launch MVP","description":"Ship the AI Resume Builder MVP in Q3","type":"Product","status":"Open","progress":0.0}'
$goalResult = Test-Endpoint -Name "Create-Goal" -Method POST -Url "$base/planning/goals?workspace_id=$wsId" -Headers $h -Body $goalBody
$goalId = if ($goalResult.Status -eq "PASS") { $goalResult.Data.id } else { $null }
Test-Endpoint -Name "List-Goals" -Method GET -Url "$base/planning/goals?workspace_id=$wsId" -Headers $h

# Mission Planner
if ($goalId) {
    $missionBody = "{`"title`":`"Q3 Launch Mission`",`"goal_ids`":[`"$goalId`"]}"
    Test-Endpoint -Name "Generate-Mission" -Method POST -Url "$base/planning/missions?workspace_id=$wsId" -Headers $h -Body $missionBody
}

# Backlog Decomposition
$backlogBody = '{"vision":"Build an AI-powered resume builder with template selection, AI content generation, PDF export, and job matching"}'
$backlogResult = Test-Endpoint -Name "AI-Backlog-Decompose" -Method POST -Url "$base/planning/backlog/generate?workspace_id=$wsId" -Headers $h -Body $backlogBody
if ($backlogResult.Status -eq "PASS") {
    Write-Host "  Backlog Items Created: $($backlogResult.Data.Count)"
}

# List Backlog
Test-Endpoint -Name "List-Backlog" -Method GET -Url "$base/planning/backlog/items?workspace_id=$wsId" -Headers $h

# Dependencies
Test-Endpoint -Name "Detect-Dependencies" -Method POST -Url "$base/planning/dependencies/detect?workspace_id=$wsId" -Headers $h -Body "{}"

# AI Scheduler
Test-Endpoint -Name "AI-Scheduler" -Method POST -Url "$base/planning/scheduler/schedule?workspace_id=$wsId" -Headers $h -Body "{}"

# Scenario Simulation
$simBody = '{"name":"MVP Launch Sim","vision":"AI Resume Builder with 3 core features in 12 weeks"}'
Test-Endpoint -Name "Scenario-Simulation" -Method POST -Url "$base/planning/simulations?workspace_id=$wsId" -Headers $h -Body $simBody

# Resource Planner (needs an epic ID)
Test-Endpoint -Name "List-Simulations" -Method GET -Url "$base/planning/simulations?workspace_id=$wsId" -Headers $h

# Analytics
Test-Endpoint -Name "Planning-Analytics" -Method GET -Url "$base/planning/analytics/latest?workspace_id=$wsId" -Headers $h

# Templates
Test-Endpoint -Name "List-Templates" -Method GET -Url "$base/planning/intelligence/templates" -Headers $h

# Roadmap
Test-Endpoint -Name "Get-Roadmap" -Method GET -Url "$base/planning/intelligence/roadmap?workspace_id=$wsId" -Headers $h

# Context Compression
$compressBody = '{"text":"The AI Resume Builder is a comprehensive platform that helps job seekers create professional resumes using artificial intelligence. It analyzes job descriptions and tailors resume content accordingly.","target_summary_words":50}'
Test-Endpoint -Name "Context-Compression" -Method POST -Url "$base/planning/compress/text" -Headers $h -Body $compressBody

# === EXECUTIVE REPORTS ===
Write-Host "`n=== EXECUTIVE BOARDROOM ==="
$ceoBody = '{"product_idea":"AI Resume Builder","target_industry":"HR Tech","competitors":["Resume.io","Zety","Canva"],"budget":50000}'
Test-Endpoint -Name "CEO-Report" -Method POST -Url "$base/executive/$wsId/ceo/generate" -Headers $h -Body $ceoBody

$ctoBody = '{"product_spec":"AI Resume Builder with NLP parsing and PDF generation","preferred_cloud":"AWS","compliance_needs":["GDPR","SOC2"]}'
Test-Endpoint -Name "CTO-Report" -Method POST -Url "$base/executive/$wsId/cto/generate" -Headers $h -Body $ctoBody

$cooBody = '{"sprint_name":"Sprint 1 - Foundation","team_members":["Alice","Bob","Charlie"],"total_budget":50000}'
Test-Endpoint -Name "COO-Report" -Method POST -Url "$base/executive/$wsId/coo/generate" -Headers $h -Body $cooBody

# === DEVELOPMENT PIPELINES ===
Write-Host "`n=== DEVELOPMENT PIPELINES ==="
$prdPipe = '{"target_name":"AI Resume Builder","prompt":"Build a resume builder with AI content generation, multiple templates, PDF/DOCX export"}'
Test-Endpoint -Name "Pipeline-PRD" -Method POST -Url "$base/development/pipelines/execute?workspace_id=$wsId&pipeline_type=prd" -Headers $h -Body $prdPipe

$dbPipe = '{"target_name":"AI Resume Builder","prompt":"Users, resumes, templates, AI generations, job descriptions, exports"}'
Test-Endpoint -Name "Pipeline-Database" -Method POST -Url "$base/development/pipelines/execute?workspace_id=$wsId&pipeline_type=database" -Headers $h -Body $dbPipe

$apiPipe = '{"target_name":"AI Resume Builder","prompt":"CRUD resumes, generate content, export PDF, manage templates, user auth"}'
Test-Endpoint -Name "Pipeline-API" -Method POST -Url "$base/development/pipelines/execute?workspace_id=$wsId&pipeline_type=api" -Headers $h -Body $apiPipe

$backendPipe = '{"target_name":"AI Resume Builder","prompt":"FastAPI routes for resume CRUD, AI generation, PDF export"}'
Test-Endpoint -Name "Pipeline-Backend" -Method POST -Url "$base/development/pipelines/execute?workspace_id=$wsId&pipeline_type=backend" -Headers $h -Body $backendPipe

$frontendPipe = '{"target_name":"AI Resume Builder","prompt":"Next.js pages for resume editor, template gallery, export page"}'
Test-Endpoint -Name "Pipeline-Frontend" -Method POST -Url "$base/development/pipelines/execute?workspace_id=$wsId&pipeline_type=frontend" -Headers $h -Body $frontendPipe

$archPipe = '{"target_name":"AI Resume Builder","prompt":"Microservices architecture with AI engine, PDF service, template service"}'
Test-Endpoint -Name "Pipeline-Architecture" -Method POST -Url "$base/development/pipelines/execute?workspace_id=$wsId&pipeline_type=architecture" -Headers $h -Body $archPipe

$unitPipe = '{"target_name":"AI Resume Builder","prompt":"def create_resume(): pass\ndef generate_content(): pass"}'
Test-Endpoint -Name "Pipeline-UnitTest" -Method POST -Url "$base/development/pipelines/execute?workspace_id=$wsId&pipeline_type=unittest" -Headers $h -Body $unitPipe

$docPipe = '{"target_name":"AI Resume Builder","prompt":"Complete user guide with setup, API reference, deployment"}'
Test-Endpoint -Name "Pipeline-Documentation" -Method POST -Url "$base/development/pipelines/execute?workspace_id=$wsId&pipeline_type=documentation" -Headers $h -Body $docPipe

# === BROKEN FRONTEND ENDPOINTS ===
Write-Host "`n=== TESTING NON-EXISTENT ENDPOINTS (Frontend references) ==="
$engBody = '{"engine_name":"idea_analysis","input_data":{"idea":"AI Resume Builder"}}'
Test-Endpoint -Name "GHOST-engines-execute" -Method POST -Url "$base/ai/engines/execute" -Headers $h -Body $engBody

$wfBody = '{"workflow_name":"prd_generation","context":{"idea":"AI Resume Builder"}}'
Test-Endpoint -Name "GHOST-workflows-execute" -Method POST -Url "$base/ai/workflows/execute" -Headers $h -Body $wfBody

# === SEARCH ===
Write-Host "`n=== SEARCH ==="
Test-Endpoint -Name "Global-Search" -Method GET -Url "$base/search/$wsId`?q=resume" -Headers $h

# === SECURITY TESTS ===
Write-Host "`n=== SECURITY ==="
# No auth
Test-Endpoint -Name "SEC-No-Auth" -Method GET -Url "$base/projects/$wsId"
# Wrong workspace
$fakeWs = "00000000-0000-0000-0000-000000000000"
Test-Endpoint -Name "SEC-Wrong-Workspace" -Method GET -Url "$base/projects/$fakeWs" -Headers $h

Write-Host "`n=== ALL TESTS COMPLETE ==="
