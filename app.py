import os
from fastapi import FastAPI\nfrom fastapi.responses import HTMLResponse

SYSTEM="UNG-GOVBRIDGE"
VERSION="0.1.0"
app=FastAPI(title=SYSTEM,version=VERSION,description="Open government legacy interoperability bridge")

def configured(name): return bool(os.getenv(name,"").strip())

@app.get("/health")
def health(): return {"status":"ok","service":SYSTEM,"version":VERSION}

@app.get("/ready")
def ready():
    deps={"janus":configured("JANUS_BASE_URL"),"nexus":configured("NEXUS_BASE_URL"),"pulsar":configured("PULSAR_BASE_URL"),"vault":configured("VAULT_BASE_URL")}
    return {"status":"ready" if all(deps.values()) else "degraded","service":SYSTEM,"dependencies":deps}

@app.get("/v1/system")
def system():
    return {"system":SYSTEM,"version":VERSION,"domain":"legacy-interoperability","architecture":"open-vendor-neutral","capacity_target":{"concurrent_sessions":75000,"validated":False}}

@app.get("/v1/topology")
def topology():
    return {"layers":[
      {"layer":1,"name":"cloud-neutral gateway","standards":["Envoy","Istio","SPIFFE","SPIRE","mTLS"]},
      {"layer":2,"name":"protocol translation","standards":["JSON Schema","Apache Avro","TN3270E adapter","Enterprise Extender adapter"]},
      {"layer":3,"name":"hardware-agnostic WAN encryption","standards":["IPsec","StrongSwan","WireGuard"],"fips_claim":"validation required"},
      {"layer":4,"name":"open routing and resiliency","standards":["FRRouting","BGP"]}
    ],"synchronous":["gRPC","Protobuf"],"asynchronous":["Kafka-compatible API","Redpanda-compatible API"],"storage":"S3-compatible"}

@app.get("/v1/capacity")
def capacity():
    return {"target_concurrent_sessions":75000,"validated_concurrent_sessions":None,"status":"not_benchmarked"}


@app.get("/",response_class=HTMLResponse,include_in_schema=False)
def console():
    return """<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>UNG-GOVBRIDGE</title><style>body{margin:0;background:#07111f;color:#eaf2ff;font:15px system-ui}.wrap{max-width:1100px;margin:auto;padding:32px}.hero{padding:28px;border:1px solid #29415f;border-radius:18px;background:#0c192b}h1{font-size:34px;margin:0 0 6px}.tag{color:#9bb2cf}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px;margin-top:18px}.card{background:#101f34;border:1px solid #29415f;border-radius:14px;padding:18px}.ok{color:#61e6a8}.warn{color:#ffd166}.flow{margin-top:18px;padding:18px;border:1px solid #29415f;border-radius:14px;line-height:2}b{color:#fff}</style></head><body><main class="wrap"><section class="hero"><h1>UNG-GOVBRIDGE</h1><div class="tag">National Open Interoperability Bridge · Vendor-Neutral Transition Layer</div><div class="grid"><div class="card"><b>Service</b><p class="ok">● ONLINE</p></div><div class="card"><b>Architecture</b><p>Open / Cloud Neutral</p></div><div class="card"><b>Capacity Target</b><p>75,000 concurrent sessions</p><small class="warn">Benchmark pending</small></div><div class="card"><b>Security</b><p>Deny by default</p></div></div><div class="flow"><b>Modern UNG Systems</b> → NEXUS → <b>GOVBRIDGE</b> → Authorized Legacy/Mainframe Enclaves<br><b>Legacy Events</b> → GOVBRIDGE → PULSAR → NEXUS / UNG Systems</div><div class="grid"><div class="card"><b>Layer 1</b><p>Envoy · Istio · SPIFFE/SPIRE · mTLS</p></div><div class="card"><b>Layer 2</b><p>Protocol & Schema Translation</p></div><div class="card"><b>Layer 3</b><p>IPsec · StrongSwan · WireGuard</p></div><div class="card"><b>Layer 4</b><p>FRRouting · BGP Resiliency</p></div></div></section></main></body></html>"""
