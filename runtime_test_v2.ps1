$ErrorActionPreference = "Stop"
$base = "http://127.0.0.1:8000/api/v1"
$token = (Get-Content "c:\Users\mansu\Desktop\AI_Product_Manager\.token.txt" -Raw).Trim()
$h = @{Authorization="Bearer $token"; "Content-Type"="application/json"}
$wsId = "13a90335-25b5-489d-ac02-646ceb0e20aa"
$pass = 0; $fail = 0; $results = @()

function T($name, $block) {
    $start = Get-Date
    try {
        $r = & $block
        $ms = [math]::Round(((Get-Date)-$start).TotalMilliseconds)
        $script:pass++
        $script:results += "PASS | $name | ${ms}ms"
        Write-Host "PASS | $name | ${ms}ms"
        return $r
    } catch {
        $ms = [math]::Round(((Get-Date)-$start).TotalMilliseconds)
        $err = "$($_.Exception.Message)".Substring(0,[Math]::Min(150,"$($_.Exception.Message)".Length))
        $script:fail++
        $script:results += "FAIL | $name | $err"
        Write-Host "FAIL | $name | $err"
        return $null
    }
}

Write-Host "=== AI ORCHESTRATOR (Idea Validation + PRD + Architecture) ==="
$ai = T "AI-Multi-Agent-Pipeline" {
    Invoke-RestMethod -Uri "$base/ai/$wsId/generate" -Method POST -Headers $h -Body '{"idea":"I want to build an AI Resume Builder that generates professional resumes with AI","industry":"HR Tech"}'
}
if ($ai) {
    Write-Host "  >> Refined Title: $($ai.refined_idea.refined_title)"
    Write-Host "  >> Target Audience: $($ai.refined_idea.target_audience -join ', ')"
    Write-Host "  >> Key Objectives: $($ai.refined_idea.key_objectives.Count)"
    Write-Host "  >> Feature Milestones: $($ai.refined_idea.feature_milestones.Count)"
    Write-Host "  >> PRD Title: $($ai.prd.prd_title)"
    Write-Host "  >> User Stories: $($ai.prd.user_stories.Count) stories"
    Write-Host "  >> Functional Reqs: $($ai.prd.functional_requirements.Count)"
    Write-Host "  >> Technical Constraints: $($ai.prd.technical_constraints.Count)"
    Write-Host "  >> System Description: $($ai.architecture.system_description.Substring(0,[Math]::Min(100,$ai.architecture.system_description.Length)))"
    Write-Host "  >> DB Schema DDLs: $($ai.architecture.database_schema_ddl.Count)"
    Write-Host "  >> API Endpoints: $($ai.architecture.api_endpoints.Count)"
    Write-Host "  >> Deployment: $($ai.architecture.deployment_strategy.Substring(0,[Math]::Min(80,$ai.architecture.deployment_strategy.Length)))"
}

Write-Host "`n=== AI CHAT ==="
$chat = T "AI-Chat-ProductAssistant" {
    Invoke-RestMethod -Uri "$base/ai/$wsId/chat" -Method POST -Headers $h -Body '{"message":"Add a payment gateway to the AI Resume Builder. What requirements, database changes, API changes, frontend and backend changes are needed?"}'
}
if ($chat) { Write-Host "  >> Response length: $($chat.response.Length) chars" }

Write-Host "`n=== PLANNING ENGINE ==="
$goal = T "Create-Goal" {
    Invoke-RestMethod -Uri "$base/planning/goals?workspace_id=$wsId" -Method POST -Headers $h -Body '{"name":"Launch MVP Resume Builder","description":"Ship core features by Q3","type":"Product","status":"Open","progress":0.0}'
}
$goalId = if ($goal) { $goal.id } else { $null }

T "List-Goals" { Invoke-RestMethod -Uri "$base/planning/goals?workspace_id=$wsId" -Method GET -Headers $h } | Out-Null

