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
