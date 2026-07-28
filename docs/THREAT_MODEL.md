# Threat Model

## Protected assets
- API keys and credentials.
- Team-owned data and scouting notes.
- Recommendation history.
- Proprietary features and model artifacts.
- User identity and feedback.

## Principal risks
- Secret leakage through Git history or logs.
- Unauthorized redistribution of sports data.
- Prompt injection from knowledge documents.
- Model output presented without evidence.
- Cross-tenant data exposure in a future hosted product.
- Use of pre-game features during restricted in-game contexts.

## MVP controls
- `.env` excluded from Git.
- Synthetic default data.
- Local SQLite logging.
- Evidence and abstention policies.
- No authentication claims.
- No team-owned data.

## Enterprise controls on roadmap
- SSO/RBAC, tenant isolation, encryption, VPC deployment, audit retention, document allowlists, secrets manager and capability timing controls.