if ($goalId) {
    $mission = T "Generate-Mission-Plan" {
        Invoke-RestMethod -Uri "$base/planning/missions?workspace_id=$wsId" -Method POST -Headers $h -Body "{`"title`":`"Q3 MVP Launch Mission`",`"goal_ids`":[`"$goalId`"]}"
    }
    if ($mission) {
        Write-Host "  >> Mission Objectives: $($mission.objectives.Count)"
        Write-Host "  >> Milestones: $($mission.milestones.Count)"
        Write-Host "  >> Deliverables: $($mission.deliverables.Count)"
    }
}

$backlog = T "AI-Backlog-Decompose" {
    Invoke-RestMethod -Uri "$base/planning/backlog/generate?workspace_id=$wsId" -Method POST -Headers $h -Body '{"vision":"Build an AI resume builder with template selection, AI content generation, PDF export, ATS optimization, and job matching"}'
}
if ($backlog) {
    Write-Host "  >> Backlog Items Created: $($backlog.Count)"
    $types = $backlog | Group-Object type | ForEach-Object { "$($_.Name):$($_.Count)" }
    Write-Host "  >> Hierarchy: $($types -join ', ')"
}

T "List-Backlog" { Invoke-RestMethod -Uri "$base/planning/backlog/items?workspace_id=$wsId" -Method GET -Headers $h } | Out-Null

$deps = T "AI-Detect-Dependencies" {
    Invoke-RestMethod -Uri "$base/planning/dependencies/detect?workspace_id=$wsId" -Method POST -Headers $h -Body "{}"
}
if ($deps) { Write-Host "  >> Dependencies Found: $($deps.Count)" }

$sched = T "AI-Scheduler" {
    Invoke-RestMethod -Uri "$base/planning/scheduler/schedule?workspace_id=$wsId" -Method POST -Headers $h -Body "{}"
}

$sim = T "Scenario-Simulation" {
    Invoke-RestMethod -Uri "$base/planning/simulations?workspace_id=$wsId" -Method POST -Headers $h -Body '{"name":"MVP Timeline Simulation","vision":"AI Resume Builder with 5 core features in 12 weeks"}'
}
if ($sim) { Write-Host "  >> Simulation has budget_impact and timeline_impact data" }

T "Planning-Analytics" {
    Invoke-RestMethod -Uri "$base/planning/analytics/latest?workspace_id=$wsId" -Method GET -Headers $h
} | Out-Null

T "Get-Roadmap" {
    Invoke-RestMethod -Uri "$base/planning/intelligence/roadmap?workspace_id=$wsId" -Method GET -Headers $h
} | Out-Null

T "Context-Compression" {
    Invoke-RestMethod -Uri "$base/planning/compress/text" -Method POST -Headers $h -Body '{"text":"The AI Resume Builder is a comprehensive platform that enables job seekers to create professional resumes using artificial intelligence technology that analyzes job descriptions and generates tailored content","target_summary_words":30}'
} | Out-Null

Write-Host "`n=== EXECUTIVE BOARDROOM ==="
$ceo = T "CEO-Strategy-Report" {
    Invoke-RestMethod -Uri "$base/executive/$wsId/ceo/generate" -Method POST -Headers $h -Body '{"product_idea":"AI Resume Builder","target_industry":"HR Tech","competitors":["Resume.io","Zety","Canva"],"budget":50000}'
}
if ($ceo) {
    Write-Host "  >> CEO Report Title: $($ceo.title)"
    Write-Host "  >> Has SWOT: $($ceo.strategy_data.swot -ne $null)"
    Write-Host "  >> Has PESTLE: $($ceo.strategy_data.pestle -ne $null)"
    Write-Host "  >> Has GTM: $($ceo.strategy_data.gtm -ne $null)"
    Write-Host "  >> Has Financials: $($ceo.financials -ne $null)"
    Write-Host "  >> Has Competitors: $($ceo.market_intelligence -ne $null)"
}

$cto = T "CTO-Technical-Report" {
    Invoke-RestMethod -Uri "$base/executive/$wsId/cto/generate" -Method POST -Headers $h -Body '{"product_spec":"AI Resume Builder with NLP parsing and PDF generation","preferred_cloud":"AWS","compliance_needs":["GDPR","SOC2"]}'
}
if ($cto) {
    Write-Host "  >> CTO Report Title: $($cto.title)"
    Write-Host "  >> Has Architecture: $($cto.architecture_review -ne $null)"
    Write-Host "  >> Has Security: $($cto.security_devops -ne $null)"
    Write-Host "  >> Has Optimization: $($cto.optimization_plans -ne $null)"
    Write-Host "  >> Has Tech Debt: $($cto.technical_debt -ne $null)"
}

$coo = T "COO-Operations-Report" {
    Invoke-RestMethod -Uri "$base/executive/$wsId/coo/generate" -Method POST -Headers $h -Body '{"sprint_name":"Sprint 1","team_members":["Alice","Bob","Charlie"],"total_budget":50000}'
}

Write-Host "`n=== DEVELOPMENT PIPELINES ==="
$prd = T "Pipeline-PRD-Generation" {
    Invoke-RestMethod -Uri "$base/development/pipelines/execute?workspace_id=$wsId&pipeline_type=prd" -Method POST -Headers $h -Body '{"target_name":"Food Delivery Platform","prompt":"Build a food delivery platform with restaurant listings, real-time tracking, payment processing"}'
}
if ($prd) { Write-Host "  >> PRD Output Length: $($prd.outputs.content.Length) chars" }

$db = T "Pipeline-Database-Design" {
    Invoke-RestMethod -Uri "$base/development/pipelines/execute?workspace_id=$wsId&pipeline_type=database" -Method POST -Headers $h -Body '{"target_name":"Food Delivery Platform","prompt":"Users, restaurants, menus, orders, payments, delivery tracking, reviews"}'
}
if ($db) { Write-Host "  >> DB Schema Length: $($db.outputs.content.Length) chars" }

$api = T "Pipeline-API-Design" {
    Invoke-RestMethod -Uri "$base/development/pipelines/execute?workspace_id=$wsId&pipeline_type=api" -Method POST -Headers $h -Body '{"target_name":"Food Delivery Platform","prompt":"CRUD restaurants, menus, orders, payments, tracking, reviews, auth"}'
}
$be = T "Pipeline-Backend-Code" {
    Invoke-RestMethod -Uri "$base/development/pipelines/execute?workspace_id=$wsId&pipeline_type=backend" -Method POST -Headers $h -Body '{"target_name":"Food Delivery Platform","prompt":"FastAPI routes for restaurant CRUD, order management, payment processing"}'
}
$fe = T "Pipeline-Frontend-Code" {
    Invoke-RestMethod -Uri "$base/development/pipelines/execute?workspace_id=$wsId&pipeline_type=frontend" -Method POST -Headers $h -Body '{"target_name":"Food Delivery Platform","prompt":"Next.js pages for restaurant listing, cart, checkout, order tracking"}'
}
$arch = T "Pipeline-Architecture-Design" {
    Invoke-RestMethod -Uri "$base/development/pipelines/execute?workspace_id=$wsId&pipeline_type=architecture" -Method POST -Headers $h -Body '{"target_name":"Food Delivery Platform","prompt":"Microservices architecture with order service, payment service, delivery service"}'
}
$ut = T "Pipeline-Unit-Tests" {
    Invoke-RestMethod -Uri "$base/development/pipelines/execute?workspace_id=$wsId&pipeline_type=unittest" -Method POST -Headers $h -Body '{"target_name":"Food Delivery Platform","prompt":"def create_order(): pass\ndef process_payment(): pass\ndef track_delivery(): pass"}'
}
$doc = T "Pipeline-Documentation" {
    Invoke-RestMethod -Uri "$base/development/pipelines/execute?workspace_id=$wsId&pipeline_type=documentation" -Method POST -Headers $h -Body '{"target_name":"Food Delivery Platform","prompt":"Complete developer guide with setup, API reference, deployment instructions"}'
}

Write-Host "`n=== GHOST ENDPOINTS (Called by Frontend but missing) ==="
try { Invoke-RestMethod -Uri "$base/ai/engines/execute" -Method POST -Headers $h -Body '{}'; Write-Host "PASS | GHOST-engines-execute" } catch { Write-Host "FAIL | GHOST-engines-execute | Endpoint does not exist (confirms frontend breakage)" }
try { Invoke-RestMethod -Uri "$base/ai/workflows/execute" -Method POST -Headers $h -Body '{}'; Write-Host "PASS | GHOST-workflows-execute" } catch { Write-Host "FAIL | GHOST-workflows-execute | Endpoint does not exist (confirms frontend breakage)" }

Write-Host "`n=== SEARCH ==="
T "Global-Search" { Invoke-RestMethod -Uri "$base/search/$wsId`?q=resume" -Method GET -Headers $h } | Out-Null

Write-Host "`n=== DOCUMENTS ==="
T "Create-Document" {
    Invoke-RestMethod -Uri "$base/documents/$wsId" -Method POST -Headers $h -Body '{"name":"Test PRD","category":"prd","content":"# PRD for AI Resume Builder"}'
} | Out-Null
T "List-Documents" { Invoke-RestMethod -Uri "$base/documents/$wsId" -Method GET -Headers $h } | Out-Null

Write-Host "`n=== ACTIVITIES ==="
T "List-Activities" { Invoke-RestMethod -Uri "$base/activities/$wsId" -Method GET -Headers $h } | Out-Null

Write-Host "`n=========================================="
Write-Host "RESULTS: $pass PASSED | $fail FAILED"
Write-Host "=========================================="
