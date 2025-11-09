# Lifemate

## Configuration

The backend expects a strong JWT signing secret to be provided through the
`JWT_SECRET_KEY` environment variable. The application will refuse to start if
this variable is missing or shorter than 32 characters.

Environment variables are loaded from `.env.dev` during development and
`.env.prod` when `ENVIRONMENT=production`. Copy the example files and replace the
secret with a freshly generated value:

```bash
cp backend/.env.dev.example backend/.env.dev
cp backend/.env.prod.example backend/.env.prod
python - <<'PY'
import secrets
print(secrets.token_urlsafe(64))
PY
```

Paste the generated value into both copied files under `JWT_SECRET_KEY`.

## Generating Secrets for Deployment

When preparing container deployments, ensure that the `JWT_SECRET_KEY` provided
via environment variables or orchestration templates uses a similarly strong
value. You can generate a secret inline when running Docker Compose:

```bash
export JWT_SECRET_KEY="$(python - <<'PY'
import secrets
print(secrets.token_urlsafe(64))
PY
)"
docker compose up --build
```

Never commit the generated secrets to version control.
