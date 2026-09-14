# Production release checklist

Category: Engineering

Fictional Northstar demonstration content. Not a real company policy.

## Before a release

A production release requires a reviewed pull request, passing automated tests, a successful staging smoke test, and a documented rollback plan. The release owner records the version and change summary in the release log. Production deployments require a separate Production Deployer role.

## Release window

Routine production releases take place Tuesday through Thursday between 10:00 and 16:00 UTC. Avoid routine releases during an active incident. Emergency fixes require approval from the incident commander and still need a rollback plan.

## After a release

After deploying, watch the error rate and request latency for 20 minutes. Run the health endpoint and the checkout smoke test. If the new version causes sustained errors, follow the rollback runbook and notify the incident channel.
