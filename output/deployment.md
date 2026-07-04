```markdown
# Deployment Guide: Food Delivery App

This document provides comprehensive guidance for deploying the Food Delivery App, covering Dockerization, environment management, reverse proxy configuration, database operations, observability, CI/CD, and a production readiness checklist.

## 1. Dockerfile Recommendations

Containerization with Docker ensures consistent environments across development, testing, and production. We will use multi-stage builds for both backend and frontend to optimize image size and build times.

### 1.1. Backend Dockerfile (`food-delivery-backend/Dockerfile`)

The FastAPI backend will be built using a multi-stage Dockerfile.

``````

### 1.2. Frontend Dockerfile (`food-delivery-frontend/Dockerfile`)

The React frontend will also use a multi-stage Dockerfile to build the static assets and then serve them with Nginx.

``````

## 2. `docker-compose.yml` Explanation

`docker-compose.yml` defines and runs multi-container Docker applications. It's ideal for local development and can be adapted for small-scale production deployments.

``````

**Explanation:**

*   **`db` service:**
    *   Uses `postgres:16-alpine` image.
    *   Environment variables for database name, user, and password are set from `.env`.
    *   A named volume `pgdata` persists database data.
    *   `healthcheck` ensures the database is ready before dependent services start.
*   **`backend` service:**
    *   Builds from the `food-delivery-backend/Dockerfile`.
    *   `DATABASE_URL` and `ASYNC_DATABASE_URL` are constructed using environment variables, pointing to the `db` service.
    *   `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES` are crucial for JWT.
    *   `depends_on` ensures `db` is healthy before `backend` starts.
    *   `volumes` mounts the local backend code for development, enabling live-reloading.
    *   The `command` is set for development with `--reload`. For production, this should be removed or replaced with a more robust command (e.g., `gunicorn`).
*   **`frontend` service:**
    *   Builds from the `food-delivery-frontend/Dockerfile`.
    *   `VITE_API_BASE_URL` is passed as a build argument to configure the React app's API endpoint.
    *   Exposes port 80 (Nginx default) and maps it to 3000 locally.
    *   `depends_on` ensures `backend` is available.
*   **`nginx` service (Reverse Proxy):**
    *   Uses `nginx:stable-alpine` image.
    *   Maps ports 80 and 443 for HTTP/HTTPS traffic.
    *   Mounts custom Nginx configuration files and volumes for Certbot (for SSL).
    *   `depends_on` ensures both `frontend` and `backend` are running.
    *   `healthcheck` verifies Nginx configuration.
*   **`volumes`:** Defines `pgdata` for persistent PostgreSQL data.

## 3. Nginx Reverse Proxy Configuration

Nginx will serve as the entry point for all incoming traffic, acting as a reverse proxy to route requests to the appropriate backend or serve static frontend assets. It will also handle SSL termination.

### 3.1. Main Nginx Configuration (`nginx/nginx.conf`)

This is the global Nginx configuration.

``````

### 3.2. Server Block Configuration (`nginx/conf.d/default.conf`)

This file defines how Nginx handles requests for your domain.

``````

**Key Points:**

*   **`server_name`**: Replace `your_domain.com` with your actual domain.
*   **HTTP to HTTPS Redirect**: All HTTP traffic is redirected to HTTPS for security.
*   **Certbot Challenge**: Configuration for Let's Encrypt (Certbot) to handle SSL certificate issuance and renewal.
*   **SSL Configuration**: Specifies SSL certificate paths, protocols, and ciphers for secure communication.
*   **Frontend Serving**: The root `/` location serves the static React application files. `try_files` is crucial for React Router to handle client-side routing.
*   **Backend Proxy**: The `/api/v1/` location proxies requests to the `backend` service (FastAPI) running on port 8000.
*   **Proxy Headers**: Essential headers are set to pass client information to the backend.

## 4. Deployment Steps

These steps outline a basic deployment using Docker Compose on a single server. For larger scale, consider Kubernetes or cloud-native container services.

### 4.1. Prerequisites

1.  **Server:** A Linux server (e.g., Ubuntu, CentOS) with Docker and Docker Compose installed.
2.  **Domain Name:** A registered domain name pointing to your server's IP address.
3.  **Git:** Installed on the server.

### 4.2. Initial Server Setup

1.  **SSH into your server:**
    ```Here's the complete `deployment.md` document for your Food Delivery App:

