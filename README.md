# UNG-GOVBRIDGE

Open, vendor-neutral government interoperability bridge for controlled transition between cloud-native UNG services and authorized legacy/mainframe environments.

## System boundary

**Modern side:** NEXUS orchestration, PULSAR events, JANUS workload/user identity, VAULT protected records.

**GOVBRIDGE:** protocol adapters, schema translation, policy enforcement, transaction correlation, retry/dead-letter handling, health/observability and resilient gateway abstractions.

**Legacy side:** explicitly configured, allow-listed enterprise endpoints. No legacy endpoint is enabled by default.

## Open architecture

- Envoy/Istio-compatible service-mesh boundary; SPIFFE/SPIRE-compatible workload identity.
- Portable JSON Schema / Apache Avro contracts.
- StrongSwan/IPsec or WireGuard transport profiles on standard Linux hosts.
- FRRouting/BGP-compatible WAN resiliency.
- Adapter interfaces for authorized TN3270E / Enterprise Extender transition workloads.
- gRPC/Protobuf synchronous path and Kafka/Redpanda-compatible asynchronous path.
- S3-compatible object-storage interface for archives/dead-letter artifacts.

## Security defaults

Deny by default. Legacy clear-text TN3270/TCP 23 is disabled unless an isolated compatibility profile explicitly enables it. Secrets are supplied by deployment secret stores, never committed. FIPS claims require a validated cryptographic module and approved deployment configuration; enabling a software flag alone is not treated as compliance.

## Capacity

75,000 concurrent sessions is an engineering target, **not a demonstrated capacity**. It must be established by staged load and failure testing.

## API

- `GET /health`
- `GET /ready`
- `GET /v1/system`
- `GET /v1/topology`
- `GET /v1/capacity`

