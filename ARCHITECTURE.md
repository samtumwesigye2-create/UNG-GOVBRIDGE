# GOVBRIDGE production architecture

GOVBRIDGE is the controlled transition boundary between NEXUS/PULSAR and explicitly authorized legacy enterprise environments.

## Runtime rules

- JANUS is the identity authority. Protected GOVBRIDGE endpoints accept JANUS bearer sessions and introspect them server-side.
- NEXUS and PULSAR are external dependencies, never simulated as live. The console reports configured/reachable/unreachable/not-configured state.
- TN3270E and Enterprise Extender adapters ship disabled. TCP/23 is not a production default.
- gRPC/Protobuf and Kafka/Redpanda are adapter contracts; a configured upstream is required before traffic is represented as delivered.
- Translation envelopes are versioned and portable. The v1 JSON Schema lives in `schemas/transaction-v1.json`.
- 75,000 concurrent sessions is a target. It remains unvalidated until a real load generator completes the staged acceptance plan.
- FIPS compliance is never inferred from an OpenSSL flag. It requires a validated module, approved configuration, and applicable operational controls.

## Acceptance gates

Health must pass, anonymous protected requests must be rejected, legacy adapters must remain disabled without explicit configuration, dependency state must be truthful, and capacity must remain marked unbenchmarked until measured.
