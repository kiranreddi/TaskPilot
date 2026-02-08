# Configuration Checklist — TaskPilot

## Environments
- [ ] dev / staging / prod deployments
- [ ] separate OAuth apps per environment
- [ ] feature flags for risky actions

## Secrets management
- [ ] store secrets in Secret Manager (AWS/GCP)
- [ ] encrypt OAuth tokens with KMS
- [ ] rotate keys quarterly (or per incident)

## Orchestrator
- [ ] Temporal cluster deployed
- [ ] worker autoscaling based on queue depth
- [ ] DLQ configured for poison messages

## Reliability
- [ ] retries with exponential backoff
- [ ] idempotency keys for write actions
- [ ] rate limit handling per provider

## Security
- [ ] PII & secret redaction in logs
- [ ] tenant isolation tests
- [ ] approval required for WRITE by default

## Observability
- [ ] OpenTelemetry tracing
- [ ] error alerting (failure spike, OAuth failures)
- [ ] dashboards for run latency and success rate

## Billing
- [ ] Stripe products/plans configured
- [ ] webhook verification and replay protection
- [ ] quotas enforced server-side
