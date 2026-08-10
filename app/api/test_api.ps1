# NimbusCart Phase 2 — API Test Suite (PowerShell)
# Runs all 12 required test cases against http://127.0.0.1:5000
# Usage: powershell -ExecutionPolicy Bypass -File test_api.ps1

$BASE = "http://127.0.0.1:5000"
$pass = 0
$fail = 0

function Assert-Status($label, $got, $expected) {
    if ($got -eq $expected) {
        Write-Host "  [PASS] $label" -ForegroundColor Green
        $script:pass++
    } else {
        Write-Host "  [FAIL] $label  (expected $expected, got $got)" -ForegroundColor Red
        $script:fail++
    }
}

function Assert-Contains($label, $json, $key) {
    if ($json.PSObject.Properties.Name -contains $key) {
        Write-Host "  [PASS] $label" -ForegroundColor Green
        $script:pass++
    } else {
        Write-Host "  [FAIL] $label  (key '$key' not found)" -ForegroundColor Red
        $script:fail++
    }
}

function Assert-Equal($label, $got, $expected) {
    if ($got -eq $expected) {
        Write-Host "  [PASS] $label" -ForegroundColor Green
        $script:pass++
    } else {
        Write-Host "  [FAIL] $label  (expected '$expected', got '$got')" -ForegroundColor Red
        $script:fail++
    }
}

