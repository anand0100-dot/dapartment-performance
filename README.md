# Department Performance Dashboard

A repeatable local deployment demo using Git/GitHub, Docker Compose, PostgreSQL, and Jenkins.

## Application components

- app: Flask dashboard and JSON API on port 8080, backed by PostgreSQL.
- db: PostgreSQL 16 with a named volume. Compose waits for the database health check before starting the app.
- Jenkins: Builds the app image, starts an isolated Compose stack, checks /health, and removes the CI stack afterward.
- Git/GitHub: Store the project in a repository; configure Jenkins to load its Jenkinsfile from SCM.

## Run locally

Docker Engine and Docker Compose plugin are required.

    cp .env.example .env
    docker compose up --build -d
    docker compose ps

Open http://localhost:8080. Health endpoint: /health. Metrics API: /api/departments.

Stop services and retain database data:

    docker compose down

Reset the database volume and sample data:

    docker compose down -v

## Environment variables

Copy .env.example to .env before starting Compose.

| Variable | Purpose | Default |
|---|---|---|
| APP_PORT | Host port for dashboard | 8080 |
| POSTGRES_DB | Database name | performance |
| POSTGRES_USER | Database user | dashboard |
| POSTGRES_PASSWORD | Local database password | change-this-local-password |
| DATABASE_URL | App connection string | Compose service db |

Credentials are for local simulation. Use Jenkins Credentials and managed secrets in a shared deployment.

## Jenkins and GitHub

1. Push this folder to a GitHub repository.
2. Create a Jenkins Pipeline job using Pipeline script from SCM, choose Git and the repository URL, and set script path to Jenkinsfile.
3. The Jenkins agent needs Git, Docker CLI with Compose, Docker daemon access, and curl. Restrict Docker socket access to trusted agents because it grants host-level control.
4. Run the job. It builds the app image, starts PostgreSQL and the app on port 18080, checks /health, and cleans up the temporary stack.

The CI stack uses a separate Compose project name and host port so it can run beside the local dashboard.