dockerfile
# Stage 1: Build - Install dependencies
FROM python:3.11-slim-buster AS builder

WORKDIR /app

# Install system dependencies for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production - Copy application code and run
FROM python:3.11-slim-buster AS production

WORKDIR /app

# Install system dependencies needed at runtime (e.g., libpq for psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn
COPY --from=builder /usr/local/bin/alembic /usr/local/bin/alembic

# Copy application code
COPY food-delivery-backend/app ./app
COPY food-delivery-backend/alembic ./alembic
COPY food-delivery-backend/alembic.ini .
COPY food-delivery-backend/requirements.txt . # For reference, not strictly needed for runtime

# Expose the port FastAPI will run on
EXPOSE 8000

# Set environment variables for production
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /app

# Command to run the application using Uvicorn
# Use gunicorn with uvicorn workers in production for robustness
# For simplicity in docker-compose, we might start with uvicorn directly.
# In a real production setup, consider a process manager like Gunicorn.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
dockerfile
# Stage 1: Build the React application
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package.json and package-lock.json to leverage Docker cache
COPY food-delivery-frontend/package*.json ./
RUN npm install

# Copy the rest of the frontend code
COPY food-delivery-frontend/ .

# Build the React app for production
# Ensure VITE_API_BASE_URL is correctly set during build or runtime
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:stable-alpine AS production

# Copy custom Nginx configuration
COPY food-delivery-frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Copy the built React app from the builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port 80 for Nginx
EXPOSE 80

# Command to run Nginx (default command is sufficient)
CMD ["nginx", "-g", "daemon off;"]
yaml
version: '3.8'

