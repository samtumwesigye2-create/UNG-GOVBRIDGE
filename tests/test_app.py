from fastapi.testclient import TestClient
import app

c=TestClient(app.app)

def test_health():
 assert c.get("/health").status_code==200
 assert c.get("/health").json()["service"]=="UNG-GOVBRIDGE"

def test_capacity_not_overclaimed():
 x=c.get("/v1/capacity").json()
 assert x["target_concurrent_sessions"]==75000
 assert x["validated_concurrent_sessions"] is None

def test_legacy_adapters_disabled():
 rows={x["id"]:x for x in c.get("/v1/adapters").json()}
 assert rows["tn3270e"]["state"]=="disabled"
 assert rows["enterprise-extender"]["state"]=="disabled"

def test_protected_audit_rejects_anonymous():
 assert c.get("/v1/audit").status_code==401
