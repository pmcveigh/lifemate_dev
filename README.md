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
## Required environment

The backend migrations seed three initial user accounts. To keep their credentials
out of source control, provide the following environment variables before running
`alembic upgrade` or starting the backend application:

| Variable | Description |
| --- | --- |
| `GLOBAL_ADMIN_PASSWORD` | Password for the `globaladmin` user that owns the global administrator role. |
| `HOME_ADMIN_PASSWORD` | Password for the `phil` user that owns the home administrator role. |
| `HOME_USER_PASSWORD` | Password for the `courtney` user that owns the home user role. |

You can define them in `.env.dev` / `.env.prod` or export them in the shell that
invokes the deployment scripts. The migration environment and the migrations
themselves will now fail fast if any of these variables are missing.

> **Password rotation**
>
> Existing deployments must set new values for the variables above and run the
> `3f2d8e7c5a90_rotate_seeded_user_passwords` Alembic migration to rotate the
> seeded credentials.
