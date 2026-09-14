# Secrets and API keys

Category: Security

Fictional Northstar demonstration content. Not a real company policy.

## Store secrets

Store service secrets in the approved secret manager and inject them as environment variables at runtime. Never commit API keys to Git or paste them in documentation, screenshots, or chat. Development and production use different credentials.

## Suspected exposure

If an API key is exposed, report a security incident, revoke the key, and issue a replacement through the approved process. Review relevant access logs. Removing the key from the latest Git commit does not remove it from repository history.

## Rotation

Service owners review credentials every 90 days and rotate them according to the service policy or immediately after suspected compromise. Record the owner and purpose of each credential. Avoid shared personal tokens.