function Invoke-API($method, $path, $body = $null) {
    $uri = "$BASE$path"
    $headers = @{ "Content-Type" = "application/json" }
    try {
        if ($body) {
            $resp = Invoke-WebRequest -Method $method -Uri $uri -Headers $headers `
                -Body ($body | ConvertTo-Json) -ErrorAction Stop
        } else {
            $resp = Invoke-WebRequest -Method $method -Uri $uri -ErrorAction Stop
        }
        return @{ Status = [int]$resp.StatusCode; Body = $resp.Content | ConvertFrom-Json }
    } catch {
        $code = [int]$_.Exception.Response.StatusCode
        $raw  = $_.ErrorDetails.Message
        try   { $parsed = $raw | ConvertFrom-Json }
        catch { $parsed = @{ error = $raw } }
        return @{ Status = $code; Body = $parsed }
    }
}

# ===========================================================================
Write-Host ""
Write-Host "=== NimbusCart Phase 2 API Tests ===" -ForegroundColor Cyan
Write-Host ""

# ---------------------------------------------------------------------------
# TEST 1: GET /health
# ---------------------------------------------------------------------------
Write-Host "TEST 1: GET /health"
$r = Invoke-API "GET" "/health"
Assert-Status   "HTTP 200"           $r.Status 200
Assert-Equal    "status == ok"       $r.Body.status "ok"
Write-Host ""

# ---------------------------------------------------------------------------
# TEST 2: GET /api/items on startup → empty list
# ---------------------------------------------------------------------------
Write-Host "TEST 2: GET /api/items (startup → should be empty)"
$r = Invoke-API "GET" "/api/items"
Assert-Status   "HTTP 200"           $r.Status 200
Assert-Equal    "body is empty array" ($r.Body.Count) 0
Write-Host ""

# ---------------------------------------------------------------------------
# TEST 3: POST valid product → Laptop
# ---------------------------------------------------------------------------
Write-Host "TEST 3: POST /api/items — valid product (Laptop)"
$r = Invoke-API "POST" "/api/items" @{ name="Laptop"; price=60000; stock=10 }
Assert-Status   "HTTP 201"           $r.Status 201
Assert-Contains "has id"             $r.Body "id"
Assert-Equal    "name == Laptop"     $r.Body.name "Laptop"
Assert-Equal    "price == 60000"     $r.Body.price 60000
Assert-Equal    "stock == 10"        $r.Body.stock 10
$laptopId = $r.Body.id
Write-Host "  (created id=$laptopId)"
Write-Host ""

# ---------------------------------------------------------------------------
# TEST 4: GET /api/items after POST → Laptop present
# ---------------------------------------------------------------------------
Write-Host "TEST 4: GET /api/items after POST — Laptop present"
$r = Invoke-API "GET" "/api/items"
Assert-Status   "HTTP 200"           $r.Status 200
Assert-Equal    "one product exists" ($r.Body.Count) 1
Assert-Equal    "first product name" $r.Body[0].name "Laptop"
Write-Host ""

# ---------------------------------------------------------------------------
# TEST 5: POST second product → Mouse
# ---------------------------------------------------------------------------
Write-Host "TEST 5: POST /api/items — second product (Mouse)"
$r = Invoke-API "POST" "/api/items" @{ name="Wireless Mouse"; price=25.99; stock=0 }
Assert-Status   "HTTP 201"           $r.Status 201
Assert-Equal    "name == Wireless Mouse" $r.Body.name "Wireless Mouse"
$mouseId = $r.Body.id
Write-Host "  (created id=$mouseId)"

$r2 = Invoke-API "GET" "/api/items"
Assert-Equal    "two products in list" ($r2.Body.Count) 2
Write-Host ""

# ---------------------------------------------------------------------------
# TEST 6: Empty name → 400
# ---------------------------------------------------------------------------
Write-Host "TEST 6: POST — empty name"
$r = Invoke-API "POST" "/api/items" @{ name=""; price=99; stock=5 }
Assert-Status   "HTTP 400"           $r.Status 400
Assert-Contains "error key present"  $r.Body "error"
Write-Host ""

# ---------------------------------------------------------------------------
# TEST 7: Missing name field → 400
# ---------------------------------------------------------------------------
Write-Host "TEST 7: POST — missing name field"
$r = Invoke-API "POST" "/api/items" @{ price=99; stock=5 }
Assert-Status   "HTTP 400"           $r.Status 400
Assert-Contains "error key present"  $r.Body "error"
Write-Host ""

# ---------------------------------------------------------------------------
# TEST 8: Zero/negative price → 400
# ---------------------------------------------------------------------------
Write-Host "TEST 8a: POST — zero price"
$r = Invoke-API "POST" "/api/items" @{ name="Widget"; price=0; stock=1 }
Assert-Status   "HTTP 400"           $r.Status 400

Write-Host "TEST 8b: POST — negative price"
$r = Invoke-API "POST" "/api/items" @{ name="Widget"; price=-5; stock=1 }
Assert-Status   "HTTP 400"           $r.Status 400
Write-Host ""

# ---------------------------------------------------------------------------
# TEST 9: Negative stock → 400
# ---------------------------------------------------------------------------
Write-Host "TEST 9: POST — negative stock"
$r = Invoke-API "POST" "/api/items" @{ name="Widget"; price=10; stock=-1 }
Assert-Status   "HTTP 400"           $r.Status 400
Assert-Contains "error key present"  $r.Body "error"
Write-Host ""

# ---------------------------------------------------------------------------
# TEST 10: Decimal stock (5.5) → 400
# ---------------------------------------------------------------------------
Write-Host "TEST 10: POST — decimal stock (5.5)"
$r = Invoke-API "POST" "/api/items" @{ name="Widget"; price=10; stock=5.5 }
Assert-Status   "HTTP 400"           $r.Status 400
Assert-Contains "error key present"  $r.Body "error"
Write-Host ""

# ---------------------------------------------------------------------------
# TEST 11: Malformed/missing JSON → 400
# ---------------------------------------------------------------------------
Write-Host "TEST 11: POST — malformed JSON (raw string body)"
try {
    $resp = Invoke-WebRequest -Method POST -Uri "$BASE/api/items" `
        -Headers @{ "Content-Type" = "application/json" } `
        -Body "not json at all" -ErrorAction Stop
    Assert-Status "HTTP 400" ([int]$resp.StatusCode) 400
} catch {
    $code = [int]$_.Exception.Response.StatusCode
    Assert-Status "HTTP 400" $code 400
}
Write-Host ""

# ---------------------------------------------------------------------------
# TEST 12: Verify list count not contaminated by failed POSTs
# ---------------------------------------------------------------------------
Write-Host "TEST 12: GET /api/items — only 2 valid products stored (failed POSTs not inserted)"
$r = Invoke-API "GET" "/api/items"
Assert-Status   "HTTP 200"           $r.Status 200
Assert-Equal    "still 2 products"   ($r.Body.Count) 2
Write-Host ""

# ===========================================================================
Write-Host ""
Write-Host "=== Results ===" -ForegroundColor Cyan
Write-Host "  Passed: $pass" -ForegroundColor Green
if ($fail -eq 0) {
    Write-Host "  Failed: $fail" -ForegroundColor Green
} else {
    Write-Host "  Failed: $fail" -ForegroundColor Red
}
Write-Host ""
