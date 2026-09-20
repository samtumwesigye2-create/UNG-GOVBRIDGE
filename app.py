import os, json, sqlite3, time
from urllib.request import Request, urlopen
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

SYSTEM="UNG-GOVBRIDGE"; VERSION="0.2.0"
app=FastAPI(title=SYSTEM,version=VERSION)
DB=os.getenv("STATE_DB","/tmp/govbridge.db")
JANUS=os.getenv("JANUS_BASE_URL","https://ung-iam-production.up.railway.app").rstrip("/")
DEPS={"janus":JANUS,"nexus":os.getenv("NEXUS_BASE_URL","").rstrip("/"),"pulsar":os.getenv("PULSAR_BASE_URL","").rstrip("/"),"vault":os.getenv("VAULT_BASE_URL","").rstrip("/")}

def db():
 c=sqlite3.connect(DB); c.row_factory=sqlite3.Row
 c.execute("create table if not exists audit(id integer primary key autoincrement, at real, actor text, action text, detail text)")
 c.execute("create table if not exists jobs(id integer primary key autoincrement, at real, adapter text, status text, payload text)")
 c.commit(); return c
def audit(actor,action,detail):
 c=db(); c.execute("insert into audit(at,actor,action,detail) values(?,?,?,?)",(time.time(),actor,action,json.dumps(detail))); c.commit(); c.close()
def probe(url):
 if not url:return "not_configured"
 try:
  with urlopen(url+"/health",timeout=2) as r:return "reachable" if r.status<400 else "unhealthy"
 except Exception:return "unreachable"
def principal(auth):
 if not auth.lower().startswith("bearer "): raise HTTPException(401,"JANUS bearer required")
 try:
  q=Request(JANUS+"/v1/auth/introspect",method="POST",headers={"Authorization":auth})
  with urlopen(q,timeout=3) as r:x=json.load(r)
  if not x.get("active"):raise ValueError()
  return x["principal"]
 except HTTPException:raise
 except Exception:raise HTTPException(401,"JANUS session invalid")

class Job(BaseModel):
 adapter:str
 payload:dict

ADAPTERS=[
 {"id":"tn3270e","name":"TN3270E","state":"disabled","secure_default":True,"note":"TCP/23 compatibility remains disabled"},
 {"id":"enterprise-extender","name":"Enterprise Extender","state":"disabled","secure_default":True,"note":"Endpoint and port profile required"},
 {"id":"grpc","name":"gRPC / Protobuf","state":"available","secure_default":True,"note":"mTLS expected"},
 {"id":"event-stream","name":"Kafka / Redpanda API","state":"available","secure_default":True,"note":"Broker configuration required"}]

@app.get("/health")
def health():return {"status":"ok","service":SYSTEM,"version":VERSION}
@app.get("/ready")
def ready():return {"status":"ready","service":SYSTEM,"dependencies":{k:probe(v) for k,v in DEPS.items()}}
@app.get("/v1/system")
def system():return {"system":SYSTEM,"version":VERSION,"capacity_target":{"concurrent_sessions":75000,"validated":False}}
@app.get("/v1/dependencies")
def dependencies():return {k:{"configured":bool(v),"state":probe(v)} for k,v in DEPS.items()}
@app.get("/v1/adapters")
def adapters():return ADAPTERS
@app.get("/v1/audit")
def logs(authorization:str=Header("")):
 principal(authorization); c=db(); rows=[dict(x) for x in c.execute("select * from audit order by id desc limit 100")]; c.close(); return rows
@app.post("/v1/jobs")
def create_job(body:Job,authorization:str=Header("")):
 p=principal(authorization)
 a=next((x for x in ADAPTERS if x["id"]==body.adapter),None)
 if not a:raise HTTPException(404,"adapter_not_found")
 if a["state"]!="available":raise HTTPException(409,"adapter_not_enabled")
 c=db(); cur=c.execute("insert into jobs(at,adapter,status,payload) values(?,?,?,?)",(time.time(),body.adapter,"accepted",json.dumps(body.payload))); c.commit(); jid=cur.lastrowid;c.close()
 audit(p.get("display_name") or p.get("subject") or "JANUS", "job.accepted",{"job_id":jid,"adapter":body.adapter})
 return {"id":jid,"status":"accepted","adapter":body.adapter}
@app.get("/v1/capacity")
def capacity():return {"target_concurrent_sessions":75000,"validated_concurrent_sessions":None,"status":"not_benchmarked","test_plan":[1000,5000,10000,25000,50000,75000]}

@app.get("/",response_class=HTMLResponse,include_in_schema=False)
def ui():
 return """<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>UNG-GOVBRIDGE</title><style>body{margin:0;background:#07111f;color:#edf4ff;font:15px system-ui}.w{max-width:1150px;margin:auto;padding:28px}.hero,.card{background:#0d1a2d;border:1px solid #2b4363;border-radius:17px;padding:22px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;margin-top:14px}h1{font-size:34px;margin:0}.muted{color:#9eb3cf}.ok{color:#6ee7ad}.warn{color:#ffd166}.bad{color:#ff7b86}.flow{margin-top:14px;line-height:2}.row{display:flex;justify-content:space-between;gap:12px;border-top:1px solid #253a56;padding:12px 0}.row:first-child{border:0}</style></head><body><main class="w"><section class="hero"><h1>UNG-GOVBRIDGE</h1><p class="muted">National Open Interoperability Bridge · Operations Console</p><div class="grid"><div class="card"><b>Service</b><p class="ok">● ONLINE</p></div><div class="card"><b>Security</b><p>JANUS bearer enforcement</p></div><div class="card"><b>Capacity Target</b><p>75,000 sessions</p><small class="warn">Not benchmarked</small></div></div><div class="card flow"><b>Modern UNG</b> → NEXUS → <b>GOVBRIDGE</b> → Authorized Legacy Enclave<br><b>Legacy Events</b> → GOVBRIDGE → PULSAR → NEXUS</div><h2>Connected Systems</h2><div id="deps" class="grid"></div><h2>Adapter Registry</h2><div id="adapters" class="card"></div><h2>Data Plane</h2><div class="grid"><div class="card"><b>Synchronous</b><p>gRPC / Protobuf</p></div><div class="card"><b>Asynchronous</b><p>Kafka / Redpanda compatible</p></div><div class="card"><b>Legacy Compatibility</b><p>TN3270E / Enterprise Extender</p><small class="warn">Disabled until explicitly configured</small></div></div></section></main><script>
async function j(u){try{return await (await fetch(u)).json()}catch(e){return {}}}
(async()=>{let d=await j('/v1/dependencies'),x=document.querySelector('#deps');for(let [k,v] of Object.entries(d)){let c=v.state==='reachable'?'ok':v.state==='not_configured'?'warn':'bad';x.innerHTML+=`<div class="card"><b>${k.toUpperCase()}</b><p class="${c}">● ${v.state}</p></div>`}let a=await j('/v1/adapters'),z=document.querySelector('#adapters');a.forEach(v=>z.innerHTML+=`<div class="row"><span><b>${v.name}</b><br><small class="muted">${v.note}</small></span><span class="${v.state==='available'?'ok':'warn'}">${v.state}</span></div>`)})()
</script></body></html>"""
