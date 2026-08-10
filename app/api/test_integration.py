"""Integration verification: Flask serves HTML + API round-trip."""
import urllib.request, json, sys

BASE = "http://127.0.0.1:5000"

def api(method, path, body=None):
    url = BASE + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url, data=data, method=method,
        headers={"Content-Type": "application/json"} if data else {}
    )
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())

errors = 0

print("=== Integration: Flask serves frontend HTML ===")
req = urllib.request.Request(BASE + "/")
with urllib.request.urlopen(req) as r:
    html = r.read().decode()
if "NimbusCart" in html and "/api/items" in html:
    print("[PASS] GET / returns index.html with NimbusCart heading + /api/items references")
else:
    print("[FAIL] index.html missing expected content")
    errors += 1

print()
print("=== Integration: Frontend -> Flask API round trip ===")

s, b = api("GET", "/api/items")
print(f"[INFO] Items before test: {len(b)} (from earlier test run — expected)")

s, b = api("POST", "/api/items", {"name": "Keyboard", "price": 79.99, "stock": 50})
if s == 201 and b.get("name") == "Keyboard":
    print(f"[PASS] POST Keyboard -> id={b['id']}, price={b['price']}, stock={b['stock']}")
else:
    print(f"[FAIL] POST Keyboard returned {s}: {b}")
    errors += 1

s, b = api("POST", "/api/items", {"name": "Monitor", "price": 299.00, "stock": 3})
if s == 201 and b.get("name") == "Monitor":
    print(f"[PASS] POST Monitor -> id={b['id']}")
else:
    print(f"[FAIL] POST Monitor returned {s}: {b}")
    errors += 1

s, items = api("GET", "/api/items")
names = [p["name"] for p in items]
if "Keyboard" in names and "Monitor" in names:
    print(f"[PASS] GET /api/items lists {len(items)} products: {names}")
else:
    print(f"[FAIL] expected Keyboard+Monitor in {names}")
    errors += 1

print()
if errors == 0:
    print("All integration checks passed.")
else:
    print(f"{errors} integration check(s) failed.")
sys.exit(errors)