services:
  db:
    image: postgres:16-alpine
    container_name: food_delivery_db
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432" # Expose for local development/debugging
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: .
      dockerfile: food-delivery-backend/Dockerfile
    container_name: food_delivery_backend
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
      ASYNC_DATABASE_URL: postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
      SECRET_KEY: ${SECRET_KEY}
      ALGORITHM: ${ALGORITHM}
      ACCESS_TOKEN_EXPIRE_MINUTES: ${ACCESS_TOKEN_EXPIRE_MINUTES}
      # Add other backend-specific environment variables here (e.g., Stripe API keys, Google Maps API keys)
    ports:
      - "8000:8000" # Expose for local development/debugging
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./food-delivery-backend:/app # Mount for live-reloading in development
    command: ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] # For development
    # For production, use the CMD from Dockerfile or a gunicorn command:
    # command: ["gunicorn", "app.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]

  frontend:
    build:
      context: .
      dockerfile: food-delivery-frontend/Dockerfile
      args:
        VITE_API_BASE_URL: ${VITE_API_BASE_URL} # Pass API URL at build time
    container_name: food_delivery_frontend
    ports:
      - "3000:80" # Expose frontend on port 3000 for local access
    depends_on:
      - backend # Frontend needs backend to be available for API calls
    volumes:
      - ./food-delivery-frontend/nginx.conf:/etc/nginx/conf.d/default.conf:ro # Mount custom Nginx config
      # For development with hot-reloading, you'd typically run the React dev server outside Docker
      # or use a more complex setup. For production, the built assets are copied.

  nginx:
    image: nginx:stable-alpine
    container_name: food_delivery_nginx_proxy
    ports:
      - "80:80"   # HTTP traffic
      - "443:443" # HTTPS traffic
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./nginx/certbot/conf:/etc/nginx/ssl:ro # For SSL certificates
      - ./nginx/certbot/www:/var/www/certbot:ro # For Certbot challenges
    depends_on:
      - frontend
      - backend
    # Ensure Nginx starts after frontend and backend are ready
    healthcheck:
      test: ["CMD-SHELL", "nginx -t"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  pgdata:
nginx
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_buffers 16 8k;
    gzip_http_version 1.1;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Include all server blocks from conf.d
    include /etc/nginx/conf.d/*.conf;
}
nginx
server {
    listen 80;
    server_name your_domain.com www.your_domain.com; # Replace with your actual domain

    # Redirect HTTP to HTTPS
    location / {
        return 301 https://$host$request_uri;
    }

    # Certbot challenge for SSL certificate renewal
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
}

server {
    listen 443 ssl;
    server_name your_domain.com www.your_domain.com; # Replace with your actual domain

    ssl_certificate /etc/nginx/ssl/live/your_domain.com/fullchain.pem; # Path to your SSL certificate
    ssl_certificate_key /etc/nginx/ssl/live/your_domain.com/privkey.pem; # Path to your SSL key
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384';
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_stapling on;
    ssl_stapling_verify on;
    resolver 8.8.8.8 8.8.4.4 valid=300s;
    resolver_timeout 5s;

    # Frontend static files
    location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
        try_files $uri $uri/ /index.html; # For React Router
    }

    # Backend API proxy
    location /api/v1/ {
        proxy_pass http://backend:8000; # 'backend' is the service name in docker-compose
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    # Optional: Serve static assets from S3/CDN directly if configured
    # location /static/ {
    #     proxy_pass https://your-s3-bucket.s3.amazonaws.com/static/;
    #     proxy_set_header Host your-s3-bucket.s3.amazonaws.com;
    # }

    # Error pages
    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}
bash
    ssh user@your_server_ip
    ```
2.  **Update system packages:**
    ```bash
    sudo apt update && sudo apt upgrade -y
    ```
3.  **Install Docker:** Follow the official Docker installation guide for your OS.
    ```bash
    # Example for Ubuntu
    sudo apt install apt-transport-https ca-certificates curl software-properties-common -y
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt update
    sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y
    ```
4.  **Install Docker Compose (if not included with Docker Desktop):**
    ```bash
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.27.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    ```
5.  **Add your user to the `docker` group (optional, but convenient):**
    ```bash
    sudo usermod -aG docker $USER
    newgrp docker # Apply group changes immediately
    ```

### 4.3. Application Deployment

1.  **Clone your repository:**
    ```bash
    git clone https://github.com/your-repo/food-delivery-app.git
    cd food-delivery-app
    ```
2.  **Create `.env` file:** See Section 5 for details.
    ```bash
    touch .env
    # Populate with your environment variables
    ```
3.  **Create Nginx configuration directories and placeholder for Certbot:**
    ```bash
    mkdir -p nginx/conf.d nginx/certbot/conf nginx/certbot/www
    # Copy your default.conf and nginx.conf into these directories
    cp food-delivery-frontend/nginx.conf nginx/conf.d/default.conf # This is for the frontend service's Nginx
    # You will need to manually create the main nginx.conf and default.conf for the Nginx proxy service
    # based on the examples in section 3.
    ```
4.  **Generate initial SSL certificates (using Certbot with Nginx):**
    *   First, start Nginx without SSL to allow Certbot to verify domain ownership.
    *   Temporarily comment out the HTTPS server block in `nginx/conf.d/default.conf` or ensure only the HTTP block is active.
    *   Run `docker-compose up -d nginx`.
    *   Then, run Certbot:
        ```bash
        sudo docker run -it --rm \
            -v ./nginx/certbot/conf:/etc/letsencrypt \
            -v ./nginx/certbot/www:/var/www/certbot \
            certbot/certbot \
            certonly --webroot -w /var/www/certbot \
            --email your_email@example.com \
            -d your_domain.com -d www.your_domain.com \
            --agree-tos --no-eff-email
        ```
    *   Once certificates are obtained, uncomment/add the HTTPS server block in `nginx/conf.d/default.conf`.
5.  **Build and run the Docker Compose services:**
    ```bash
    docker-compose build --no-cache # Build images from scratch
    docker-compose up -d           # Run services in detached mode
    ```
6.  **Run database migrations:**
    ```bash
    docker-compose exec backend alembic upgrade head
    ```
7.  **Verify deployment:**
    ```bash
    docker-compose ps # Check container status
    curl http://localhost # Or your domain
    curl http://localhost/api/v1/health # Check backend health endpoint
    ```

### 4.4. Updates and Rollbacks

*   **To update:**
    1.  Pull latest code: `git pull origin main`
    2.  Rebuild images: `docker-compose build`
    3.  Apply migrations (if any): `docker-compose exec backend alembic upgrade head`
    4.  Restart services: `docker-compose up -d`
*   **To rollback:**
    *   If an update causes issues, you can revert to a previous Git commit, rebuild, and restart.
    *   For database rollbacks, use `alembic downgrade -1` (or to a specific revision), but be cautious as this can lead to data loss.

## 5. Environment Variable Management

Proper environment variable management is critical for security and configuration flexibility.

### 5.1. Local Development (`.env` file)

For local development, a `.env` file at the root of your project will store non-sensitive variables. This file should **NEVER** be committed to version control.

**Example `.env`:**

``````

### 5.2. Production Environment

In production, environment variables should be managed using secure, cloud-native secret management services.

*   **AWS:** AWS Secrets Manager or AWS Systems Manager Parameter Store.
*   **Google Cloud:** Google Secret Manager.
*   **Azure:** Azure Key Vault.
*   **Kubernetes:** Kubernetes Secrets (though these need additional encryption at rest).

**Best Practices:**

*   **Never commit secrets to Git.**
*   **Use strong, randomly generated passwords and API keys.**
*   **Rotate secrets regularly.**
*   **Grant least privilege access** to secrets.
*   **Encrypt secrets at rest and in transit.**

## 6. Database Migration and Backup Process

### 6.1. Database Migration (Alembic)

Alembic is used for managing database schema changes in a controlled and versioned manner.

**Workflow:**

1.  **Develop:** Make changes to your SQLAlchemy models (`app/models/`).
2.  **Generate Migration:** From the `food-delivery-backend` directory, run:
    ```dotenv
# Database Configuration
POSTGRES_DB=food_delivery_db
POSTGRES_USER=food_delivery_user
POSTGRES_PASSWORD=your_strong_db_password

# FastAPI Backend Configuration
SECRET_KEY=supersecretkeythatshouldbechangedinproduction
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Frontend Configuration
VITE_API_BASE_URL=https://your_domain.com/api/v1 # Or http://localhost:8000/api/v1 for local backend

# External Service API Keys (Example)
STRIPE_SECRET_KEY=sk_test_xxxxxxxxxxxxxxxxxxxx
GOOGLE_MAPS_API_KEY=AIzaSyBxxxxxxxxxxxxxxxxxxxx
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1501712266
bash
    docker-compose exec backend alembic revision --autogenerate -m "Descriptive message for changes"
    ```
    This creates a new migration script in `alembic/versions/`.
3.  **Review:** **Crucially, review the generated migration script.** Alembic's autogenerate isn't perfect; manually adjust `upgrade()` and `downgrade()` functions if needed.
4.  **Apply Migration:** To apply the migration to your database:
    ```bash
    docker-compose exec backend alembic upgrade head
    ```
    This command applies all pending migrations up to the latest revision.
5.  **Downgrade (if needed):** To revert the last migration:
    ```bash
    docker-compose exec backend alembic downgrade -1
    ```
    Or to a specific revision:
    ```bash
    docker-compose exec backend alembic downgrade <revision_id>
    ```

### 6.2. Database Backup Process (PostgreSQL)

Regular and reliable database backups are essential for disaster recovery.

**Methods:**

1.  **`pg_dump` (Logical Backup):**
    *   Creates a text file with SQL commands to reconstruct the database.
    *   Can be used to restore to different PostgreSQL versions or even other database systems (with modifications).
    *   **Command Example (from host):**
        ```bash
        docker-compose exec db pg_dump -U ${POSTGRES_USER} -d ${POSTGRES_DB} > /path/to/backups/food_delivery_db_$(date +%Y%m%d%H%M%S).sql
        ```
    *   **Command Example (from inside `db` container):**
        ```bash
        pg_dump -U ${POSTGRES_USER} -d ${POSTGRES_DB} > /var/lib/postgresql/data/backups/food_delivery_db_$(date +%Y%m%d%H%M%S).sql
        ```
        (Ensure `/var/lib/postgresql/data/backups` is a mounted volume for persistence)
2.  **Volume Backups (Snapshot):**
    *   If using cloud providers (AWS EBS, GCP Persistent Disk), you can take snapshots of the database volume. This is a block-level backup.
    *   Requires stopping the database or ensuring quiescence for consistency.

**Backup Strategy:**

*   **Frequency:** Daily full backups, with more frequent (e.g., hourly) incremental backups or transaction log archiving for Point-in-Time Recovery (PITR).
*   **Retention:** Keep backups for a defined period (e.g., 7 days daily, 4 weeks weekly, 12 months monthly).
*   **Storage:** Store backups in a separate, geographically redundant location (e.g., S3 bucket in a different region).
*   **Encryption:** All backups must be encrypted at rest.
*   **Testing:** Periodically test backup restoration to ensure data integrity and validate your recovery procedures.

**Automated Backups (Example with Cron and S3):**

1.  **Create a backup script** (e.g., `backup.sh`):
    ```bash
    #!/bin/bash
    set -e

    BACKUP_DIR="/tmp/db_backups"
    TIMESTAMP=$(date +%Y%m%d%H%M%S)
    BACKUP_FILE="${BACKUP_DIR}/food_delivery_db_${TIMESTAMP}.sql.gz"
    S3_BUCKET="s3://your-food-delivery-backups" # Replace with your S3 bucket

    mkdir -p ${BACKUP_DIR}

    echo "Starting PostgreSQL backup..."
    docker-compose exec db pg_dump -U ${POSTGRES_USER} -d ${POSTGRES_DB} | gzip > ${BACKUP_FILE}
    echo "Backup created: ${BACKUP_FILE}"

    echo "Uploading backup to S3..."
    aws s3 cp ${BACKUP_FILE} ${S3_BUCKET}/
    echo "Backup uploaded to S3."

    echo "Cleaning up local backup files..."
    rm -rf ${BACKUP_DIR}
    echo "Cleanup complete."
    ```
2.  **Make the script executable:** `chmod +x backup.sh`
3.  **Schedule with Cron:** Add an entry to your crontab (`crontab -e`) to run the script daily.
    ```cron
    0 2 * * * /path/to/your/food-delivery-app/backup.sh >> /var/log/food_delivery_backup.log 2>&1
    ```
    (This runs the backup script at 2 AM daily).
    *   Ensure `aws-cli` is installed and configured on your server for S3 uploads.

## 7. Monitoring and Logging

Robust monitoring and logging are crucial for understanding system health, identifying issues, and ensuring reliability.

### 7.1. Logging

*   **Centralized Logging:** All application logs (FastAPI, Nginx, PostgreSQL) should be collected and sent to a centralized logging system.
    *   **Options:** ELK Stack (Elasticsearch, Logstash, Kibana), Grafana Loki, cloud-native services (AWS CloudWatch Logs, Google Cloud Logging).
*   **Structured Logging:** Use structured logging (e.g., JSON format) for easier parsing and analysis. FastAPI can be configured to use `python-json-logger`.
*   **Log Levels:** Use appropriate log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL) to filter noise.
*   **Contextual Logging:** Include relevant context in logs (e.g., `request_id`, `user_id`, `order_id`) to trace requests across services.

**Example FastAPI Logging (using `logging.basicConfig` or `loguru`):**

``````

### 7.2. Monitoring

*   **Metrics Collection:** Collect key performance metrics from all services.
    *   **Backend (FastAPI):** CPU usage, memory usage, request latency, error rates, number of active requests, database query times.
    *   **Frontend (Nginx):** Request rates, error rates, bandwidth usage.
    *   **Database (PostgreSQL):** Connection count, active queries, disk I/O, cache hit ratio, replication lag.
    *   **System:** CPU, memory, disk, network I/O of the host server.
*   **Tools:**
    *   **Prometheus:** For time-series data collection.
    *   **Grafana:** For creating dashboards and visualizing metrics.
    *   **Cloud-native services:** AWS CloudWatch, Google Cloud Monitoring.
*   **Health Checks:**
    *   Implement `/health` and `/ready` endpoints in your FastAPI application.
    *   `/health`: A lightweight check to confirm the service is running.
    *   `/ready`: A more comprehensive check that verifies dependencies (database, external APIs) are reachable.
    *   Docker Compose health checks (as shown in `docker-compose.yml`) leverage these.

**Example FastAPI Health Check:**

``````

### 7.3. Alerting

*   Configure alerts for critical issues based on your monitoring metrics and logs.
*   **Examples:**
    *   High error rates (e.g., 5xx errors > 5% for 5 minutes).
    *   Service downtime.
    *   High latency for critical API endpoints.
    *   Low disk space.
    *   Failed database backups.
    *   Security incidents (e.g., multiple failed login attempts).
*   **Notification Channels:** PagerDuty, Slack, Email, SMS.

## 8. CI/CD Recommendation

Continuous Integration (CI) and Continuous Deployment (CD) automate the software delivery process, ensuring faster, more reliable releases.

**Recommended Tools:** GitHub Actions (for GitHub repositories), GitLab CI/CD, Jenkins, CircleCI.

**CI/CD Pipeline Stages:**

1.  **Source Code Checkout:** Get the latest code from the repository.
2.  **Environment Setup:** Install necessary tools (Python, Node.js, Docker).
3.  **Linting & Static Analysis:**
    *   **Backend (Python):** `flake8`, `black`, `isort`, `mypy`.
    *   **Frontend (React):** `ESLint`, `Prettier`.
4.  **Testing:**
    *   **Unit Tests:** Run `pytest` for backend, `jest` for frontend.
    *   **Integration Tests:** Run `pytest` for backend API interactions, `jest`/`React Testing Library` for frontend component interactions.
    *   **Code Coverage:** Generate coverage reports (`pytest-cov`, `jest --coverage`).
5.  **Build Docker Images:**
    *   Build `backend` and `frontend` Docker images using their respective Dockerfiles.
    *   Tag images with commit SHA or version number.
    *   Perform vulnerability scanning on images (e.g., Trivy, Snyk).
6.  **Push to Container Registry:** Push built Docker images to a container registry (e.g., Docker Hub, AWS ECR, Google Container Registry).
7.  **Database Migrations (CI/CD specific):**
    *   For production, migrations should be applied carefully.
    *   Option 1: Run `alembic upgrade head` as a separate step before deploying the new application version.
    *   Option 2: Embed migration logic into the application startup (less recommended for complex migrations).
8.  **Deployment (CD):**
    *   **Staging Environment:** Deploy to a staging environment for final testing and validation.
    *   **Production Environment:**
        *   **Rolling Updates:** Deploy new container versions with zero downtime (e.g., using Kubernetes deployments or `docker-compose up -d --no-deps --scale service=N`).
        *   **Blue/Green Deployment:** Deploy new version alongside old, then switch traffic.
        *   **Canary Deployment:** Gradually roll out new version to a small subset of users.
    *   **Update Nginx configuration** (if necessary, e.g., for new services).
    *   **Health Checks:** Verify new deployment is healthy before fully routing traffic.
9.  **Post-Deployment Actions:**
    *   Run smoke tests.
    *   Notify stakeholders.
    *   Update monitoring dashboards.

**Example GitHub Actions Workflow (Conceptual):**

``````

## 9. Production Readiness Checklist

This checklist ensures your Food Delivery App is ready for a production environment, covering key aspects of reliability, security, performance, and maintainability.

### 9.1. Security

*   [ ] All sensitive data (passwords, API keys, payment info) is encrypted at rest and in transit.
*   [ ] User passwords are hashed using strong algorithms (bcrypt/argon2).
*   [ ] JWT `SECRET_KEY` is a strong, randomly generated string, stored securely, and rotated regularly.
*   [ ] Role-Based Access Control (RBAC) is enforced at the API level.
*   [ ] Input validation is implemented on all API endpoints to prevent injection attacks (SQL, XSS).
*   [ ] Rate limiting is configured on critical endpoints (login, registration, order placement).
*   [ ] CORS policies are strictly configured to allow only trusted origins.
*   [ ] Nginx is configured with HTTPS/TLS 1.2+ and strong cipher suites.
*   [ ] SSL certificates are valid and auto-renewing (e.g., Certbot).
*   [ ] Payment processing is handled by a PCI DSS compliant gateway (e.g., Stripe), avoiding direct storage of sensitive card data.
*   [ ] Secrets are managed using a dedicated secret management service (e.g., AWS Secrets Manager, GCP Secret Manager).
*   [ ] Regular security audits and penetration testing are planned.
*   [ ] Docker images are scanned for vulnerabilities.

### 9.2. Performance & Scalability

*   [ ] Backend services are stateless to enable horizontal scaling.
*   [ ] Database (PostgreSQL) has appropriate indexes for frequently queried columns.
*   [ ] Database connection pooling (e.g., PgBouncer) is configured.
*   [ ] Caching (Redis) is implemented for frequently accessed, non-volatile data.
*   [ ] Asynchronous tasks (notifications, reports) are offloaded to worker services via a message queue.
*   [ ] Static assets (frontend bundles, images) are served via a CDN.
*   [ ] Nginx is configured for Gzip compression.
*   [ ] Load balancing is in place to distribute traffic across multiple backend instances.
*   [ ] Database is configured for replication (read replicas) if read-heavy.
*   [ ] Application code is optimized for performance (e.g., efficient queries, minimal I/O).

### 9.3. Reliability & Availability

*   [ ] All services have robust health check endpoints (`/health`, `/ready`).
*   [ ] Automated database backups are configured, tested, and stored off-site.
*   [ ] A disaster recovery plan is documented and periodically tested.
*   [ ] Critical components are deployed across multiple availability zones/regions.
*   [ ] Error handling is robust and provides meaningful feedback without exposing sensitive information.
*   [ ] Automated rollbacks are possible in the CI/CD pipeline.
*   [ ] Resource limits (CPU, memory) are set for Docker containers.

### 9.4. Observability

*   [ ] Centralized logging system (ELK, Loki, CloudWatch) is configured for all application and infrastructure logs.
*   [ ] Structured logging is implemented for easier analysis.
*   [ ] Comprehensive monitoring dashboards (Grafana, CloudWatch) are set up for key metrics.
*   [ ] Alerting is configured for critical issues (e.g., high error rates, service downtime, resource exhaustion).
*   [ ] Distributed tracing (if using microservices) is considered for complex request flows.

### 9.5. Deployment & Operations

*   [ ] CI/CD pipelines are fully automated for building, testing, and deploying.
*   [ ] Database schema migrations are managed with Alembic and integrated into CI/CD.
*   [ ] Environment variables are correctly configured for production.
*   [ ] Runbooks are created for common operational tasks and incident response.
*   [ ] Access to production environments is restricted and audited.
*   [ ] Container images are optimized for size and built with multi-stage Dockerfiles.
*   [ ] Docker Compose (or orchestration tool) is configured for production (e.g., Gunicorn for FastAPI, Nginx for static files).

### 9.6. Cost Management

*   [ ] Cloud resource usage is regularly monitored.
*   [ ] Instances are right-sized to avoid over-provisioning.
*   [ ] Cost-effective storage solutions are used (e.g., S3 for backups).
*   [ ] Auto-scaling policies are configured to match demand.

This comprehensive guide should provide a solid foundation for deploying and operating your Food Delivery App reliably in production.
```python
# app/main.py (simplified example)
import logging
from fastapi import FastAPI, Request

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(...)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Outgoing response: {request.method} {request.url} - Status: {response.status_code}")
    return response

# For structured logging, you'd integrate a library like python-json-logger
# or configure uvicorn's logging.
python
# app/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db # Assuming get_db provides a session

app = FastAPI(...)

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "ok"}

@app.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check(db: Session = Depends(get_db)):
    try:
        # Attempt a simple database query to check connectivity
        db.execute("SELECT 1")
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {e}"
        )
yaml
# .github/workflows/deploy.yml
name: CI/CD Food Delivery App

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install Backend Dependencies
        run: pip install -r food-delivery-backend/requirements.txt

      - name: Run Backend Linting & Tests
        run: |
          cd food-delivery-backend
          flake8 .
          pytest --cov=app --cov-report=xml # Generate coverage report
          cd ..

      - name: Install Frontend Dependencies
        run: |
          cd food-delivery-frontend
          npm install
          cd ..

      - name: Run Frontend Linting & Tests
        run: |
          cd food-delivery-frontend
          npm run lint
          npm test -- --coverage # Run tests and generate coverage
          cd ..

      - name: Build Docker Images
        run: |
          docker build -t your_docker_repo/food-delivery-backend:latest -f food-delivery-backend/Dockerfile .
          docker build -t your_docker_repo/food-delivery-frontend:latest -f food-delivery-frontend/Dockerfile --build-arg VITE_API_BASE_URL=${{ secrets.VITE_API_BASE_URL }} .

      - name: Log in to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Push Docker Images
        run: |
          docker push your_docker_repo/food-delivery-backend:latest
          docker push your_docker_repo/food-delivery-frontend:latest

  deploy:
    needs: build-and-test
    runs-on: self-hosted # Or use a cloud-specific deployment action
    environment: production # Define a production environment in GitHub
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Pull latest Docker images
        run: |
          docker pull your_docker_repo/food-delivery-backend:latest
          docker pull your_docker_repo/food-delivery-frontend:latest

      - name: Log in to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Deploy with Docker Compose
        run: |
          # Ensure .env is present on the self-hosted runner or passed securely
          # For production, use a more robust command, e.g., for Gunicorn
          docker-compose -f docker-compose.yml up -d --remove-orphans
          docker-compose exec backend alembic upgrade head # Run migrations
