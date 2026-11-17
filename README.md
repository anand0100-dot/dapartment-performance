# Department Performance Dashboard

Flask dashboard and JSON API, with PostgreSQL, packaged using Docker and deployed to a test environment by Jenkins.

## Components and dependencies

- app: Flask dashboard and /api/departments endpoint, served on container port 8080.
- db: PostgreSQL 16 with persistent Compose volume. The app waits for the DB health check.
- Jenkins: checks out GitHub source, builds and tests the image, creates build and test tags, deploys the tagged image, then verifies the live endpoints.
- Git/GitHub: source control and Jenkins Pipeline from SCM.

## Run locally

Requires Docker Engine and Docker Compose.

    docker compose up --build -d

The included local .env sets host port 18081 because 8080 is already in use on this laptop. Open http://localhost:18081. Health: /health. Metrics API: /api/departments.

Stop the local stack with docker compose down. Remove its database volume too with docker compose down -v.

## Automated checks

The unittest suite covers health status, database failure behavior, API data, and dashboard rendering. Run it inside the built image:

    docker build -t department-performance-dashboard:local .
    docker run --rm department-performance-dashboard:local python -m unittest discover -s tests -v

## CI/CD pipeline

Jenkinsfile defines these stages:

1. Checkout from the configured GitHub repository using checkout scm.
2. Build Docker image tagged department-performance-dashboard:<BUILD_NUMBER>.
3. Run the automated unittest suite in a disposable container.
4. Add the department-performance-dashboard:test tag and inspect both tags.
5. Deploy that exact build tag with PostgreSQL to a separate Compose test project.
6. Poll /health and request /api/departments; fail the build if either check fails.
7. Always remove the temporary test containers and volume. The built tagged images remain on the Jenkins agent as the pipeline artefact.

## Connect Jenkins to GitHub

1. Create an empty GitHub repository and push this project to it. The project already has a local Git repository on branch main.
2. In Jenkins, create a Pipeline job. Select Pipeline script from SCM, choose Git, enter the repository clone URL and credentials if it is private, and set the script path to Jenkinsfile.
3. Ensure the Jenkins agent has Git, Docker CLI plus Compose, Docker daemon access, and curl.
4. Run Build Now. A GitHub webhook can trigger the same job on pushes if the GitHub and webhook plugins are configured.

The pipeline tags images locally on the Jenkins agent. Publishing to Docker Hub is a separate optional step and requires a Docker Hub repository plus credentials stored in Jenkins Credentials.
