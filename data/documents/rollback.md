# Rollback runbook

Category: Engineering

Fictional Northstar demonstration content. Not a real company policy.

## Trigger a rollback

Start a rollback if a new release produces a sustained error rate above 2 percent for five minutes or breaks the checkout smoke test. The release owner contacts the incident commander before rolling back. If there is no active incident, the release owner opens one.

## Restore the last version

Select the last known healthy application version in the deployment console, restore that version, and rerun the smoke tests. Record the old and new version identifiers. Database migrations must be reviewed separately because reverting application code does not automatically revert a schema change.

## Verify recovery

Monitor error rate and latency for 20 minutes after rollback. Confirm the health endpoint is healthy and a test checkout succeeds. Attach the timeline to the incident report and schedule a follow-up review.
