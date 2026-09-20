from fastapi.testclient import TestClient
import app

c=TestClient(app.app)

def test_health():
 assert c.get("/health").status_code==200
 assert c.get("/health").json()["service"]=="UNG-GOVBRIDGE"

def test_ready_reports_all_dependencies_truthfully():
 x=c.get("/ready")
 assert x.status_code==200
 d=x.json()["dependencies"]
 assert set(d)=={"janus","nexus","pulsar","vault"}
 assert all(v in {"reachable","unreachable","unhealthy","not_configured"} for v in d.values())

def test_capacity_not_overclaimed():
 x=c.get("/v1/capacity").json()
 assert x["target_concurrent_sessions"]==75000
 assert x["validated_concurrent_sessions"] is None
 assert x["status"]=="not_benchmarked"

def test_legacy_adapters_disabled():
 rows={x["id"]:x for x in c.get("/v1/adapters").json()}
 assert rows["tn3270e"]["state"]=="disabled"
 assert rows["enterprise-extender"]["state"]=="disabled"

def test_modern_adapters_available():
 rows={x["id"]:x for x in c.get("/v1/adapters").json()}
 assert rows["grpc"]["state"]=="available"
 assert rows["event-stream"]["state"]=="available"

def test_protected_audit_rejects_anonymous():
 assert c.get("/v1/audit").status_code==401

def test_job_rejects_anonymous():
 assert c.post("/v1/jobs",json={"adapter":"grpc","payload":{"probe":True}}).status_code==401

def test_unknown_adapter_requires_auth_first():
 assert c.post("/v1/jobs",json={"adapter":"missing","payload":{}}).status_code==401
